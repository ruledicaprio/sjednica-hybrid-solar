import os
import time
import pandas as pd
from bifacial_radiance import RadianceObj, AnalysisObj

MAIN_NAME = "solar_fence_annual"
BASE_PATH = os.path.abspath(f"./{MAIN_NAME}")
os.makedirs(BASE_PATH, exist_ok=True)

EPW_FILE = r"E:\Radiance_build\moja_solar_ograda\EPWs\SRB_Podgorica.134620_IWEC.epw"

PANEL_X = 1.134
PANEL_Y = 2.2
BIFACIALITY = 0.75
ALBEDO = 0.4

SIDES = [
    ("Southeast", 135, 4),
    ("Southwest", 225, 5),
    ("Northeast",  45, 5),
    ("Northwest", 315, 5),
]

results = {}

for side_name, azimuth, num_panels in SIDES:
    print(f"\n🚀 Pokrećem simulaciju za: {side_name} (azimut {azimuth}°, {num_panels} panela)")

    demo = RadianceObj(f"{MAIN_NAME}_{side_name}", path=BASE_PATH)
    demo.setGround(ALBEDO)

    module = demo.makeModule(
        name=f'panel_{side_name}',
        x=PANEL_X,
        y=PANEL_Y,
        bifi=BIFACIALITY
    )

    if not os.path.exists(EPW_FILE):
        raise FileNotFoundError(f"EPW fajl nije pronađen: {EPW_FILE}")
    demo.readWeatherFile(EPW_FILE, coerce_year=2023)

    demo.genCumSky(EPW_FILE)

    scene_dict = {
        'tilt': 60,
        'azimuth': azimuth,
        'nMods': num_panels,
        'nRows': 1,
        'clearance_height': 0.5,
        'pitch': 10.0
    }
    scene = demo.makeScene(module=module, sceneDict=scene_dict)

    oct_file = demo.makeOct(demo.getfilelist())

    # ========== ISPRAVLJENI DIO ==========
    analysis = AnalysisObj(oct_file, demo.basename)
    frontscan, backscan = analysis.moduleAnalysis(scene)
    analysis.analysis(oct_file, demo.basename, frontscan, backscan)
    # ====================================

    # Nakon analize, pronađi odgovarajući CSV fajl u results folderu
    results_dir = os.path.join(BASE_PATH, 'results')
    # Pronađi bilo koji .csv fajl u results folderu (trebao bi biti samo jedan po strani)
    csv_files = [f for f in os.listdir(results_dir) if f.endswith('.csv')]
    if not csv_files:
        raise FileNotFoundError(f"Nema CSV fajlova u {results_dir}")
    # Uzmi prvi pronađeni CSV fajl
    result_file = os.path.join(results_dir, csv_files[0])
    print(f"Učitavam fajl: {result_file}")
    
    df = pd.read_csv(result_file)
    
    # Ispiši kolone (samo za prvu stranu, da vidimo)
    if side_name == "Southeast":
        print("DEBUG: Kolone u CSV fajlu:", list(df.columns))
        print("DEBUG: Prvih nekoliko redova (Wm2Front, Wm2Back):")
        print(df[['Wm2Front', 'Wm2Back']].head())
    
    front_col = 'Wm2Front' if 'Wm2Front' in df.columns else 'Front'
    back_col = 'Wm2Back' if 'Wm2Back' in df.columns else 'Back'
    
    front_sum = df[front_col].sum()
    back_sum = df[back_col].sum()
    area_one_panel = PANEL_X * PANEL_Y
    # Množimo sa brojem panela jer podaci u CSV-u su za jedan modul (senzor)
    energy_wh = (front_sum + back_sum) * area_one_panel * num_panels
    energy_kwh = energy_wh / 1000
    
    # Ispis prvih nekoliko redova i kolona (samo za prvu stranu)
    if side_name == "Southeast":
        print("DEBUG: Kolone u CSV fajlu:", list(df.columns))
        print("DEBUG: Prvih 5 redova:")
        print(df.head())
    
    # Pretpostavljamo da kolone sadrže riječi 'front' i 'back' (case-insensitive)
    front_col = None
    back_col = None
    for col in df.columns:
        if 'front' in col.lower():
            front_col = col
        if 'back' in col.lower():
            back_col = col
    if front_col is None or back_col is None:
        raise ValueError(f"Nisu pronađene kolone za front/back. Dostupne kolone: {list(df.columns)}")
    
    front_sum = df[front_col].sum()
    back_sum = df[back_col].sum()
    area_one_panel = PANEL_X * PANEL_Y
    # Ovdje množenje sa num_panels - pretpostavka da su podaci po modulu (jednom panelu)
    # Ako je fajl već za cijeli niz, ne množiti. Ali za sada ostavljamo.
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