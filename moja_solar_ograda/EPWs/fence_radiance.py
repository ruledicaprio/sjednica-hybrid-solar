"""
Simulacija solarne ograde oko antenskog stuba
koristeći bifacial_radiance i Radiance.
Konfiguracija: 19 panela (4 SE, 5 SW, 5 NE, 5 NW)
Nagib: 60°, albedo: 0.4 (bijeli kamen)
"""

import os
import pandas as pd
from bifacial_radiance import RadianceObj, AnalysisObj

# =========================== KONFIGURACIJA ===========================
SIMULATION_NAME = "solar_fence"
BASE_PATH = os.path.abspath(f"./{SIMULATION_NAME}")
os.makedirs(BASE_PATH, exist_ok=True)

# --- PUTANJA DO EPW FAJLA (ZAMIJENI SA TVOJOM) ---
EPW_FILE = r"E:\Radiance_build\moja_solar_ograda\EPWs\SRB_Podgorica.134620_IWEC.epw"   # <--- OVDJE STAVI PRAVU PUTANJU

# --- DIMENZIJE PANELA (m) ---
PANEL_X = 1.134   # širina
PANEL_Y = 2.2     # visina
BIFACIALITY = 0.75
ALBEDO = 0.4

# --- STRANE OGRADE: (naziv, azimut, broj panela) ---
SIDES = [
    ("Southeast", 135, 4),
    ("Southwest", 225, 5),
    ("Northeast",  45, 5),
    ("Northwest", 315, 5),
]

# =========================== INICIJALIZACIJA ===========================
demo = RadianceObj(SIMULATION_NAME, path=BASE_PATH)
demo.setGround(ALBEDO)

module = demo.makeModule(
    name='TOPBiHiKu6',
    x=PANEL_X,
    y=PANEL_Y,
    bifaciality=BIFACIALITY
)

# Učitavanje vremenskih podataka
if not os.path.exists(EPW_FILE):
    raise FileNotFoundError(f"EPW fajl nije pronađen: {EPW_FILE}")
met_data = demo.readWeatherFile(EPW_FILE, coerce_year=2023)
if met_data is None:
    raise RuntimeError("Neuspješno učitavanje EPW fajla.")

# Generisanje neba za cijelu godinu
demo.gendaylit(0)
demo.genCumSky()

# =========================== KREIRANJE SCENA ===========================
scene_objects = []

for name, azimuth, num_panels in SIDES:
    scene_dict = {
        'tilt': 60,
        'azimuth': azimuth,
        'nMods': num_panels,
        'nRows': 1,
        'clearance_height': 0.5,
        'pitch': 10.0
    }
    scene_obj = demo.makeScene(module=module, sceneDict=scene_dict, append=True)
    scene_objects.append(scene_obj)
    print(f"Scena dodana: {name} ({num_panels} panela, azimut {azimuth}°)")

oct_file = demo.makeOct(demo.getfilelist())
print(f".oct fajl kreiran: {oct_file}")

# =========================== ANALIZA PO SCENAMA ===========================
# Rezultati će se čuvati u folderu 'results'
# Iz foldera results se čitaju podaci i računa proizvodnja
results = {}

for idx, scene_obj in enumerate(scene_objects):
    # Kreiraj AnalysisObj - Bez scene parametra
    analysis = AnalysisObj(oct_file, demo.basename)
    
    # Dodaj scenu u AnalysisObj
    analysis.addScene(scene_obj)
    
    # Pokreni analizu za ovu scenu
    analysis.moduleAnalysis()
    
    # Učitaj rezultate
    result_file = f"results/{demo.basename}_{scene_obj.name}_results.csv"
    if os.path.exists(result_file):
        df = pd.read_csv(result_file)
        results[SIDES[idx][0]] = df
        print(f"Analiza završena za {SIDES[idx][0]}")
    else:
        print(f"Greška: Nije pronađen fajl sa rezultatima za {SIDES[idx][0]}")

# =========================== POST-PROCESSING ===========================
# Ovdje se računa ukupna godišnja proizvodnja
total_kwh = 0.0
for side_name, df in results.items():
    # Pretpostavka da kolone 'Wm2Front' i 'Wm2Back' postoje u df-u
    # Ovo računa energiju u Wh
    energy_wh = (df['Wm2Front'].sum() + df['Wm2Back'].sum()) * (PANEL_X * PANEL_Y)
    energy_kwh = energy_wh / 1000
    total_kwh += energy_kwh
    print(f"{side_name:10} : {energy_kwh:8.0f} kWh/god")

print("\n" + "="*50)
print(f"UKUPNA GODIŠNJA PROIZVODNJA: {total_kwh:8.0f} kWh")
print(f"Instalisana snaga: 19 × 585 Wp = {19*585/1000:.2f} kWp")
print(f"Specifična proizvodnja: {total_kwh / (19*585/1000):.0f} kWh/kWp")
print("="*50)