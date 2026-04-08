import os
import pandas as pd
from bifacial_radiance import RadianceObj, AnalysisObj

# ========== 1. KONFIGURACIJA ==========
MAIN_NAME = "solar_fence_fixed"
BASE_PATH = os.path.abspath(f"./{MAIN_NAME}")
os.makedirs(BASE_PATH, exist_ok=True)

# --- PUTANJA DO EPW FAJLA (ZAMIJENITE SA VAŠOM) ---
# Molim Vas, provjerite da li je ova putanja apsolutno tačna.
# Fajl se zove: SRB_Podgorica.134620_IWEC.epw
EPW_FILE = r"E:\Radiance_build\moja_solar_ograda\EPWs\SRB_Podgorica.134620_IWEC.epw"

# --- DIMENZIJE PANELA (u metrima) ---
PANEL_X = 1.134
PANEL_Y = 2.2
BIFACIALITY = 0.75   # Ovdje koristimo decimalni broj (float)
ALBEDO = 0.4

# --- STRANE OGRADE: (naziv, azimut, broj panela) ---
SIDES = [
    ("Southeast", 135, 4),  # Ulaz
    ("Southwest", 225, 5),
    ("Northeast",  45, 5),
    ("Northwest", 315, 5),
]

# ========== 2. SIMULACIJA ZA SVAKU STRANU ==========
total_kwh = 0.0
for side_name, azimuth, num_panels in SIDES:
    print(f"\n--- Simuliram {side_name} (az={azimuth}°, {num_panels} panela) ---")

    # 2.1 Kreiranje novog objekta za svaku stranu
    demo = RadianceObj(f"{MAIN_NAME}_{side_name}", path=BASE_PATH)
    demo.setGround(ALBEDO)

    # 2.2 Definicija modula
    module = demo.makeModule(
        name=f'panel_{side_name}',
        x=PANEL_X,
        y=PANEL_Y,
        bifi=BIFACIALITY
    )

    # 2.3 Učitavanje vremenskih podataka
    if not os.path.exists(EPW_FILE):
        raise FileNotFoundError(f"EPW fajl nije pronađen: {EPW_FILE}")
    
    # metdata je objekat koji sadrži sve vremenske podatke
    metdata = demo.readWeatherFile(EPW_FILE, coerce_year=2023)

    # ========== OVO JE KLJUČNA IZMJENA ==========
    # Pristupamo indeksu DataFrame-a 'weather' unutar metdata objekta
    # Taj indeks sadrži sve vremenske oznake (npr. '2023-01-01 00:30:00').
    time_index = metdata.weather.index
    
    # Definišemo željeni datum i vrijeme (21. jun u podne)
    target_time = pd.to_datetime('2023-06-21 12:00:00')
    
    # Pronalazimo numerički indeks koji je najbliži našem željenom vremenu
    # Ovo je broj koji gendaylit očekuje.
    try:
        # Ovo je najpouzdaniji način u novijim verzijama
        idx = time_index.get_indexer([target_time], method='nearest')[0]
    except AttributeError:
        # Ako prvi metod ne uspije, koristimo argmin za pronalaženje najbližeg indeksa
        idx = (time_index - target_time).abs().argmin()
    
    # Pokrećemo gendaylit sa našim metdata objektom i pronađenim indeksom
    demo.gendaylit(metdata, idx)
    # ===============================================

    # 2.4 Kreiranje scene
    scene_dict = {
        'tilt': 60,
        'azimuth': azimuth,
        'nMods': num_panels,
        'nRows': 1,
        'clearance_height': 0.5,
        'pitch': 10.0
    }
    scene = demo.makeScene(module=module, sceneDict=scene_dict)

    # 2.5 Kreiranje .oct fajla
    oct_file = demo.makeOct(demo.getfilelist())

    # 2.6 Pokretanje analize
    analysis = AnalysisObj(oct_file, demo.basename)
    frontscan, backscan = analysis.moduleAnalysis(scene)

    # 2.7 Izračun proizvodnje za dati dan
    front_wm2 = frontscan['Wm2Front'].sum() if 'Wm2Front' in frontscan else frontscan.iloc[:,0].sum()
    back_wm2  = backscan['Wm2Back'].sum()   if 'Wm2Back'  in backscan  else backscan.iloc[:,0].sum()

    area_one_panel = PANEL_X * PANEL_Y
    energy_wh_day = (front_wm2 + back_wm2) * area_one_panel * num_panels
    energy_kwh_day = energy_wh_day / 1000
    total_kwh += energy_kwh_day

    print(f"  ➜ {side_name}: {energy_kwh_day:.1f} kWh za 21. jun")

# ========== 3. REZULTATI ==========
print("\n" + "="*50)
print(f"🌞 UKUPNO za sve strane 21. juna: {total_kwh:.1f} kWh")
print("Napomena: Ovo je proizvodnja za JEDAN DAN (21. jun u podne).")
print("="*50)