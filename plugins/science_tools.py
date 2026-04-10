# plugins/science_tools.py — Science: Physics, Chemistry, Astronomy, Biology

import math
from plugins.advanced_ai import _ai


# ══ PHYSICS ═══════════════════════════════════════════════════════════════════
def newton_second_law(force=None, mass=None, acceleration=None):
    """F = ma — solve for any one missing variable."""
    given = sum(x is not None for x in [force, mass, acceleration])
    if given < 2:
        return "Provide at least 2 values: force (N), mass (kg), acceleration (m/s²)"
    if force is None:
        result = float(mass) * float(acceleration)
        return f"F = m×a = {mass}×{acceleration} = {result:.4f} N"
    if mass is None:
        result = float(force) / float(acceleration)
        return f"m = F/a = {force}/{acceleration} = {result:.4f} kg"
    result = float(force) / float(mass)
    return f"a = F/m = {force}/{mass} = {result:.4f} m/s²"

def kinetic_energy(mass, velocity):
    ke = 0.5 * float(mass) * float(velocity)**2
    return f"KE = ½mv² = ½×{mass}×{velocity}² = {ke:.4f} J"

def potential_energy(mass, height, g=9.81):
    pe = float(mass) * float(g) * float(height)
    return f"PE = mgh = {mass}×{g}×{height} = {pe:.4f} J"

def ohms_law(voltage=None, current=None, resistance=None):
    given = sum(x is not None for x in [voltage, current, resistance])
    if given < 2:
        return "Provide at least 2: voltage (V), current (A), resistance (Ω)"
    if voltage is None:
        result = float(current) * float(resistance)
        return f"V = I×R = {current}×{resistance} = {result:.4f} V"
    if current is None:
        result = float(voltage) / float(resistance)
        return f"I = V/R = {voltage}/{resistance} = {result:.6f} A"
    result = float(voltage) / float(current)
    return f"R = V/I = {voltage}/{current} = {result:.4f} Ω"

def electric_power(voltage=None, current=None, resistance=None, power=None):
    if voltage and current:
        p = float(voltage) * float(current)
        return f"P = V×I = {voltage}×{current} = {p:.4f} W"
    if current and resistance:
        p = float(current)**2 * float(resistance)
        return f"P = I²R = {current}²×{resistance} = {p:.4f} W"
    if voltage and resistance:
        p = float(voltage)**2 / float(resistance)
        return f"P = V²/R = {voltage}²/{resistance} = {p:.4f} W"
    return "Provide: voltage+current, or current+resistance, or voltage+resistance"

def projectile_motion(velocity, angle_deg, height=0):
    v  = float(velocity); angle = math.radians(float(angle_deg)); h = float(height)
    g  = 9.81
    vx = v * math.cos(angle)
    vy = v * math.sin(angle)
    if h == 0:
        time  = 2 * vy / g
        range_= vx * time
        max_h = vy**2 / (2*g)
    else:
        disc  = vy**2 + 2*g*h
        time  = (vy + math.sqrt(disc)) / g
        range_= vx * time
        max_h = h + vy**2 / (2*g)
    return (f"🚀 Projectile Motion:\n"
            f"  Initial velocity : {v} m/s @ {angle_deg}°\n"
            f"  Vx = {vx:.2f} m/s  |  Vy = {vy:.2f} m/s\n"
            f"  Time of flight   : {time:.2f} s\n"
            f"  Max height       : {max_h:.2f} m\n"
            f"  Range            : {range_:.2f} m")

def speed_of_light_calc(distance_km):
    c     = 299792.458  # km/s
    t_sec = float(distance_km) / c
    return (f"⚡ Speed of light:\n"
            f"  Distance : {float(distance_km):,.0f} km\n"
            f"  Time     : {t_sec:.6f} s\n"
            f"  = {t_sec*1000:.4f} ms\n"
            f"  (Light speed: 299,792 km/s)")

def pendulum_period(length_m):
    g = 9.81
    T = 2 * math.pi * math.sqrt(float(length_m) / g)
    f = 1 / T
    return (f"🕰️ Simple Pendulum:\n"
            f"  Length   : {length_m} m\n"
            f"  Period   : {T:.4f} s\n"
            f"  Frequency: {f:.4f} Hz")

def wavelength_frequency(value, given="frequency"):
    c = 3e8  # speed of light m/s
    v = float(value)
    if "freq" in given.lower():
        wl = c / v
        return f"λ = c/f = {c}/{v:.2e} = {wl:.4e} m"
    else:
        freq = c / v
        return f"f = c/λ = {c}/{v:.2e} = {freq:.4e} Hz"


# ══ CHEMISTRY ════════════════════════════════════════════════════════════════
ELEMENTS = {
    "H":("Hydrogen",1,1.008),"He":("Helium",2,4.003),"Li":("Lithium",3,6.941),
    "Be":("Beryllium",4,9.012),"B":("Boron",5,10.81),"C":("Carbon",6,12.011),
    "N":("Nitrogen",7,14.007),"O":("Oxygen",8,15.999),"F":("Fluorine",9,18.998),
    "Ne":("Neon",10,20.18),"Na":("Sodium",11,22.99),"Mg":("Magnesium",12,24.305),
    "Al":("Aluminum",13,26.982),"Si":("Silicon",14,28.086),"P":("Phosphorus",15,30.974),
    "S":("Sulfur",16,32.065),"Cl":("Chlorine",17,35.453),"Ar":("Argon",18,39.948),
    "K":("Potassium",19,39.098),"Ca":("Calcium",20,40.078),"Fe":("Iron",26,55.845),
    "Cu":("Copper",29,63.546),"Zn":("Zinc",30,65.38),"Ag":("Silver",47,107.868),
    "Au":("Gold",79,196.967),"Hg":("Mercury",80,200.59),"Pb":("Lead",82,207.2),
}

def element_info(symbol_or_name):
    q = symbol_or_name.strip()
    # Try symbol
    if q in ELEMENTS:
        name, num, mass = ELEMENTS[q]
        return (f"⚗️ Element: {name} ({q})\n"
                f"  Atomic Number : {num}\n"
                f"  Atomic Mass   : {mass} u")
    # Try name
    for sym,(name,num,mass) in ELEMENTS.items():
        if name.lower() == q.lower():
            return (f"⚗️ Element: {name} ({sym})\n"
                    f"  Atomic Number : {num}\n"
                    f"  Atomic Mass   : {mass} u")
    return f"Element not found: {q}. Try symbol (e.g., Fe) or name (e.g., Iron)"

def molar_mass(formula):
    try:
        import re
        tokens = re.findall(r'([A-Z][a-z]?)(\d*)', formula)
        total  = 0.0; breakdown = []
        for sym, count in tokens:
            if not sym: continue
            n = int(count) if count else 1
            if sym in ELEMENTS:
                mass = ELEMENTS[sym][2] * n
                total += mass
                breakdown.append(f"  {sym}×{n} = {mass:.3f}")
            else:
                return f"Unknown element: {sym}"
        return f"⚗️ Molar mass of {formula}:\n" + "\n".join(breakdown) + f"\n  TOTAL: {total:.3f} g/mol"
    except Exception as e:
        return f"Formula error: {e}"

def ph_calculator(h_concentration):
    try:
        ph = -math.log10(float(h_concentration))
        if ph < 7:   nature = "Acidic 🔴"
        elif ph > 7: nature = "Basic/Alkaline 🔵"
        else:        nature = "Neutral ⚪"
        return (f"⚗️ pH = -log[H⁺] = -log({h_concentration})\n"
                f"  pH     : {ph:.2f}\n"
                f"  Nature : {nature}")
    except Exception as e:
        return f"pH error: {e}"

def boiling_point_altitude(altitude_m):
    """Estimate water boiling point at altitude."""
    bp = 100 - (float(altitude_m) / 300)
    return (f"🌡️ Water boiling point at {altitude_m}m altitude:\n"
            f"  ≈ {bp:.1f}°C\n"
            f"  (Decreases ~1°C per 300m of altitude)")


# ══ ASTRONOMY ════════════════════════════════════════════════════════════════
def planet_info(planet):
    PLANETS = {
        "mercury":{"distance":"57.9M km","orbital_period":"88 days","diameter":"4,879 km","moons":0,"temp":"-180 to 430°C"},
        "venus":  {"distance":"108M km","orbital_period":"225 days","diameter":"12,104 km","moons":0,"temp":"465°C avg"},
        "earth":  {"distance":"149.6M km","orbital_period":"365.25 days","diameter":"12,742 km","moons":1,"temp":"-89 to 58°C"},
        "mars":   {"distance":"227.9M km","orbital_period":"687 days","diameter":"6,779 km","moons":2,"temp":"-125 to 20°C"},
        "jupiter":{"distance":"778.5M km","orbital_period":"11.86 years","diameter":"139,820 km","moons":95,"temp":"-108°C avg"},
        "saturn": {"distance":"1.43B km","orbital_period":"29.5 years","diameter":"116,460 km","moons":146,"temp":"-138°C avg"},
        "uranus": {"distance":"2.87B km","orbital_period":"84 years","diameter":"50,724 km","moons":28,"temp":"-195°C avg"},
        "neptune":{"distance":"4.5B km","orbital_period":"165 years","diameter":"49,244 km","moons":16,"temp":"-200°C avg"},
    }
    p = PLANETS.get(planet.lower())
    if not p: return f"Planet not found: {planet}"
    return (f"🪐 {planet.title()}:\n" +
            "\n".join(f"  {k.replace('_',' ').title():<20}: {v}" for k,v in p.items()))

def light_years_to_km(ly):
    km = float(ly) * 9.461e12
    return f"🌌 {ly} light-year(s) = {km:.3e} km"

def age_of_universe():
    return "🌌 Age of Universe: ~13.8 billion years (13,800,000,000 years)\n  Based on CMB measurements and Hubble constant."

def solar_system_scale(reference_object="basketball"):
    return _ai(f"Describe the solar system to scale using a {reference_object} as the Sun. "
               f"Give all 8 planets' relative sizes and distances in everyday terms.")


# ══ BIOLOGY ═══════════════════════════════════════════════════════════════════
def dna_complement(sequence):
    """Get DNA complement strand."""
    comp = {"A":"T","T":"A","G":"C","C":"G","a":"t","t":"a","g":"c","c":"g"}
    try:
        complement = "".join(comp.get(b,"?") for b in sequence)
        return (f"🧬 DNA Complement:\n"
                f"  Original   : 5'-{sequence.upper()}-3'\n"
                f"  Complement : 3'-{complement.upper()}-5'\n"
                f"  Anti-parallel: 5'-{complement[::-1].upper()}-3'")
    except Exception as e:
        return f"DNA error: {e}"

def mrna_from_dna(dna):
    """Transcribe DNA to mRNA."""
    trans = {"A":"U","T":"A","G":"C","C":"G"}
    try:
        mrna = "".join(trans.get(b.upper(),"?") for b in dna)
        return f"🧬 mRNA Transcription:\n  DNA  : 5'-{dna.upper()}-3'\n  mRNA : 5'-{mrna}-3'"
    except Exception as e:
        return f"Transcription error: {e}"

def gc_content(sequence):
    """Calculate GC content of DNA sequence."""
    seq = sequence.upper()
    gc  = sum(1 for b in seq if b in "GC")
    total = len([b for b in seq if b in "ATGC"])
    pct = gc / total * 100 if total > 0 else 0
    return (f"🧬 GC Content of sequence ({len(seq)} bp):\n"
            f"  G: {seq.count('G')}  C: {seq.count('C')}  "
            f"A: {seq.count('A')}  T: {seq.count('T')}\n"
            f"  GC content: {pct:.1f}%\n"
            f"  AT content: {100-pct:.1f}%")
