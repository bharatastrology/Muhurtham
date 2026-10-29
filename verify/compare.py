"""Compare the app's ephemeris output (SwissEph mode and internal fallback)
against pyswisseph reference values. Usage: python compare.py app_output.json"""
import json
import sys

import swisseph as swe

BODIES = {
    "sun": swe.SUN, "moon": swe.MOON, "mercury": swe.MERCURY, "venus": swe.VENUS,
    "mars": swe.MARS, "jupiter": swe.JUPITER, "saturn": swe.SATURN, "rahu": swe.MEAN_NODE,
}
NAK = 360 / 27


def angdiff(a, b):
    d = (a - b) % 360
    return d - 360 if d > 180 else d


def reference(case):
    _, y, m, d, h, mn, tz, lat, lon = case
    jd = swe.julday(y, m, d, h + mn / 60 - tz)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    p = {k: swe.calc_ut(jd, b, flags)[0][0] for k, b in BODIES.items()}
    p["ketu"] = (p["rahu"] + 180) % 360
    ay = swe.get_ayanamsa_ut(jd)
    asc = (swe.houses(jd, lat, lon, b"W")[1][0] - ay) % 360
    return {"jd": jd, "ay": ay, "asc": asc, "p": p}


def sunrise_local(case):
    """Conventional sunrise/sunset (upper limb, standard refraction) for the case's local date."""
    _, y, m, d, _, _, tz, lat, lon = case
    jd0 = swe.julday(y, m, d, 0 - tz)
    res, t = swe.rise_trans(jd0, swe.SUN, swe.CALC_RISE, (lon, lat, 0))
    rise = t[0]
    res, t = swe.rise_trans(jd0, swe.SUN, swe.CALC_SET, (lon, lat, 0))
    sset = t[0]
    to_local = lambda j: ((j - jd0) * 24) % 24
    return to_local(rise), to_local(sset)


def panchanga(sun, moon):
    elong = (moon - sun) % 360
    return {
        "tithi": int(elong // 12) + 1,
        "nak": int(moon // NAK),
        "pada": int((moon % NAK) // (NAK / 4)) + 1,
        "yoga": int(((sun + moon) % 360) // NAK),
        "karana": int(elong // 6),
        "lagna": None,
    }


def main(path):
    data = json.load(open(path, encoding="utf-8"))
    rows = []
    for i, case in enumerate(data["cases"]):
        ref = reference(case)
        rise, sset = sunrise_local(case)
        for mode in ("swe", "internal"):
            app = data[mode][i]
            row = {"case": case[0], "mode": mode, "jd": app["jd"] - ref["jd"],
                   "ay": app["ay"] - ref["ay"], "asc": angdiff(app["asc"], ref["asc"])}
            for k in ref["p"]:
                row[k] = angdiff(app["p"][k], ref["p"][k])
            pr = panchanga(ref["p"]["sun"], ref["p"]["moon"])
            pa = panchanga(app["p"]["sun"], app["p"]["moon"])
            row["mismatch"] = [k for k in ("tithi", "nak", "pada", "yoga", "karana") if pr[k] != pa[k]]
            if int(app["asc"] // 30) != int(ref["asc"] // 30):
                row["mismatch"].append("lagna")
            row["sunrise"] = rise
            row["sunset"] = sset
            row["app_rise"] = app.get("rise", 6.25)
            row["app_set"] = app.get("set", 18.25)
            rows.append(row)

    cols = ["ay", "asc", "sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "rahu"]
    print("Differences app - pyswisseph (degrees)")
    print(f"{'case':<11}{'mode':<9}" + "".join(f"{c:>9}" for c in cols) + "  mismatches")
    for r in rows:
        print(f"{r['case']:<11}{r['mode']:<9}" + "".join(f"{r[c]:>9.4f}" for c in cols)
              + "  " + (",".join(r["mismatch"]) or "-"))
    print()
    for mode in ("swe", "internal"):
        sel = [r for r in rows if r["mode"] == mode]
        print(f"max |diff| {mode}: " + ", ".join(f"{c}={max(abs(r[c]) for r in sel):.4f}" for c in cols))
    print()
    print("Sunrise / sunset (local hours): pyswisseph vs app (06:15 / 18:15 if the app has no sunrise calc)")
    for r in rows[::2]:
        print(f"  {r['case']:<11} rise {r['sunrise']:.3f}h app {r['app_rise']:.3f}h ({(r['app_rise'] - r['sunrise']) * 60:+.1f} min)"
              f"   set {r['sunset']:.3f}h app {r['app_set']:.3f}h ({(r['app_set'] - r['sunset']) * 60:+.1f} min)")
    json.dump(rows, open(path.replace(".json", "_compare.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
