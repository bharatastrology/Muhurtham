"""Check the app's tithi / yoga / karana indices and veto detection against pyswisseph.
App rows (Trivandrum, IST, Nov 2026 - Jan 2027 search with vetoes omitted):
[y, m, d, hour, minute, tithiIdx, yogaIdx, karanaIdx, vetoes]"""
import swisseph as swe

APP = [[2026,11,26,9,1,16,21,33,""],[2026,11,16,9,20,6,10,12,""],[2026,11,21,9,1,11,15,22,""],[2026,11,21,8,55,11,15,22,""],[2026,11,19,8,55,9,13,18,""],[2027,1,24,14,50,17,3,34,""],[2026,11,25,9,20,15,19,31,""],[2026,11,25,14,50,15,20,31,""],[2027,1,27,14,50,20,6,40,"Chandrashtama"],[2026,11,22,8,55,12,16,24,"Vyatipata yoga"],[2026,11,22,9,1,12,16,24,"Vyatipata yoga"],[2026,11,14,16,20,4,8,9,""],[2026,11,22,9,20,12,16,24,"Vyatipata yoga"],[2026,11,18,14,50,8,12,16,""],[2026,12,5,12,15,26,4,52,""],[2026,11,18,9,20,8,12,16,""],[2026,12,3,9,1,24,1,48,"Chandrashtama"],[2026,12,3,8,55,24,1,48,"Chandrashtama"],[2027,1,28,12,15,21,7,42,"Vishti (Bhadra) karana"],[2027,1,30,8,55,23,9,46,""],[2027,1,30,9,1,23,9,46,""],[2026,11,27,9,20,17,22,35,"Vishti (Bhadra) karana"],[2026,11,13,9,20,3,7,7,"Vishti (Bhadra) karana"],[2027,1,30,12,15,23,9,46,""],[2026,12,1,9,1,22,26,44,"Vaidhriti yoga"],[2026,12,1,8,55,22,26,44,"Vaidhriti yoga"]]

swe.set_sid_mode(swe.SIDM_LAHIRI)
flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
bad = 0
for y, m, d, h, mn, ti, yi, ki, veto in APP:
    jd = swe.julday(y, m, d, h + mn / 60 - 5.5)
    sun = swe.calc_ut(jd, swe.SUN, flags)[0][0]
    moon = swe.calc_ut(jd, swe.MOON, flags)[0][0]
    elong = (moon - sun) % 360
    ref = (int(elong // 12), int(((sun + moon) % 360) // (360 / 27)), int(elong // 6))
    k = ref[2]
    is_vishti = 1 <= k <= 56 and (k - 1) % 7 == 6
    veto_ok = (("Vishti" in veto) == is_vishti and ("Vyatipata" in veto) == (ref[1] == 16)
               and ("Vaidhriti" in veto) == (ref[1] == 26) and ("Amavasya" in veto) == (ref[0] == 29))
    if ref != (ti, yi, ki) or not veto_ok:
        bad += 1
        print("MISMATCH", y, m, d, h, mn, "app", (ti, yi, ki), veto, "swe", ref)
print(f"{len(APP) - bad}/{len(APP)} slots: tithi, yoga, karana and Panchanga vetoes match pyswisseph")
