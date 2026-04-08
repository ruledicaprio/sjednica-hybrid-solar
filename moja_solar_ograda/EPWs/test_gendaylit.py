import os
import pandas as pd
from bifacial_radiance import RadianceObj, AnalysisObj

# Kreiraj folder za test
test_folder = "./test_run"
os.makedirs(test_folder, exist_ok=True)

demo = RadianceObj("test_gendaylit", path=test_folder)
demo.setGround(0.4)

# Definiši modul
module = demo.makeModule(name='test_panel', x=1.134, y=2.2, bifi=0.75)

# Učitaj EPW fajl
epw_file = r"E:\Radiance_build\moja_solar_ograda\EPWs\SRB_Podgorica.134620_IWEC.epw"
if not os.path.exists(epw_file):
    raise FileNotFoundError(f"EPW fajl nije pronađen: {epw_file}")
metdata = demo.readWeatherFile(epw_file, coerce_year=2023)

# Pristupi tmydata DataFrame-u
time_index = metdata.tmydata.index
print(f"Vremenska zona indeksa: {time_index.tz}")

# Napravi ciljno vrijeme svjesno vremenske zone
target_time = pd.to_datetime('2023-06-21 12:00:00')
if time_index.tz is not None:
    target_time = target_time.tz_localize(time_index.tz)
else:
    # Ako nema zone, ostavi kako jeste
    pass

# Pronađi najbliži indeks
idx = time_index.get_indexer([target_time], method='nearest')[0]
print(f"Odabrani indeks: {idx}, vrijeme: {time_index[idx]}")

# Generiši nebo za taj sat
demo.gendaylit(idx)

# Napravi scenu (jedan panel)
scene_dict = {'tilt': 60, 'azimuth': 135, 'nMods': 1, 'nRows': 1, 'clearance_height': 0.5, 'pitch': 10}
scene = demo.makeScene(module=module, sceneDict=scene_dict)

oct_file = demo.makeOct(demo.getfilelist())
analysis = AnalysisObj(oct_file, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(scene)

print("Front Wm2 sum:", frontscan['Wm2Front'].sum())
print("Back Wm2 sum:", backscan['Wm2Back'].sum())