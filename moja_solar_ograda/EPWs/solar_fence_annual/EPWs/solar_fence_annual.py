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

# --- PUTANJA DO EPW FAJLA ---
EPW_FILE = r"E:\Radiance_build\moja_solar_ograda\EPWs\SRB_Podgorica.134620_IWEC.epw"

# --- DIMENZIJE PANELA (m) ---
PANEL_X = 1.134
PANEL_Y = 2.2
BIFACIALITY = 0.75
ALBEDO = 0.4

# --- STRANE OGRADE: (naziv, azimut, broj panela) ---
SIDES = [
    ("Southeast", 135, 4),
    ("Southwest", 225, 5),
    ("Northeast",  45, 5),
    ("Northwest", 315, 5),
]

# =========================== SIMULACIJA ===========================
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

    # Generiši nebo za cijelu godinu
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

    analysis = AnalysisObj(oct_file, demo.basename)
    result = analysis.moduleAnalysis(scene)   # result je rječnik

    # DEBUG: Ispiši strukturu result
    print("DEBUG: tip result =", type(result))
    if isinstance(result, dict):
        print("DEBUG: ključevi =", list(result.keys()))
        for k, v in result.items():
            print(f"  Ključ '{k}' -> tip: {type(v)}")
            if hasattr(v, 'shape'):
                print(f"      oblik: {v.shape}")
            elif isinstance(v, dict):
                print(f"      podključevi: {list(v.keys())}")
    else:
        print("DEBUG: result nije dict, već", type(result))

    # Inteligentno izvlačenje podataka
    if isinstance(result, dict):
        # Pokušaj pronaći DataFrame sa front/back zračenjem
        # Prvo provjeri da li postoje 'Wm2Front' i 'Wm2Back'
        if 'Wm2Front' in result and 'Wm2Back' in result:
            front = result['Wm2Front']
            back = result['Wm2Back']
        elif 'front' in result and 'back' in result:
            front = result['front']
            back = result['back']
        else:
            # Možda su pod ključem 'combined' ili slično
            # Ako nema, uzmi prvi ključ koji sadrži DataFrame
            front = None
            back = None
            for k, v in result.items():
                if isinstance(v, pd.DataFrame):
                    if front is None:
                        front = v
                    else:
                        back = v
                        break
            if front is None:
                raise ValueError("Ne mogu pronaći DataFrame sa rezultatima u rječniku.")
    else:
        # Ako je tuple (starija verzija)
        front, back = result

    # Ako su front i back DataFrame, izračunaj sumu
    if isinstance(front, pd.DataFrame) and isinstance(back, pd.DataFrame):
        area_one_panel = PANEL_X * PANEL_Y
        front_sum = front.sum().sum()
        back_sum = back.sum().sum()
        energy_wh = (front_sum + back_sum) * area_one_panel * num_panels
        energy_kwh = energy_wh / 1000
    else:
        print(f"Upozorenje: front i back nisu DataFrame. front tip: {type(front)}, back tip: {type(back)}")
        energy_kwh = 0

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