"""
Cjelogodišnja simulacija solarne ograde (4 strane)
koristeći bifacial_radiance i Radiance.
Konfiguracija: 19 panela (4 SE, 5 SW, 5 NE, 5 NW)
Nagib: 60°, albedo: 0.4 (bijeli kamen)
"""

import os
import pandas as pd
from bifacial_radiance import RadianceObj, AnalysisObj

# =========================== KONFIGURACIJA ===========================
MAIN_NAME = "solar_fence_annual"
BASE_PATH = os.path.abspath(f"./{MAIN_NAME}")
os.makedirs(BASE_PATH, exist_ok=True)

# --- PUTANJA DO EPW FAJLA (ZAMIJENITE SA VAŠOM) ---
EPW_FILE = r"E:\Radiance_build\moja_solar_ograda\EPWs\SRB_Podgorica.134620_IWEC.epw"

# --- DIMENZIJE PANELA (m) ---
PANEL_X = 1.134   # širina
PANEL_Y = 2.2     # visina
BIFACIALITY = 0.75
ALBEDO = 0.4

# --- STRANE OGRADE: (naziv, azimut, broj panela) ---
SIDES = [
    ("Southeast", 135, 4),   # ulaz
    ("Southwest", 225, 5),
    ("Northeast",  45, 5),
    ("Northwest", 315, 5),
]

# =========================== PETLJA KROZ STRANE ===========================
results = {}   # rječnik za čuvanje godišnje proizvodnje po strani

for side_name, azimuth, num_panels in SIDES:
    print(f"\n🚀 Pokrećem simulaciju za: {side_name} (azimut {azimuth}°, {num_panels} panela)")

    # 1. Kreiraj novi RadianceObj za svaku stranu
    demo = RadianceObj(f"{MAIN_NAME}_{side_name}", path=BASE_PATH)
    demo.setGround(ALBEDO)

    # 2. Definiši panel (bifacijalnost)
    module = demo.makeModule(
        name=f'panel_{side_name}',
        x=PANEL_X,
        y=PANEL_Y,
        bifi=BIFACIALITY
    )

    # 3. Učitaj EPW fajl
    if not os.path.exists(EPW_FILE):
        raise FileNotFoundError(f"EPW fajl nije pronađen: {EPW_FILE}")
    metdata = demo.readWeatherFile(EPW_FILE, coerce_year=2023)

    # 4. Generiši nebo za cijelu godinu (genCumSky)
    #    OVDJE JE KLJUČNA ISPRAVKA:
    #    demo.genCumSky prima putanju do EPW fajla kao DIREKTAN argument,
    #    a ne kao ključnu riječ (keyword argument).
    demo.genCumSky(EPW_FILE)

    # 5. Kreiraj scenu (jedan red, bez sjenčenja između redova)
    scene_dict = {
        'tilt': 60,
        'azimuth': azimuth,
        'nMods': num_panels,
        'nRows': 1,
        'clearance_height': 0.5,
        'pitch': 10.0      # dovoljno veliko jer je samo jedan red
    }
    scene = demo.makeScene(module=module, sceneDict=scene_dict)

    # 6. Spajanje u .oct fajl
    oct_file = demo.makeOct(demo.getfilelist())

    # 7. Pokretanje analize za cijelu godinu
    analysis = AnalysisObj(oct_file, demo.basename)
    frontscan, backscan = analysis.moduleAnalysis(scene)

    # 8. Izračun godišnje proizvodnje (kWh)
    # frontscan i backscan su DataFrame-i sa satnim vrijednostima u W/m2
    # Površina jednog panela:
    area_one_panel = PANEL_X * PANEL_Y
    
    # Ukupna energija (Wh) = (zbir front + zbir back) * površina * broj panela
    # Dodajemo i množenje sa brojem panela, jer frontscan i backscan daju vrijednosti po modulu.
    front_sum = frontscan.sum().sum() if hasattr(frontscan, 'sum') else frontscan.sum()
    back_sum  = backscan.sum().sum()  if hasattr(backscan,  'sum') else backscan.sum()
    
    energy_wh = (front_sum + back_sum) * area_one_panel * num_panels
    energy_kwh = energy_wh / 1000
    
    results[side_name] = energy_kwh
    print(f"   ✅ {side_name}: {energy_kwh:8.0f} kWh/god")

# =========================== REZULTATI ===========================
print("\n" + "="*60)
print("📊 GODIŠNJA PROIZVODNJA PO STRANAMA")
print("-"*60)
total_kwh = 0
for side, kwh in results.items():
    print(f"  {side:10} : {kwh:8.0f} kWh")
    total_kwh += kwh
print("-"*60)
print(f"  UKUPNO    : {total_kwh:8.0f} kWh")
print("="*60)

installed_kwp = 19 * 585 / 1000
print(f"\n📈 Instalisana snaga: 19 × 585 Wp = {installed_kwp:.2f} kWp")
print(f"⚡ Specifična proizvodnja: {total_kwh / installed_kwp:.0f} kWh/kWp")
print(f"☀️  Prosječna dnevna proizvodnja: {total_kwh / 365:.1f} kWh/dan")
print("\n✅ Simulacija završena.")