"""
Cjelogodišnja simulacija solarne ograde (bifacialni paneli)
Lokacija: Bileća / Trebinje (BiH), albedo 0.4 (bijeli kamen)
Konfiguracija: 19 panela (4 SE, 5 SW, 5 NE, 5 NW), nagib 60°
Koristi ispravni TMY EPW fajl sa PVGIS-a.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from bifacial_radiance import RadianceObj, AnalysisObj

# =========================== KONFIGURACIJA ===========================
MAIN_NAME = "sjednica_bileca_irradiance"
BASE_PATH = os.path.abspath(f"./{MAIN_NAME}")
os.makedirs(BASE_PATH, exist_ok=True)

EPW_FILE = os.path.join(os.path.dirname(__file__), "tmy_42.946_18.322_2005_2020.epw")

PANEL_X = 1.134      # m (Canadian Solar – točno 1.134 m)
PANEL_Y = 2.2        # m
BIFACIALITY = 0.75
ALBEDO = 0.4
CLEARANCE = 0.45     # m

# Stvarna električna energija (efikasnost + PR + bifacijalni gain)
EFFICIENCY_PR = 0.21

# Okvir konstrukcije – točno 5.8 m (5 panela = 5.67 m + mali razmak)
FRAME_SIDE = 5.8

SIDES = [
    ("Southeast", 135, 4),
    ("Southwest", 225, 5),
    ("Northeast",  45, 5),
    ("Northwest", 315, 5),
]

# =========================== GLAVNA PETLJA ===========================
results = {}
actual_results = {}

for side_name, azimuth, num_panels in SIDES:
    print(f"\n🚀 Simuliram {side_name} (azimut {azimuth}°, {num_panels} panela)")
    
    demo = RadianceObj(f"{MAIN_NAME}_{side_name}", path=BASE_PATH)
    demo.setGround(ALBEDO)
    
    module = demo.makeModule(
        name=f'panel_{side_name}',
        x=PANEL_X,
        y=PANEL_Y,
        bifi=BIFACIALITY  # type: ignore
    )
    
    if not os.path.exists(EPW_FILE):
        raise FileNotFoundError(f"EPW fajl nije pronađen: {EPW_FILE}. Kopiraj ga u radni folder!")
    
    demo.readWeatherFile(EPW_FILE, coerce_year=2023)
    demo.genCumSky()
    
    scene_dict = {
        'tilt': 60,
        'azimuth': azimuth,
        'nMods': num_panels,
        'nRows': 1,
        'clearance_height': CLEARANCE,
        'pitch': 10.0
    }
    scene = demo.makeScene(module=module, sceneDict=scene_dict)
    oct_file = demo.makeOct(demo.getfilelist())
    
    analysis = AnalysisObj(oct_file, demo.basename)
    frontscan, backscan = analysis.moduleAnalysis(scene)
    analysis.analysis(oct_file, demo.basename, frontscan, backscan)
    
    results_dir = os.path.join(BASE_PATH, 'results')
    csv_files = [f for f in os.listdir(results_dir) if f.endswith('.csv')]
    result_file = os.path.join(results_dir, csv_files[0])
    df = pd.read_csv(result_file)
    
    n_points = len(df)
    front_col = 'Wm2Front' if 'Wm2Front' in df.columns else 'Front'
    back_col = 'Wm2Back' if 'Wm2Back' in df.columns else 'Back'
    
    front_sum = df[front_col].sum()
    back_sum = df[back_col].sum()
    
    avg_front = front_sum / n_points
    avg_back  = back_sum / n_points
    
    area_one = PANEL_X * PANEL_Y
    energy_one_wh = (avg_front + avg_back) * area_one
    total_wh = energy_one_wh * num_panels
    incident_kwh = total_wh / 1000
    
    actual_kwh = incident_kwh * EFFICIENCY_PR
    
    results[side_name] = incident_kwh
    actual_results[side_name] = actual_kwh
    print(f"   ✅ {side_name}: {incident_kwh:8.0f} kWh incidentna → {actual_kwh:6.0f} kWh stvarna")

# =========================== REZULTATI ===========================
print("\n" + "="*80)
print("📊 GODIŠNJA PROIZVODNJA PO STRANAMA")
print("-"*80)
total_incident = 0
total_actual = 0
for side in results:
    inc = results[side]
    act = actual_results[side]
    print(f"  {side:10} : {inc:8.0f} kWh incidentna  |  {act:6.0f} kWh stvarna")
    total_incident += inc
    total_actual += act
print("-"*80)
print(f"  UKUPNO incidentna : {total_incident:8.0f} kWh")
print(f"  UKUPNO stvarna    : {total_actual:8.0f} kWh")
print("="*80)

installed_kwp = 19 * 585 / 1000
print(f"\n📈 Instalisana snaga: 19 × 585 Wp = {installed_kwp:.2f} kWp")
print(f"⚡ Specifična proizvodnja (incidentna): {total_incident / installed_kwp:.0f} kWh/kWp")
print(f"⚡ Specifična proizvodnja (stvarna)   : {total_actual / installed_kwp:.0f} kWh/kWp")
print(f"☀️  Prosječna dnevna proizvodnja (stvarna): {total_actual / 365:.1f} kWh/dan")

# =========================== VIZUALIZACIJA 2D ===========================
plt.figure(figsize=(9,5))
sides = list(results.keys())
incident_values = list(results.values())
actual_values = list(actual_results.values())

x = np.arange(len(sides))
width = 0.35

fig, ax = plt.subplots(figsize=(9,5))
ax.bar(x - width/2, incident_values, width, label='Incidentna energija (kWh)', color=['gold', 'orange', 'lightgreen', 'lightblue'])
ax.bar(x + width/2, actual_values, width, label='Stvarna električna energija (kWh)', color=['darkgoldenrod', 'darkorange', 'forestgreen', 'steelblue'], hatch='//')

ax.set_ylabel('kWh/god')
ax.set_title('Godišnja proizvodnja – incidentna vs. stvarna električna energija', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels(sides)
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.7)

for i, v in enumerate(incident_values):
    ax.text(i - width/2, v + 300, f'{v:,.0f}', ha='center', fontsize=9)
for i, v in enumerate(actual_values):
    ax.text(i + width/2, v + 300, f'{v:,.0f}', ha='center', fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(BASE_PATH, 'proizvodnja_incidentna_vs_stvarna.png'), dpi=150)
plt.show()

plt.figure(figsize=(6,6))
plt.pie(actual_values, labels=sides, autopct='%1.1f%%', startangle=90, colors=['darkgoldenrod', 'darkorange', 'forestgreen', 'steelblue'])
plt.title('Udio pojedine strane u stvarnoj električnoj energiji')
plt.tight_layout()
plt.savefig(os.path.join(BASE_PATH, 'udio_strana_stvarna.png'), dpi=150)
plt.show()

# ==================== ISPRAVLJENA 3D VIZUALIZACIJA ====================
# Razmak za kapiju na SE strani: širina jednog panela (1.134 m)
# Stub samo do 10 m (preglednije)
print("\n🖼️ Generišem KONAČNU 3D vizualizaciju (tilt 60° prema van, kapija širine panela, stub do 10 m)...")

fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')

# Geometrija panela
panel_width = PANEL_X          # 1.134 m
panel_height = PANEL_Y         # 2.2 m
tilt_rad = np.deg2rad(60)
clearance_bottom = 0.5         # donji rub panela

# Visina gornjeg frame-a
z_top = clearance_bottom + panel_height * np.cos(tilt_rad)   # 1.6 m

# Frame: kvadrat zakrenut 45°, stranica 5.8 m
frame_side = 5.8
frame_half_diag = frame_side / np.sqrt(2)   # 4.101 m
frame_apothem = frame_side / 2.0            # 2.9 m

# Horizontalni pomak donjeg ruba prema VAN
horiz_offset = panel_height * np.sin(tilt_rad)   # 1.905 m

# Betonska baza 7×7 m
base_side = 7.0
base_half_diag = base_side / np.sqrt(2)     # 4.95 m

# Strane
side_data = {
    "Southeast": {"az": 135, "n": 4, "color": "gold"},
    "Southwest": {"az": 225, "n": 5, "color": "orange"},
    "Northeast": {"az":  45, "n": 5, "color": "lightgreen"},
    "Northwest": {"az": 315, "n": 5, "color": "lightblue"},
}

# Crtanje panela
for side_name, data in side_data.items():
    az_rad = np.deg2rad(data["az"])
    n_panels = data["n"]
    color = data["color"]
    
    along_rad = az_rad + np.pi/2
    norm_x = np.cos(az_rad)
    norm_y = np.sin(az_rad)
    along_x = np.cos(along_rad)
    along_y = np.sin(along_rad)
    
    mid_top_x = frame_apothem * norm_x
    mid_top_y = frame_apothem * norm_y
    
    if side_name == "Southeast":
        # 4 panela sa razmakom u sredini tačno širine jednog panela
        panel_width = PANEL_X
        gap_width = panel_width   # razmak za kapiju = širina jednog panela
        total_panels_width = 4 * panel_width
        total_width = total_panels_width + gap_width   # = 5.67 m
        # Preostali prostor na frame-u (5.8 - 5.67 = 0.13 m) ravnomjerno dodajemo sa strane
        side_margin = (frame_side - total_width) / 2.0   # ~0.065 m
        
        # Položaj lijeve grupe (2 panela)
        left_group_start = mid_top_x - (total_width/2) * along_x + side_margin * along_x
        left_group_start_y = mid_top_y - (total_width/2) * along_y + side_margin * along_y
        for i in range(2):
            top_x = left_group_start + i * panel_width * along_x
            top_y = left_group_start_y + i * panel_width * along_y
            top_z = z_top
            bottom_x = top_x + horiz_offset * norm_x
            bottom_y = top_y + horiz_offset * norm_y
            bottom_z = clearance_bottom
            p1 = (bottom_x, bottom_y, bottom_z)
            p2 = (bottom_x + panel_width * along_x, bottom_y + panel_width * along_y, bottom_z)
            p3 = (top_x + panel_width * along_x, top_y + panel_width * along_y, top_z)
            p4 = (top_x, top_y, top_z)
            xs = [p1[0], p2[0], p3[0], p4[0], p1[0]]
            ys = [p1[1], p2[1], p3[1], p4[1], p1[1]]
            zs = [p1[2], p2[2], p3[2], p4[2], p1[2]]
            ax.plot(xs, ys, zs, color=color, linewidth=3, alpha=0.95)
        
        # Desna grupa (2 panela) – pomjerena za gap + širina lijeve grupe
        right_group_start = left_group_start + (2 * panel_width + gap_width) * along_x
        right_group_start_y = left_group_start_y + (2 * panel_width + gap_width) * along_y
        for i in range(2):
            top_x = right_group_start + i * panel_width * along_x
            top_y = right_group_start_y + i * panel_width * along_y
            top_z = z_top
            bottom_x = top_x + horiz_offset * norm_x
            bottom_y = top_y + horiz_offset * norm_y
            bottom_z = clearance_bottom
            p1 = (bottom_x, bottom_y, bottom_z)
            p2 = (bottom_x + panel_width * along_x, bottom_y + panel_width * along_y, bottom_z)
            p3 = (top_x + panel_width * along_x, top_y + panel_width * along_y, top_z)
            p4 = (top_x, top_y, top_z)
            xs = [p1[0], p2[0], p3[0], p4[0], p1[0]]
            ys = [p1[1], p2[1], p3[1], p4[1], p1[1]]
            zs = [p1[2], p2[2], p3[2], p4[2], p1[2]]
            ax.plot(xs, ys, zs, color=color, linewidth=3, alpha=0.95)
    
    else:
        # Ostale strane: 5 panela bez razmaka
        total_len = n_panels * panel_width
        half_len = total_len / 2.0
        start_x = mid_top_x - half_len * along_x
        start_y = mid_top_y - half_len * along_y
        for i in range(n_panels):
            top_x = start_x + i * panel_width * along_x
            top_y = start_y + i * panel_width * along_y
            top_z = z_top
            bottom_x = top_x + horiz_offset * norm_x
            bottom_y = top_y + horiz_offset * norm_y
            bottom_z = clearance_bottom
            p1 = (bottom_x, bottom_y, bottom_z)
            p2 = (bottom_x + panel_width * along_x, bottom_y + panel_width * along_y, bottom_z)
            p3 = (top_x + panel_width * along_x, top_y + panel_width * along_y, top_z)
            p4 = (top_x, top_y, top_z)
            xs = [p1[0], p2[0], p3[0], p4[0], p1[0]]
            ys = [p1[1], p2[1], p3[1], p4[1], p1[1]]
            zs = [p1[2], p2[2], p3[2], p4[2], p1[2]]
            ax.plot(xs, ys, zs, color=color, linewidth=3, alpha=0.95)

# Gornji frame
frame_vertices = np.array([
    [0,  frame_half_diag, z_top],
    [ frame_half_diag, 0, z_top],
    [0, -frame_half_diag, z_top],
    [-frame_half_diag, 0, z_top],
    [0,  frame_half_diag, z_top]
])
ax.plot(frame_vertices[:,0], frame_vertices[:,1], frame_vertices[:,2],
        color='darkred', linewidth=5, label=f'Gornji frame {frame_side} m')

# Betonska baza
base_vertices = np.array([
    [0,  base_half_diag, 0],
    [ base_half_diag, 0, 0],
    [0, -base_half_diag, 0],
    [-base_half_diag, 0, 0],
    [0,  base_half_diag, 0]
])
ax.plot(base_vertices[:,0], base_vertices[:,1], base_vertices[:,2],
        color='gray', linewidth=4, alpha=0.8, label='Betonska baza 7×7 m')

# ========== STUB SAMO DO 10 m (detaljno) ==========
max_height = 10.0   # prikazujemo samo do 10 m
tower_width = 1.5
tower_half = tower_width / 2

# Vertikalne šipke (uglovi)
for x, y in [(-tower_half, -tower_half), ( tower_half, -tower_half),
             ( tower_half,  tower_half), (-tower_half,  tower_half)]:
    ax.plot([x, x], [y, y], [0, max_height], color='black', linewidth=2)

# Horizontalne prečage (svakih 1 m)
for z in np.arange(1, max_height, 1):
    pts = np.array([[ -tower_half, -tower_half, z],
                    [  tower_half, -tower_half, z],
                    [  tower_half,  tower_half, z],
                    [ -tower_half,  tower_half, z],
                    [ -tower_half, -tower_half, z]])
    ax.plot(pts[:,0], pts[:,1], pts[:,2], color='black', linewidth=1.5)

# Dijagonalne ukrštene šipke (X) na svakoj strani
for z_start in np.arange(0, max_height-0.5, 1):
    z_end = z_start + 1
    # Strana 0-1 (y = -hw)
    ax.plot([-tower_half, tower_half], [-tower_half, -tower_half], [z_start, z_end], color='gray', linewidth=1)
    ax.plot([ tower_half, -tower_half], [-tower_half, -tower_half], [z_start, z_end], color='gray', linewidth=1)
    # Strana 1-2 (x = +hw)
    ax.plot([ tower_half,  tower_half], [-tower_half, tower_half], [z_start, z_end], color='gray', linewidth=1)
    ax.plot([ tower_half,  tower_half], [ tower_half, -tower_half], [z_start, z_end], color='gray', linewidth=1)
    # Strana 2-3 (y = +hw)
    ax.plot([ tower_half, -tower_half], [ tower_half,  tower_half], [z_start, z_end], color='gray', linewidth=1)
    ax.plot([-tower_half,  tower_half], [ tower_half,  tower_half], [z_start, z_end], color='gray', linewidth=1)
    # Strana 3-0 (x = -hw)
    ax.plot([-tower_half, -tower_half], [ tower_half, -tower_half], [z_start, z_end], color='gray', linewidth=1)
    ax.plot([-tower_half, -tower_half], [-tower_half,  tower_half], [z_start, z_end], color='gray', linewidth=1)

# Centralna vertikalna linija (jezgro) – takođe samo do 10 m
ax.plot([0, 0], [0, 0], [0, max_height], color='black', linewidth=1, linestyle='dashed', alpha=0.5)

# Ograničenje Z ose na 10 m radi preglednosti
ax.set_zlim(0, 11)

# Ose i izgled
ax.set_xlabel('X (istok) [m]')
ax.set_ylabel('Y (sjever) [m]')
ax.set_zlabel('Z (visina) [m]')
ax.set_title('3D model solarne ograde – KONAČNA VERZIJA\n'
             'Tilt 60° prema van • Kapija širine panela na SE • Stub prikazan do 10 m',
             fontsize=12)
ax.view_init(elev=28, azim=-55)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend()

plt.tight_layout()
plt.savefig(os.path.join(BASE_PATH, '3D_solarna_ograda_final.png'), dpi=300)
plt.show()

print("\n✅ Konačna vizualizacija:")
print("   - SE strana: razmak za kapiju tačno širine jednog panela (1.134 m).")
print("   - Stub prikazan samo do visine 10 m (preglednije).")
print("   - Paneli naginju prema van (tilt 60°, donji rub na 0.5 m).")
print("   - Gornji frame i baza usklađeni (vrh na sjeveru).")