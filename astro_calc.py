"""
Vedic Astrology Calculation Engine
Pure Python implementation using astronomical algorithms.
"""
import math
from datetime import datetime, timedelta

# ─── Constants ───────────────────────────────────────────────────────────────
RASHI_NAMES = [
    "Aries (Mesh)", "Taurus (Vrishabh)", "Gemini (Mithun)", "Cancer (Kark)",
    "Leo (Simha)", "Virgo (Kanya)", "Libra (Tula)", "Scorpio (Vrishchik)",
    "Sagittarius (Dhanu)", "Capricorn (Makar)", "Aquarius (Kumbh)", "Pisces (Meen)"
]
RASHI_SHORT = ["Ari","Tau","Gem","Can","Leo","Vir","Lib","Sco","Sag","Cap","Aqu","Pis"]
RASHI_LORDS = ["Mars","Venus","Mercury","Moon","Sun","Mercury","Venus","Mars","Jupiter","Saturn","Saturn","Jupiter"]

NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu",
    "Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta",
    "Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha",
    "Uttara Ashadha","Shravana","Dhanishtha","Shatabhisha","Purva Bhadrapada",
    "Uttara Bhadrapada","Revati"
]
NAKSHATRA_LORDS = [
    "Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury",
    "Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury",
    "Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"
]
DASHA_YEARS = {
    "Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,
    "Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17
}
DASHA_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]

PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]

# ─── Julian Day ───────────────────────────────────────────────────────────────
def julian_day(year, month, day, hour=0.0):
    """Calculate Julian Day Number."""
    if month <= 2:
        year -= 1
        month += 12
    A = int(year / 100)
    B = 2 - A + int(A / 4)
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + hour/24.0 + B - 1524.5
    return jd

def jd_to_datetime(jd):
    jd = jd + 0.5
    Z = int(jd)
    F = jd - Z
    if Z < 2299161:
        A = Z
    else:
        alpha = int((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - int(alpha / 4)
    B = A + 1524
    C = int((B - 122.1) / 365.25)
    D = int(365.25 * C)
    E = int((B - D) / 30.6001)
    day = B - D - int(30.6001 * E)
    month = E - 1 if E < 14 else E - 13
    year = C - 4716 if month > 2 else C - 4715
    hour = F * 24
    return year, month, day, hour

# ─── Ayanamsha (Lahiri) ────────────────────────────────────────────────────
def ayanamsha_lahiri(jd):
    """Lahiri ayanamsha."""
    T = (jd - 2451545.0) / 36525.0
    return 23.85 + 0.0136 * (T + 100)  # simplified

# ─── Sun longitude ────────────────────────────────────────────────────────────
def sun_longitude(jd):
    T = (jd - 2451545.0) / 36525.0
    L0 = 280.46646 + 36000.76983 * T
    M = math.radians(357.52911 + 35999.05029 * T - 0.0001537 * T*T)
    C = (1.914602 - 0.004817*T - 0.000014*T*T) * math.sin(M)
    C += (0.019993 - 0.000101*T) * math.sin(2*M)
    C += 0.000289 * math.sin(3*M)
    sun_lon = (L0 + C) % 360
    return sun_lon

# ─── Moon longitude ───────────────────────────────────────────────────────────
def moon_longitude(jd):
    T = (jd - 2451545.0) / 36525.0
    L1 = 218.3165 + 481267.8813 * T
    M  = math.radians(357.5291 + 35999.0503 * T)
    Mp = math.radians(134.9634 + 477198.8676 * T)
    D  = math.radians(297.8502 + 445267.1115 * T)
    F  = math.radians(93.2721 + 483202.0175 * T)
    lon = L1
    lon += 6.2888 * math.sin(Mp)
    lon += 1.2740 * math.sin(2*D - Mp)
    lon += 0.6583 * math.sin(2*D)
    lon += 0.2136 * math.sin(2*Mp)
    lon -= 0.1851 * math.sin(M)
    lon -= 0.1143 * math.sin(2*F)
    lon += 0.0588 * math.sin(2*D - 2*Mp)
    lon += 0.0572 * math.sin(2*D - M - Mp)
    lon += 0.0533 * math.sin(2*D + Mp)
    return lon % 360

# ─── Planetary longitudes (simplified VSOP87) ────────────────────────────────
def planet_longitude(jd, planet):
    T = (jd - 2451545.0) / 36525.0
    if planet == "Sun":
        return sun_longitude(jd)
    elif planet == "Moon":
        return moon_longitude(jd)
    elif planet == "Mars":
        L = 355.433 + 19141.6964 * T
        M = math.radians(19.387 + 19141.6964 * T)
        L += 10.691 * math.sin(M) + 0.623 * math.sin(2*M)
        return L % 360
    elif planet == "Mercury":
        L = 252.251 + 149474.0722 * T
        M = math.radians(168.641 + 149474.0722 * T)
        L += 23.440 * math.sin(M) + 2.996 * math.sin(2*M) + 0.636 * math.sin(3*M)
        return L % 360
    elif planet == "Jupiter":
        L = 34.351 + 3036.0303 * T
        M = math.radians(20.020 + 3036.0303 * T)
        L += 5.555 * math.sin(M) + 0.168 * math.sin(2*M)
        return L % 360
    elif planet == "Venus":
        L = 181.980 + 58519.2130 * T
        M = math.radians(212.448 + 58519.2130 * T)
        L += 0.7758 * math.sin(M) + 0.0033 * math.sin(2*M)
        return L % 360
    elif planet == "Saturn":
        L = 50.077 + 1223.5110 * T
        M = math.radians(317.021 + 1223.5110 * T)
        L += 6.406 * math.sin(M) + 0.317 * math.sin(2*M)
        return L % 360
    elif planet == "Rahu":
        # Mean Rahu (North Node)
        N = 125.0445 - 1934.1363 * T
        return N % 360
    elif planet == "Ketu":
        N = 125.0445 - 1934.1363 * T
        return (N + 180) % 360
    return 0.0

# ─── Ascendant ────────────────────────────────────────────────────────────────
def ascendant(jd, lat, lon):
    """Calculate Lagna (Ascendant) in tropical degrees."""
    T = (jd - 2451545.0) / 36525.0
    # GMST
    gmst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * T*T
    gmst = gmst % 360
    lst = (gmst + lon) % 360  # Local Sidereal Time in degrees
    # Obliquity
    eps = math.radians(23.439291 - 0.013004 * T)
    lst_rad = math.radians(lst)
    lat_rad = math.radians(lat)
    # Ascendant formula
    y = -math.cos(lst_rad)
    x = math.sin(eps) * math.tan(lat_rad) + math.cos(eps) * math.sin(lst_rad)
    asc = math.degrees(math.atan2(y, x)) % 360
    return asc

# ─── Convert to Sidereal (Vedic) ─────────────────────────────────────────────
def to_sidereal(tropical_lon, jd):
    ayn = ayanamsha_lahiri(jd)
    return (tropical_lon - ayn) % 360

# ─── Rashi & Degree ───────────────────────────────────────────────────────────
def get_rashi(lon):
    return int(lon / 30) % 12

def get_degree_in_rashi(lon):
    return lon % 30

def get_nakshatra(lon):
    idx = int(lon / (360/27)) % 27
    pada = int((lon % (360/27)) / (360/108)) + 1
    return NAKSHATRAS[idx], idx, pada

# ─── Houses ───────────────────────────────────────────────────────────────────
def calculate_houses(lagna_lon):
    """Whole-sign house system for Vedic astrology."""
    lagna_rashi = get_rashi(lagna_lon)
    houses = []
    for i in range(12):
        houses.append((lagna_rashi + i) % 12)
    return houses

# ─── Vimshottari Dasha ────────────────────────────────────────────────────────
def vimshottari_dasha(moon_lon_sid, birth_date):
    nak_name, nak_idx, pada = get_nakshatra(moon_lon_sid)
    dasha_lord = NAKSHATRA_LORDS[nak_idx]
    # Balance of dasha
    nak_start = nak_idx * (360/27)
    nak_end = (nak_idx + 1) * (360/27)
    traversed = (moon_lon_sid - nak_start) / (360/27)
    balance_fraction = 1 - traversed
    total_years = DASHA_YEARS[dasha_lord]
    balance_years = balance_fraction * total_years

    # Build dasha timeline
    dashas = []
    start_idx = DASHA_ORDER.index(dasha_lord)
    current_date = birth_date
    # First dasha with balance
    end_date = current_date + timedelta(days=balance_years * 365.25)
    dashas.append({
        "lord": dasha_lord,
        "start": current_date.strftime("%d %b %Y"),
        "end": end_date.strftime("%d %b %Y"),
        "years": round(balance_years, 2)
    })
    current_date = end_date
    for i in range(1, 10):
        lord = DASHA_ORDER[(start_idx + i) % 9]
        years = DASHA_YEARS[lord]
        end_date = current_date + timedelta(days=years * 365.25)
        dashas.append({
            "lord": lord,
            "start": current_date.strftime("%d %b %Y"),
            "end": end_date.strftime("%d %b %Y"),
            "years": years
        })
        current_date = end_date
        if (current_date - birth_date).days > 120 * 365:
            break
    return dashas, nak_name, pada, dasha_lord, round(balance_years, 2)

# ─── Manglik ──────────────────────────────────────────────────────────────────
def check_manglik(planet_positions, houses):
    """Mars in 1,4,7,8,12 from Lagna, Moon, or Venus = Manglik."""
    mars_lon = planet_positions["Mars"]["sidereal"]
    mars_house = None
    lagna_rashi = houses[0]
    mars_rashi = get_rashi(mars_lon)
    mars_house = (mars_rashi - lagna_rashi) % 12 + 1
    manglik_houses = [1, 4, 7, 8, 12]
    is_manglik = mars_house in manglik_houses
    partial = mars_house in [1, 4, 7]
    return {
        "is_manglik": is_manglik,
        "partial": partial and is_manglik,
        "mars_house": mars_house,
        "note": "Strong Manglik" if (is_manglik and not partial) else ("Partial Manglik" if partial else "Non-Manglik")
    }

# ─── Panchang ─────────────────────────────────────────────────────────────────
def calculate_panchang(jd, lat, lon):
    sun_lon = to_sidereal(sun_longitude(jd), jd)
    moon_lon = to_sidereal(moon_longitude(jd), jd)
    # Tithi
    diff = (moon_lon - sun_lon) % 360
    tithi_num = int(diff / 12) + 1
    tithis = ["Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi",
              "Saptami","Ashtami","Navami","Dashami","Ekadashi","Dwadashi",
              "Trayodashi","Chaturdashi","Purnima/Amavasya"]
    paksha = "Shukla" if diff < 180 else "Krishna"
    tithi_name = tithis[min(tithi_num-1, 14)]
    # Vara (weekday)
    varas = ["Ravivara (Sunday)","Somavara (Monday)","Mangalavara (Tuesday)",
             "Budhavara (Wednesday)","Guruvara (Thursday)","Shukravara (Friday)","Shanivara (Saturday)"]
    day_of_week = int(jd + 1.5) % 7
    # Yoga
    yoga_num = int((sun_lon + moon_lon) % 360 / (360/27))
    yogas = ["Vishkambha","Preeti","Ayushman","Saubhagya","Shobhana","Atiganda",
             "Sukarma","Dhriti","Shoola","Ganda","Vriddhi","Dhruva","Vyaghata",
             "Harshana","Vajra","Siddhi","Vyatipata","Variyan","Parigha","Shiva",
             "Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti"]
    # Karana
    karana_num = int(diff / 6) % 11
    karanas = ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti","Shakuni","Chatushpada","Naga","Kimstughna"]
    return {
        "tithi": f"{paksha} {tithi_name} ({tithi_num})",
        "vara": varas[day_of_week],
        "nakshatra": get_nakshatra(moon_lon)[0],
        "yoga": yogas[yoga_num % 27],
        "karana": karanas[karana_num % 11]
    }

# ─── Doshas ───────────────────────────────────────────────────────────────────
def check_doshas(planet_positions, houses):
    results = {}
    lagna_rashi = houses[0]

    def house_of(planet):
        r = get_rashi(planet_positions[planet]["sidereal"])
        return (r - lagna_rashi) % 12 + 1

    # Kaal Sarp Dosha: all planets between Rahu and Ketu
    rahu_lon = planet_positions["Rahu"]["sidereal"]
    ketu_lon = planet_positions["Ketu"]["sidereal"]
    planets_check = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
    ksd = True
    for p in planets_check:
        pl = planet_positions[p]["sidereal"]
        # Check if planet is between Rahu and Ketu (going in direction of Rahu to Ketu)
        d = (pl - rahu_lon) % 360
        dk = (ketu_lon - rahu_lon) % 360
        if d > dk:
            ksd = False
            break
    results["Kaal Sarp Dosha"] = "Present" if ksd else "Absent"

    # Guru Chandal Dosha: Jupiter conjunct Rahu or Ketu
    jup_rashi = get_rashi(planet_positions["Jupiter"]["sidereal"])
    rahu_rashi = get_rashi(planet_positions["Rahu"]["sidereal"])
    ketu_rashi = get_rashi(planet_positions["Ketu"]["sidereal"])
    results["Guru Chandal Dosha"] = "Present" if jup_rashi in [rahu_rashi, ketu_rashi] else "Absent"

    # Shani Dosha (Saturn in 1,3,7,10,12)
    sat_house = house_of("Saturn")
    results["Shani Dosha"] = "Present" if sat_house in [1,3,7,10,12] else "Absent"

    # Pitru Dosha: Sun + Rahu or Moon + Ketu in same sign
    sun_rashi = get_rashi(planet_positions["Sun"]["sidereal"])
    moon_rashi = get_rashi(planet_positions["Moon"]["sidereal"])
    results["Pitru Dosha"] = "Present" if (sun_rashi == rahu_rashi or moon_rashi == ketu_rashi) else "Absent"

    return results

# ─── Main Kundli Calculator ───────────────────────────────────────────────────
def calculate_kundli(name, gender, dob, tob, lat, lon, tz_offset):
    """
    dob: "DD/MM/YYYY", tob: "HH:MM", lat/lon: float, tz_offset: float (hours)
    """
    day, month, year = map(int, dob.split("/"))
    h, m = map(int, tob.split(":"))
    utc_hour = h + m/60.0 - tz_offset
    jd = julian_day(year, month, day, utc_hour)

    # Planets
    planet_positions = {}
    for p in PLANETS:
        trop = planet_longitude(jd, p)
        sid = to_sidereal(trop, jd)
        rashi_idx = get_rashi(sid)
        nak_name, nak_idx, pada = get_nakshatra(sid)
        planet_positions[p] = {
            "tropical": round(trop, 4),
            "sidereal": round(sid, 4),
            "rashi": RASHI_NAMES[rashi_idx],
            "rashi_idx": rashi_idx,
            "degree": round(get_degree_in_rashi(sid), 2),
            "nakshatra": nak_name,
            "pada": pada,
            "lord": RASHI_LORDS[rashi_idx]
        }

    # Ascendant
    asc_trop = ascendant(jd, lat, lon)
    asc_sid = to_sidereal(asc_trop, jd)
    lagna_rashi = get_rashi(asc_sid)

    # Houses
    houses = calculate_houses(asc_sid)

    # Assign planets to houses
    for p in PLANETS:
        p_rashi = planet_positions[p]["rashi_idx"]
        house_num = (p_rashi - lagna_rashi) % 12 + 1
        planet_positions[p]["house"] = house_num

    # Moon sign & Nakshatra
    moon_sid = planet_positions["Moon"]["sidereal"]
    moon_rashi_idx = get_rashi(moon_sid)
    nak_name, nak_idx, pada = get_nakshatra(moon_sid)

    # Dasha
    birth_dt = datetime(year, month, day, h, m)
    dashas, curr_nak, curr_pada, dasha_lord, balance = vimshottari_dasha(moon_sid, birth_dt)

    # Manglik
    manglik = check_manglik(planet_positions, houses)

    # Doshas
    doshas = check_doshas(planet_positions, houses)

    # Panchang
    panchang = calculate_panchang(jd, lat, lon)

    return {
        "name": name,
        "gender": gender,
        "dob": dob,
        "tob": tob,
        "lat": lat,
        "lon": lon,
        "tz_offset": tz_offset,
        "jd": jd,
        "lagna": {
            "rashi": RASHI_NAMES[lagna_rashi],
            "rashi_idx": lagna_rashi,
            "degree": round(get_degree_in_rashi(asc_sid), 2),
            "lord": RASHI_LORDS[lagna_rashi]
        },
        "moon_sign": RASHI_NAMES[moon_rashi_idx],
        "moon_sign_idx": moon_rashi_idx,
        "nakshatra": nak_name,
        "nakshatra_pada": pada,
        "nakshatra_lord": NAKSHATRA_LORDS[nak_idx],
        "planets": planet_positions,
        "houses": houses,
        "dashas": dashas,
        "current_dasha": dasha_lord,
        "dasha_balance": balance,
        "manglik": manglik,
        "doshas": doshas,
        "panchang": panchang,
        "rashi_names": RASHI_NAMES,
        "rashi_lords": RASHI_LORDS,
    }

# ─── Gun Milan (36 Gunas) ─────────────────────────────────────────────────────
VARNA = {  # 0=Brahmin,1=Kshatriya,2=Vaishya,3=Shudra
    "Ashwini":3,"Bharani":3,"Krittika":1,"Rohini":2,"Mrigashira":2,"Ardra":3,
    "Punarvasu":1,"Pushya":1,"Ashlesha":3,"Magha":3,"Purva Phalguni":3,
    "Uttara Phalguni":1,"Hasta":2,"Chitra":3,"Swati":3,"Vishakha":1,
    "Anuradha":1,"Jyeshtha":3,"Mula":3,"Purva Ashadha":3,"Uttara Ashadha":1,
    "Shravana":2,"Dhanishtha":3,"Shatabhisha":3,"Purva Bhadrapada":3,
    "Uttara Bhadrapada":1,"Revati":1
}
VASHYA = {  # groups
    "Aries":0,"Leo":0,"Sagittarius":0,
    "Taurus":1,"Capricorn":1,
    "Gemini":2,"Libra":2,"Aquarius":2,
    "Cancer":3,"Scorpio":3,"Pisces":3,
    "Virgo":4,"Gemini":4
}
YONI = {
    "Ashwini":"Horse","Bharani":"Elephant","Krittika":"Sheep","Rohini":"Serpent",
    "Mrigashira":"Serpent","Ardra":"Dog","Punarvasu":"Cat","Pushya":"Sheep",
    "Ashlesha":"Cat","Magha":"Rat","Purva Phalguni":"Rat","Uttara Phalguni":"Bull",
    "Hasta":"Buffalo","Chitra":"Tiger","Swati":"Buffalo","Vishakha":"Tiger",
    "Anuradha":"Hare","Jyeshtha":"Hare","Mula":"Dog","Purva Ashadha":"Monkey",
    "Uttara Ashadha":"Mongoose","Shravana":"Monkey","Dhanishtha":"Lion",
    "Shatabhisha":"Horse","Purva Bhadrapada":"Lion","Uttara Bhadrapada":"Cow",
    "Revati":"Elephant"
}
YONI_ENEMIES = {
    "Horse":"Buffalo","Buffalo":"Horse","Elephant":"Lion","Lion":"Elephant",
    "Sheep":"Monkey","Monkey":"Sheep","Serpent":"Mongoose","Mongoose":"Serpent",
    "Dog":"Hare","Hare":"Dog","Cat":"Rat","Rat":"Cat","Cow":"Tiger","Tiger":"Cow"
}
GANA = {  # Deva=0,Manav=1,Rakshasa=2
    "Ashwini":0,"Mrigashira":0,"Punarvasu":0,"Pushya":0,"Hasta":0,"Swati":0,
    "Anuradha":0,"Shravana":0,"Revati":0,
    "Bharani":1,"Rohini":1,"Ardra":1,"Purva Phalguni":1,"Uttara Phalguni":1,
    "Purva Ashadha":1,"Uttara Ashadha":1,"Purva Bhadrapada":1,"Uttara Bhadrapada":1,
    "Krittika":2,"Ashlesha":2,"Magha":2,"Chitra":2,"Vishakha":2,"Jyeshtha":2,
    "Mula":2,"Dhanishtha":2,"Shatabhisha":2
}
GANA_NAMES = ["Deva","Manav","Rakshasa"]
NADI = {  # 0=Aadi,1=Madhya,2=Antya
    "Ashwini":0,"Ardra":0,"Punarvasu":0,"Uttara Phalguni":0,"Hasta":0,
    "Jyeshtha":0,"Mula":0,"Shatabhisha":0,"Purva Bhadrapada":0,
    "Bharani":1,"Mrigashira":1,"Pushya":1,"Purva Phalguni":1,"Chitra":1,
    "Anuradha":1,"Purva Ashadha":1,"Dhanishtha":1,"Uttara Bhadrapada":1,
    "Krittika":2,"Rohini":2,"Ashlesha":2,"Magha":2,"Swati":2,"Vishakha":2,
    "Uttara Ashadha":2,"Shravana":2,"Revati":2
}
NADI_NAMES = ["Aadi","Madhya","Antya"]

PLANET_FRIENDS = {
    "Sun":    {"friends":["Moon","Mars","Jupiter"],"neutral":["Mercury"],"enemies":["Venus","Saturn","Rahu","Ketu"]},
    "Moon":   {"friends":["Sun","Mercury"],"neutral":["Mars","Jupiter","Venus","Saturn"],"enemies":["Rahu","Ketu"]},
    "Mars":   {"friends":["Sun","Moon","Jupiter"],"neutral":["Venus","Saturn"],"enemies":["Mercury","Rahu","Ketu"]},
    "Mercury":{"friends":["Sun","Venus"],"neutral":["Mars","Jupiter","Saturn"],"enemies":["Moon","Rahu","Ketu"]},
    "Jupiter":{"friends":["Sun","Moon","Mars"],"neutral":["Saturn"],"enemies":["Mercury","Venus","Rahu","Ketu"]},
    "Venus":  {"friends":["Mercury","Saturn"],"neutral":["Mars","Jupiter"],"enemies":["Sun","Moon","Rahu","Ketu"]},
    "Saturn": {"friends":["Mercury","Venus","Rahu"],"neutral":["Jupiter"],"enemies":["Sun","Moon","Mars","Ketu"]},
}

def graha_maitri_score(lord1, lord2):
    if lord1 == lord2:
        return 5
    rel1 = None
    if lord1 in PLANET_FRIENDS:
        if lord2 in PLANET_FRIENDS[lord1]["friends"]: rel1 = "friend"
        elif lord2 in PLANET_FRIENDS[lord1]["enemies"]: rel1 = "enemy"
        else: rel1 = "neutral"
    rel2 = None
    if lord2 in PLANET_FRIENDS:
        if lord1 in PLANET_FRIENDS[lord2]["friends"]: rel2 = "friend"
        elif lord1 in PLANET_FRIENDS[lord2]["enemies"]: rel2 = "enemy"
        else: rel2 = "neutral"
    combo = (rel1, rel2)
    scores = {
        ("friend","friend"): 5,
        ("friend","neutral"): 4,
        ("neutral","friend"): 4,
        ("neutral","neutral"): 3,
        ("friend","enemy"): 1,
        ("enemy","friend"): 1,
        ("neutral","enemy"): 0.5,
        ("enemy","neutral"): 0.5,
        ("enemy","enemy"): 0,
    }
    return scores.get(combo, 2)

def calculate_gun_milan(k1, k2):
    nak1 = k1["nakshatra"]
    nak2 = k2["nakshatra"]
    rashi1 = k1["moon_sign_idx"]
    rashi2 = k2["moon_sign_idx"]
    lord1 = RASHI_LORDS[rashi1]
    lord2 = RASHI_LORDS[rashi2]

    results = {}

    # 1. Varna (1 point)
    v1 = VARNA.get(nak1, 2)
    v2 = VARNA.get(nak2, 2)
    varna_score = 1 if v2 <= v1 else 0
    results["Varna"] = {"score": varna_score, "max": 1,
        "detail": f"Bride:{['Brahmin','Kshatriya','Vaishya','Shudra'][v2]} Groom:{['Brahmin','Kshatriya','Vaishya','Shudra'][v1]}"}

    # 2. Vashya (2 points)
    rashi_name1 = RASHI_NAMES[rashi1].split("(")[0].strip()
    rashi_name2 = RASHI_NAMES[rashi2].split("(")[0].strip()
    v1g = rashi1 % 5
    v2g = rashi2 % 5
    vashya = 2 if v1g == v2g else (1 if abs(v1g-v2g)==1 else 0)
    results["Vashya"] = {"score": vashya, "max": 2, "detail": f"{rashi_name1} & {rashi_name2}"}

    # 3. Tara (3 points)
    nak1_idx = NAKSHATRAS.index(nak1) if nak1 in NAKSHATRAS else 0
    nak2_idx = NAKSHATRAS.index(nak2) if nak2 in NAKSHATRAS else 0
    tara = ((nak2_idx - nak1_idx) % 9) + 1
    tara_score = 3 if tara in [1,3,5,7] else (1 if tara in [2,4,6] else 0)
    results["Tara"] = {"score": tara_score, "max": 3, "detail": f"Tara {tara}"}

    # 4. Yoni (4 points)
    y1 = YONI.get(nak1, "Horse")
    y2 = YONI.get(nak2, "Horse")
    if y1 == y2: yoni_s = 4
    elif YONI_ENEMIES.get(y1) == y2 or YONI_ENEMIES.get(y2) == y1: yoni_s = 0
    else: yoni_s = 2
    results["Yoni"] = {"score": yoni_s, "max": 4, "detail": f"{y1} & {y2}"}

    # 5. Graha Maitri (5 points)
    gm = graha_maitri_score(lord1, lord2)
    results["Graha Maitri"] = {"score": gm, "max": 5, "detail": f"{lord1} & {lord2}"}

    # 6. Gana (6 points)
    g1 = GANA.get(nak1, 1)
    g2 = GANA.get(nak2, 1)
    if g1 == g2: gana_s = 6
    elif g1 == 0 and g2 == 1: gana_s = 5
    elif g1 == 1 and g2 == 0: gana_s = 4
    elif (g1 == 0 and g2 == 2) or (g1 == 2 and g2 == 0): gana_s = 0
    else: gana_s = 3
    results["Gana"] = {"score": gana_s, "max": 6,
        "detail": f"{GANA_NAMES[g1]} & {GANA_NAMES[g2]}"}

    # 7. Bhakoot (7 points)
    diff = (rashi2 - rashi1) % 12 + 1
    if diff in [6,8,12]: bhakoot = 0
    elif diff in [2,12,5,9]: bhakoot = 3
    else: bhakoot = 7
    results["Bhakoot"] = {"score": bhakoot, "max": 7, "detail": f"Position: {diff}"}

    # 8. Nadi (8 points)
    n1 = NADI.get(nak1, 0)
    n2 = NADI.get(nak2, 0)
    nadi_s = 0 if n1 == n2 else 8
    results["Nadi"] = {"score": nadi_s, "max": 8,
        "detail": f"{NADI_NAMES[n1]} & {NADI_NAMES[n2]}"}

    total = sum(v["score"] for v in results.values())
    percentage = round((total / 36) * 100, 1)

    verdict = "Excellent" if total >= 28 else \
              "Very Good" if total >= 24 else \
              "Good" if total >= 18 else \
              "Average" if total >= 14 else "Poor"

    # Nadi Dosha
    nadi_dosha = n1 == n2
    # Bhakoot Dosha
    bhakoot_dosha = bhakoot == 0

    return {
        "gunas": results,
        "total": total,
        "percentage": percentage,
        "verdict": verdict,
        "nadi_dosha": nadi_dosha,
        "bhakoot_dosha": bhakoot_dosha,
    }
