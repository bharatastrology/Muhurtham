"""Check the app's MC (KP 10th cusp), disc-centre sunrise, Sankranti times and
void-of-course Moon against pyswisseph. App values were captured in the browser
(see app_rules_output.json). Usage: python compare_rules.py app_rules_output.json"""
import json
import sys

import swisseph as swe

CASES = [["Chennai", 1950, 3, 15, 6, 30, 5.5, 13.0827, 80.2707], ["Delhi", 1975, 7, 4, 14, 0, 5.5, 28.6139, 77.2090],
         ["Trivandrum", 1992, 8, 15, 9, 30, 5.5, 8.5241, 76.9366], ["London", 2000, 1, 1, 12, 0, 0, 51.5074, -0.1278],
         ["Mumbai", 2010, 11, 5, 18, 45, 5.5, 19.0760, 72.8777], ["NewYork", 2024, 4, 8, 10, 0, -4, 40.7128, -74.0060],
         ["Kochi", 2026, 10, 29, 8, 55, 5.5, 9.9312, 76.2673], ["Sydney", 2035, 12, 21, 23, 30, 11, -33.8688, 151.2093],
         ["Bengaluru", 2050, 6, 21, 5, 0, 5.5, 12.9716, 77.5946]]


def angdiff(a, b):
    d = (a - b) % 360
    return d - 360 if d > 180 else d


def main(path):
    app = json.load(open(path, encoding="utf-8"))
    app["voc"] = [(app["vocStart"] + k * app["vocStep"], bool(f)) for k, f in enumerate(app["vocFlags"])]
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    sid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    print("MC / KP 10th cusp (app - swe, degrees)")
    for i, (name, y, m, d, h, mn, tz, lat, lon) in enumerate(CASES):
        jd = swe.julday(y, m, d, h + mn / 60 - tz)
        mc = (swe.houses(jd, lat, lon, b"P")[1][1] - swe.get_ayanamsa_ut(jd)) % 360
        print(f"  {name:<11} swe-mode {angdiff(app['mc']['SWISSEPH_ONLY'][i], mc):+.5f}"
              f"  internal {angdiff(app['mc']['INTERNAL_ONLY'][i], mc):+.5f}")

    print("\nDisc-centre, no-refraction sunrise/sunset (app - swe, minutes)")
    flags = swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION
    for i, (name, y, m, d, h, mn, tz, lat, lon) in enumerate(CASES):
        jd0 = swe.julday(y, m, d, -tz)
        rise = (swe.rise_trans(jd0, swe.SUN, swe.CALC_RISE | flags, (lon, lat, 0))[1][0] - jd0) * 24
        sset = (swe.rise_trans(jd0, swe.SUN, swe.CALC_SET | flags, (lon, lat, 0))[1][0] - jd0) * 24
        ar, aset = app["riseCentre"][i]
        print(f"  {name:<11} rise {(ar - rise) * 60:+.1f}  set {(aset - sset) * 60:+.1f}")

    print("\nSankranti (sidereal sign ingress) time error (app - swe, minutes)")
    worst = {"swe": 0, "internal": 0}
    for k, jd in enumerate(app["sankDates"]):
        lon_now = swe.calc_ut(jd, swe.SUN, sid)[0][0]
        target = (lon_now // 30) * 30
        ref = swe.solcross_ut(target, jd - 35, sid)
        for mode, arr in (("swe", app["sank"][0]), ("internal", app["sank"][1])):
            err = (arr[k] - ref) * 1440
            worst[mode] = max(worst[mode], abs(err))
    print(f"  max |error| over {len(app['sankDates'])} ingresses: swe-mode {worst['swe']:.2f} min, internal {worst['internal']:.1f} min")

    print("\nVoid-of-course Moon (tropical), 80 samples every 3 h")
    aspects = [0, 60, 90, 120, 180, 240, 270, 300]
    bodies = [swe.SUN, swe.MERCURY, swe.VENUS, swe.MARS, swe.JUPITER, swe.SATURN]
    mismatches = []
    for jd, app_voc in app["voc"]:
        moon0 = swe.calc_ut(jd, swe.MOON)[0][0]
        sign_end = (moon0 // 30 + 1) * 30 % 360
        t_exit = swe.mooncross_ut(sign_end, jd)
        step = 1 / 288  # 5 minutes
        voc = True
        prev = {b: (moon0 - swe.calc_ut(jd, b)[0][0]) % 360 for b in bodies}
        t = jd
        while t < t_exit and voc:
            t = min(t + step, t_exit)
            m = swe.calc_ut(t, swe.MOON)[0][0]
            for b in bodies:
                s = (m - swe.calc_ut(t, b)[0][0]) % 360
                for a in aspects:
                    lo, hi = prev[b], s if s >= prev[b] else s + 360
                    aa = a if a >= lo else a + 360
                    if lo <= aa <= hi:
                        voc = False
                prev[b] = s
        if voc != app_voc:
            mismatches.append((jd, app_voc, voc))
    print(f"  agreement {len(app['voc']) - len(mismatches)}/{len(app['voc'])}; mismatches: {mismatches}")


if __name__ == "__main__":
    main(sys.argv[1])
