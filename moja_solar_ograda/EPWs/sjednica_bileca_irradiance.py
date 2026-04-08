import os
import pandas as pd
from bifacial_radiance import RadianceObj, AnalysisObj
from tqdm import tqdm
import time

# ========== KONFIGURACIJA ==========
MAIN_NAME = "sjednica_bileca"
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
    ("Northeast", 45, 5),
    ("Northwest", 315, 5),
]

# ========== FUNKCIJA ZA JEDNU STRANU ==========
def simulate_side(side_name, azimuth, num_panels):
    print(f"\n🚀 Simuliram {side_name} (az={azimuth}°, {num_panels} panela)")
    
    demo = RadianceObj(f"{MAIN_NAME}_{side_name}", path=BASE_PATH)
    demo.setGround(ALBEDO)
    module = demo.makeModule(name=f'panel_{side_name}', x=PANEL_X, y=PANEL_Y, bifi=BIFACIALITY)
    
    metdata = demo.readWeatherFile(EPW_FILE, coerce_year=2023)
    time_index = metdata.tmydata.index
    ghi = metdata.tmydata['ghi']  # kolona se zove 'ghi'
    
    total_front = 0.0
    total_back = 0.0
    hours = 0
    
    for idx, ts in enumerate(tqdm(time_index, desc=side_name)):
        # Preskoči noć (GHI < 10 W/m2)
        if ghi.iloc[idx] < 10:
            continue
        
        demo.gendaylit(idx)
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
        frontscan, backscan = analysis.moduleAnalysis(scene)
        # Ovo kreira CSV fajl u results folderu
        analysis.analysis(oct_file, demo.basename, frontscan, backscan)
        
        # Sačekaj malo da se fajl upiše (do 2 sekunde)
        results_dir = os.path.join(BASE_PATH, 'results')
        csv_file = None
        for _ in range(10):
            csv_files = [f for f in os.listdir(results_dir) if f.endswith('.csv')]
            if csv_files:
                csv_file = csv_files[0]
                break
            time.sleep(0.2)
        if csv_file is None:
            raise RuntimeError(f"CSV nije kreiran za sat {idx} (strana {side_name})")
        
        df = pd.read_csv(os.path.join(results_dir, csv_file))
        # Kolone mogu biti 'Wm2Front', 'Front' ili slično
        front_col = 'Wm2Front' if 'Wm2Front' in df.columns else df.columns[6]  # probaj indeks
        back_col = 'Wm2Back' if 'Wm2Back' in df.columns else df.columns[7]
        total_front += df[front_col].sum()
        total_back += df[back_col].sum()
        hours += 1
        
        # Očisti fajlove da ne bi napunili disk
        os.remove(os.path.join(results_dir, csv_file))
        if os.path.exists(oct_file):
            os.remove(oct_file)
    
    area = PANEL_X * PANEL_Y
    energy_wh = (total_front + total_back) * area * num_panels
    energy_kwh = energy_wh / 1000
    print(f"   ✅ {side_name}: {energy_kwh:.0f} kWh (obrađeno {hours} sati)")
    return energy_kwh

# ========== GLAVNA PETLJA ==========
results = {}
for name, az, n in SIDES:
    results[name] = simulate_side(name, az, n)

# ========== REZULTATI ==========
print("\n" + "="*60)
print("📊 GODIŠNJA PROIZVODNJA PO STRANAMA")
print("-"*60)
total = sum(results.values())
for name, kwh in results.items():
    print(f"  {name:10} : {kwh:8.0f} kWh")
print("-"*60)
print(f"  UKUPNO    : {total:8.0f} kWh")
print("="*60)

installed_kwp = 19 * 585 / 1000
print(f"\n📈 Instalisana snaga: 19 × 585 Wp = {installed_kwp:.2f} kWp")
print(f"⚡ Specifična proizvodnja: {total / installed_kwp:.0f} kWh/kWp")
print(f"☀️  Prosječna dnevna proizvodnja: {total / 365:.1f} kWh/dan")