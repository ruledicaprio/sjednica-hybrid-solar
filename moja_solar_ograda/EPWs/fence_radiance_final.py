"""
KONAČNA SIMULACIJA I VIZUALIZACIJA – SOLARNA OGRADA SA PLATFORMOM
Lokacija: SJEDNICA, BILECA
Nagib panela: maksimalni dozvoljeni PREMA VAN (16°) – donji rub unutar betonske baze 7×7 m
Toranj: piramidalni, sužava se od baze (dijag. 5,67 m) do platforme (3×3 m, nezakrenuta)
Paneli: puna boja, crne ivice (tehnički crtež)
Izvještaj: PDF (bez pptx)
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from bifacial_radiance import RadianceObj, AnalysisObj
import warnings
warnings.filterwarnings("ignore")
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime

# =========================== KONFIGURACIJA ===========================
MAIN_NAME = "sjednica_bileca_irradiance_outward_max"
BASE_PATH = os.path.abspath(f"./{MAIN_NAME}")
os.makedirs(BASE_PATH, exist_ok=True)

EPW_FILE = os.path.join(os.path.dirname(__file__), "tmy_42.946_18.322_2005_2020.epw")

PANEL_X = 1.134          # m
PANEL_Y = 2.2            # m
BIFACIALITY = 0.75
ALBEDO = 0.4
CLEARANCE = 0.5          # donji rub panela

FRAME_SIDE = 5.8         # gornji metalni frame
BASE_SIDE = 7.0          # betonska baza

# Maksimalni nagib prema van (izračunat)
max_sin = (BASE_SIDE/2 - FRAME_SIDE/2) / PANEL_Y
TILT_DEG = np.rad2deg(np.arcsin(max_sin))
TILT_DEG = 16.0

# Strane (azimut normale – prema van)
SIDES = [
    ("Southeast", 135, 4),
    ("Southwest", 225, 5),
    ("Northeast",  45, 5),
    ("Northwest", 315, 5),
]

EFFICIENCY_PR = 0.21

# =========================== SIMULACIJA ===========================
results = {}
actual_results = {}
hourly_data = {}

for side_name, azimuth, num_panels in SIDES:
    print(f"\n🚀 Simuliram {side_name} (azimut {azimuth}°, {num_panels} panela, tilt {TILT_DEG}°)")
    
    demo = RadianceObj(f"{MAIN_NAME}_{side_name}", path=BASE_PATH)
    demo.setGround(ALBEDO)
    
    module = demo.makeModule(
        name=f'panel_{side_name}',
        x=PANEL_X,
        y=PANEL_Y,
        bifi=float(BIFACIALITY)
    )
    
    if not os.path.exists(EPW_FILE):
        raise FileNotFoundError(f"EPW fajl nije pronađen: {EPW_FILE}")
    
    demo.readWeatherFile(EPW_FILE, coerce_year=2023)
    demo.genCumSky()
    
    scene_dict = {
        'tilt': TILT_DEG,
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
    
    front_col = next((col for col in df.columns if 'front' in col.lower()), None)
    back_col = next((col for col in df.columns if 'back' in col.lower()), None)
    if front_col is None or back_col is None:
        raise KeyError(f"Nisu pronađene kolone za prednju/stražnju stranu u {result_file}")
    
    front_sum = df[front_col].sum()
    back_sum = df[back_col].sum()
    n_points = len(df)
    avg_front = front_sum / n_points
    avg_back  = back_sum / n_points
    
    area_one = PANEL_X * PANEL_Y
    energy_one_wh = (avg_front + avg_back) * area_one
    total_wh = energy_one_wh * num_panels
    incident_kwh = total_wh / 1000
    actual_kwh = incident_kwh * EFFICIENCY_PR
    
    results[side_name] = incident_kwh
    actual_results[side_name] = actual_kwh
    
    # Vremenski podaci
    if 'Time' in df.columns:
        df['Time'] = pd.to_datetime(df['Time'])
        df['Year'] = df['Time'].dt.year
        df['Month'] = df['Time'].dt.month
        df['Day'] = df['Time'].dt.day
        df['Hour'] = df['Time'].dt.hour
        df['total_W'] = (df[front_col] + df[back_col]) * area_one * num_panels
        hourly_data[side_name] = df[['Year', 'Month', 'Day', 'Hour', 'total_W']].copy()
    
    print(f"   ✅ {side_name}: {incident_kwh:8.0f} kWh incidentna → {actual_kwh:6.0f} kWh stvarna")

# =========================== REZULTATI ===========================
print("\n" + "="*80)
print("📊 GODIŠNJA PROIZVODNJA PO STRANAMA – SJEDNICA, BILECA")
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

# =========================== GRAFIKONI ===========================
sides = list(results.keys())
incident_values = list(results.values())
actual_values = list(actual_results.values())
x = np.arange(len(sides))
width = 0.35

fig1, ax1 = plt.subplots(figsize=(9,5))
ax1.bar(x - width/2, incident_values, width, label='Incidentna energija (kWh)', color=['gold', 'orange', 'lightgreen', 'lightblue'])
ax1.bar(x + width/2, actual_values, width, label='Stvarna električna energija (kWh)', color=['darkgoldenrod', 'darkorange', 'forestgreen', 'steelblue'], hatch='//')
ax1.set_ylabel('kWh/god')
ax1.set_title('SJEDNICA, BILECA – Godišnja proizvodnja solarne ograde\n(incidentna vs. stvarna električna energija)', fontsize=14)
ax1.set_xticks(x)
ax1.set_xticklabels(sides)
ax1.legend()
ax1.grid(axis='y', linestyle='--', alpha=0.7)
for i, v in enumerate(incident_values):
    ax1.text(i - width/2, v + 300, f'{v:,.0f}', ha='center', fontsize=9)
for i, v in enumerate(actual_values):
    ax1.text(i + width/2, v + 300, f'{v:,.0f}', ha='center', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(BASE_PATH, 'SJEDNICA_BILECA_proizvodnja_po_stranama.png'), dpi=150)
plt.show()

fig2, ax2 = plt.subplots(figsize=(6,6))
ax2.pie(actual_values, labels=sides, autopct='%1.1f%%', startangle=90, colors=['darkgoldenrod', 'darkorange', 'forestgreen', 'steelblue'])
ax2.set_title('SJEDNICA, BILECA – Udio pojedine strane u stvarnoj električnoj energiji')
plt.tight_layout()
plt.savefig(os.path.join(BASE_PATH, 'SJEDNICA_BILECA_udio_strana.png'), dpi=150)
plt.show()

# Kumulativna i mjesečna (ako ima satnih podataka)
if hourly_data:
    all_hourly = pd.concat(hourly_data.values(), ignore_index=True)
    all_hourly = all_hourly.sort_values(['Year', 'Month', 'Day', 'Hour'])
    all_hourly['cumulative_kWh'] = all_hourly['total_W'].cumsum() / 1000
    fig3, ax3 = plt.subplots(figsize=(10,6))
    ax3.plot(all_hourly.index, all_hourly['cumulative_kWh'], color='green', linewidth=2)
    ax3.set_xlabel('Vremenski korak (sat)')
    ax3.set_ylabel('Kumulativna energija (kWh)')
    ax3.set_title('SJEDNICA, BILECA – Kumulativna godišnja proizvodnja')
    ax3.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_PATH, 'SJEDNICA_BILECA_kumulativna.png'), dpi=150)
    plt.show()
    
    monthly = all_hourly.groupby('Month')['total_W'].sum() / 1000
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
    monthly.index = months
    fig4, ax4 = plt.subplots(figsize=(10,6))
    ax4.bar(months, monthly, color='skyblue', edgecolor='navy')
    ax4.set_title('SJEDNICA, BILECA – Mjesečna proizvodnja električne energije (kWh)')
    ax4.set_ylabel('kWh')
    ax4.set_xlabel('Mjesec')
    ax4.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_PATH, 'SJEDNICA_BILECA_mjesecna_proizvodnja.png'), dpi=150)
    plt.show()

# =========================== 3D VIZUALIZACIJA ===========================
print("\n🖼️ Generišem 3D vizualizaciju...")
fig5 = plt.figure(figsize=(12, 9))
ax = fig5.add_subplot(111, projection='3d')

panel_width = PANEL_X
panel_height = PANEL_Y
tilt_rad = np.deg2rad(TILT_DEG)
clearance_bottom = CLEARANCE
z_top = clearance_bottom + panel_height * np.cos(tilt_rad)
horiz_offset = panel_height * np.sin(tilt_rad)

frame_half_diag = FRAME_SIDE / np.sqrt(2)
frame_apothem = FRAME_SIDE / 2.0
base_half_diag = BASE_SIDE / np.sqrt(2)

side_data = {
    "Southeast": {"az": 135, "n": 4, "color": "gold"},
    "Southwest": {"az": 225, "n": 5, "color": "orange"},
    "Northeast": {"az":  45, "n": 5, "color": "lightgreen"},
    "Northwest": {"az": 315, "n": 5, "color": "lightblue"},
}

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
    total_len = n_panels * panel_width
    
    if side_name == "Southeast":
        gap_width = panel_width
        margin = (FRAME_SIDE - (4*panel_width + gap_width)) / 2.0
        half_total = (4*panel_width + gap_width) / 2.0
        start_left = mid_top_x - (half_total - margin) * along_x
        start_left_y = mid_top_y - (half_total - margin) * along_y
        for i in range(2):
            top_x = start_left + i * panel_width * along_x
            top_y = start_left_y + i * panel_width * along_y
            top_z = z_top
            bottom_x = top_x + horiz_offset * norm_x
            bottom_y = top_y + horiz_offset * norm_y
            bottom_z = clearance_bottom
            p1 = (bottom_x, bottom_y, bottom_z); p2 = (bottom_x + panel_width*along_x, bottom_y + panel_width*along_y, bottom_z)
            p3 = (top_x + panel_width*along_x, top_y + panel_width*along_y, top_z); p4 = (top_x, top_y, top_z)
            xs = [p1[0], p2[0], p3[0], p4[0], p1[0]]
            ys = [p1[1], p2[1], p3[1], p4[1], p1[1]]
            zs = [p1[2], p2[2], p3[2], p4[2], p1[2]]
            ax.plot(xs, ys, zs, color=color, linewidth=2, alpha=1.0)
            ax.plot(xs, ys, zs, color='black', linewidth=0.5, alpha=0.5)
        start_right = start_left + (2*panel_width + gap_width) * along_x
        start_right_y = start_left_y + (2*panel_width + gap_width) * along_y
        for i in range(2):
            top_x = start_right + i * panel_width * along_x
            top_y = start_right_y + i * panel_width * along_y
            top_z = z_top
            bottom_x = top_x + horiz_offset * norm_x
            bottom_y = top_y + horiz_offset * norm_y
            bottom_z = clearance_bottom
            p1 = (bottom_x, bottom_y, bottom_z); p2 = (bottom_x + panel_width*along_x, bottom_y + panel_width*along_y, bottom_z)
            p3 = (top_x + panel_width*along_x, top_y + panel_width*along_y, top_z); p4 = (top_x, top_y, top_z)
            xs = [p1[0], p2[0], p3[0], p4[0], p1[0]]
            ys = [p1[1], p2[1], p3[1], p4[1], p1[1]]
            zs = [p1[2], p2[2], p3[2], p4[2], p1[2]]
            ax.plot(xs, ys, zs, color=color, linewidth=2, alpha=1.0)
            ax.plot(xs, ys, zs, color='black', linewidth=0.5, alpha=0.5)
    else:
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
            p1 = (bottom_x, bottom_y, bottom_z); p2 = (bottom_x + panel_width*along_x, bottom_y + panel_width*along_y, bottom_z)
            p3 = (top_x + panel_width*along_x, top_y + panel_width*along_y, top_z); p4 = (top_x, top_y, top_z)
            xs = [p1[0], p2[0], p3[0], p4[0], p1[0]]
            ys = [p1[1], p2[1], p3[1], p4[1], p1[1]]
            zs = [p1[2], p2[2], p3[2], p4[2], p1[2]]
            ax.plot(xs, ys, zs, color=color, linewidth=2, alpha=1.0)
            ax.plot(xs, ys, zs, color='black', linewidth=0.5, alpha=0.5)

frame_vertices = np.array([[0, frame_half_diag, z_top], [frame_half_diag, 0, z_top], [0, -frame_half_diag, z_top], [-frame_half_diag, 0, z_top], [0, frame_half_diag, z_top]])
ax.plot(frame_vertices[:,0], frame_vertices[:,1], frame_vertices[:,2], color='darkred', linewidth=5, label=f'Gornji frame {FRAME_SIDE} m')
base_vertices = np.array([[0, base_half_diag, 0], [base_half_diag, 0, 0], [0, -base_half_diag, 0], [-base_half_diag, 0, 0], [0, base_half_diag, 0]])
ax.plot(base_vertices[:,0], base_vertices[:,1], base_vertices[:,2], color='gray', linewidth=4, alpha=0.8, label=f'Betonska baza {BASE_SIDE}×{BASE_SIDE} m')

# Piramidalni toranj
tower_base_halfdiag = 5.67 / 2.0
tower_top_halfdiag = 1.5
platform_z = 4.2
tower_height = 10.0
def get_radius(z):
    if z <= platform_z:
        t = z / platform_z
        return tower_base_halfdiag * (1 - t) + tower_top_halfdiag * t
    else:
        return tower_top_halfdiag
base_points = [(0, tower_base_halfdiag), (tower_base_halfdiag, 0), (0, -tower_base_halfdiag), (-tower_base_halfdiag, 0)]
top_points = [(0, tower_top_halfdiag), (tower_top_halfdiag, 0), (0, -tower_top_halfdiag), (-tower_top_halfdiag, 0)]
for (x0, y0), (x1, y1) in zip(base_points, top_points):
    ax.plot([x0, x1], [y0, y1], [0, tower_height], color='black', linewidth=2)
for z in np.arange(1, tower_height, 1):
    r = get_radius(z)
    pts = np.array([[0, r, z], [r, 0, z], [0, -r, z], [-r, 0, z], [0, r, z]])
    ax.plot(pts[:,0], pts[:,1], pts[:,2], color='gray', linewidth=1, alpha=0.7)
for z_start in np.arange(0, tower_height-0.5, 1):
    z_end = z_start + 1
    r_start = get_radius(z_start)
    r_end = get_radius(z_end)
    A_start, B_start, C_start, D_start = (0, r_start), (r_start, 0), (0, -r_start), (-r_start, 0)
    A_end, B_end, C_end, D_end = (0, r_end), (r_end, 0), (0, -r_end), (-r_end, 0)
    ax.plot([A_start[0], B_end[0]], [A_start[1], B_end[1]], [z_start, z_end], color='black', linewidth=1, alpha=0.7)
    ax.plot([B_start[0], A_end[0]], [B_start[1], A_end[1]], [z_start, z_end], color='black', linewidth=1, alpha=0.7)
    ax.plot([B_start[0], C_end[0]], [B_start[1], C_end[1]], [z_start, z_end], color='black', linewidth=1, alpha=0.7)
    ax.plot([C_start[0], B_end[0]], [C_start[1], B_end[1]], [z_start, z_end], color='black', linewidth=1, alpha=0.7)
    ax.plot([C_start[0], D_end[0]], [C_start[1], D_end[1]], [z_start, z_end], color='black', linewidth=1, alpha=0.7)
    ax.plot([D_start[0], C_end[0]], [D_start[1], C_end[1]], [z_start, z_end], color='black', linewidth=1, alpha=0.7)
    ax.plot([D_start[0], A_end[0]], [D_start[1], A_end[1]], [z_start, z_end], color='black', linewidth=1, alpha=0.7)
    ax.plot([A_start[0], D_end[0]], [A_start[1], D_end[1]], [z_start, z_end], color='black', linewidth=1, alpha=0.7)
ax.plot([0,0], [0,0], [0, tower_height], color='black', linewidth=1, linestyle='dashed', alpha=0.5)

platform_half = 1.5
platform_corners = np.array([[-platform_half, -platform_half, platform_z], [platform_half, -platform_half, platform_z], [platform_half, platform_half, platform_z], [-platform_half, platform_half, platform_z], [-platform_half, -platform_half, platform_z]])
ax.plot(platform_corners[:,0], platform_corners[:,1], platform_corners[:,2], color='blue', linewidth=3, label='Platforma 3×3 m na 4,2 m')
verts = [list(zip(platform_corners[:-1,0], platform_corners[:-1,1], platform_corners[:-1,2]))]
platform_face = Poly3DCollection(verts, alpha=0.3, color='cyan')
ax.add_collection3d(platform_face)

ax.set_xlabel('X (istok) [m]')
ax.set_ylabel('Y (sjever) [m]')
ax.set_zlabel('Z (visina) [m]')
ax.set_title(f'SJEDNICA, BILECA – 3D model solarne ograde\nNagib panela {TILT_DEG:.1f}° prema van, piramidalni stub, platforma 3×3 m', fontsize=12)
ax.view_init(elev=28, azim=-55)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='upper right')
plt.tight_layout()
output_image = os.path.join(BASE_PATH, 'SJEDNICA_BILECA_3D_sa_platformom.png')
plt.savefig(output_image, dpi=300)
plt.show()

# ==================== DODATAK: BOČNI PRIKAZI I AUTONOMIJA ====================
print("\n📸 Generišem bočne prikaze (East i North view)...")

# Ponovo kreiramo 3D scenu (možemo iskoristiti već postavljenu fig5, ali da ne petljamo, napravimo nove)
fig_east = plt.figure(figsize=(10, 8))
ax_east = fig_east.add_subplot(111, projection='3d')
# Kopiramo crtanje panela, frame-a, baze, tornja i platforme (isti kod kao ranije, ali sa view_init)
# Da ne duplamo kod, najlakše je ponovo pozvati funkciju, ali pošto nemamo funkciju, ponovićemo crtanje.
# Ipak, da skripta ne bude preduga, iskoristićemo već postavljene objekte? Nije jednostavno.
# Zbog preglednosti, napravit ćemo posebne figure koristeći isti kod za crtanje (kopirati iz 3D dijela).
# Umjesto kopiranja, možemo sačuvati 3D model iz prethodne figure i samo promijeniti ugao? Ne može se naknadno mijenjati.
# Zato ćemo ponovo iscrtati za svaki prikaz (malo duže ali pouzdano).

def draw_3d_model(ax):
    # Isti kod za crtanje panela, frame-a, baze, tornja i platforme
    panel_width = PANEL_X
    panel_height = PANEL_Y
    tilt_rad = np.deg2rad(TILT_DEG)
    clearance_bottom = CLEARANCE
    z_top = clearance_bottom + panel_height * np.cos(tilt_rad)
    horiz_offset = panel_height * np.sin(tilt_rad)
    frame_half_diag = FRAME_SIDE / np.sqrt(2)
    frame_apothem = FRAME_SIDE / 2.0
    base_half_diag = BASE_SIDE / np.sqrt(2)
    
    side_data = {
        "Southeast": {"az": 135, "n": 4, "color": "gold"},
        "Southwest": {"az": 225, "n": 5, "color": "orange"},
        "Northeast": {"az":  45, "n": 5, "color": "lightgreen"},
        "Northwest": {"az": 315, "n": 5, "color": "lightblue"},
    }
    
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
        total_len = n_panels * panel_width
        
        if side_name == "Southeast":
            gap_width = panel_width
            margin = (FRAME_SIDE - (4*panel_width + gap_width)) / 2.0
            half_total = (4*panel_width + gap_width) / 2.0
            start_left = mid_top_x - (half_total - margin) * along_x
            start_left_y = mid_top_y - (half_total - margin) * along_y
            for i in range(2):
                top_x = start_left + i * panel_width * along_x
                top_y = start_left_y + i * panel_width * along_y
                top_z = z_top
                bottom_x = top_x + horiz_offset * norm_x
                bottom_y = top_y + horiz_offset * norm_y
                bottom_z = clearance_bottom
                p1 = (bottom_x, bottom_y, bottom_z); p2 = (bottom_x + panel_width*along_x, bottom_y + panel_width*along_y, bottom_z)
                p3 = (top_x + panel_width*along_x, top_y + panel_width*along_y, top_z); p4 = (top_x, top_y, top_z)
                xs = [p1[0], p2[0], p3[0], p4[0], p1[0]]
                ys = [p1[1], p2[1], p3[1], p4[1], p1[1]]
                zs = [p1[2], p2[2], p3[2], p4[2], p1[2]]
                ax.plot(xs, ys, zs, color=color, linewidth=2, alpha=1.0)
                ax.plot(xs, ys, zs, color='black', linewidth=0.5, alpha=0.5)
            start_right = start_left + (2*panel_width + gap_width) * along_x
            start_right_y = start_left_y + (2*panel_width + gap_width) * along_y
            for i in range(2):
                top_x = start_right + i * panel_width * along_x
                top_y = start_right_y + i * panel_width * along_y
                top_z = z_top
                bottom_x = top_x + horiz_offset * norm_x
                bottom_y = top_y + horiz_offset * norm_y
                bottom_z = clearance_bottom
                p1 = (bottom_x, bottom_y, bottom_z); p2 = (bottom_x + panel_width*along_x, bottom_y + panel_width*along_y, bottom_z)
                p3 = (top_x + panel_width*along_x, top_y + panel_width*along_y, top_z); p4 = (top_x, top_y, top_z)
                xs = [p1[0], p2[0], p3[0], p4[0], p1[0]]
                ys = [p1[1], p2[1], p3[1], p4[1], p1[1]]
                zs = [p1[2], p2[2], p3[2], p4[2], p1[2]]
                ax.plot(xs, ys, zs, color=color, linewidth=2, alpha=1.0)
                ax.plot(xs, ys, zs, color='black', linewidth=0.5, alpha=0.5)
        else:
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
                p1 = (bottom_x, bottom_y, bottom_z); p2 = (bottom_x + panel_width*along_x, bottom_y + panel_width*along_y, bottom_z)
                p3 = (top_x + panel_width*along_x, top_y + panel_width*along_y, top_z); p4 = (top_x, top_y, top_z)
                xs = [p1[0], p2[0], p3[0], p4[0], p1[0]]
                ys = [p1[1], p2[1], p3[1], p4[1], p1[1]]
                zs = [p1[2], p2[2], p3[2], p4[2], p1[2]]
                ax.plot(xs, ys, zs, color=color, linewidth=2, alpha=1.0)
                ax.plot(xs, ys, zs, color='black', linewidth=0.5, alpha=0.5)
    
    frame_vertices = np.array([[0, frame_half_diag, z_top], [frame_half_diag, 0, z_top], [0, -frame_half_diag, z_top], [-frame_half_diag, 0, z_top], [0, frame_half_diag, z_top]])
    ax.plot(frame_vertices[:,0], frame_vertices[:,1], frame_vertices[:,2], color='darkred', linewidth=5)
    base_vertices = np.array([[0, base_half_diag, 0], [base_half_diag, 0, 0], [0, -base_half_diag, 0], [-base_half_diag, 0, 0], [0, base_half_diag, 0]])
    ax.plot(base_vertices[:,0], base_vertices[:,1], base_vertices[:,2], color='gray', linewidth=4, alpha=0.8)
    
    tower_base_halfdiag = 5.67 / 2.0
    tower_top_halfdiag = 1.5
    platform_z = 4.2
    tower_height = 10.0
    def get_radius(z):
        if z <= platform_z:
            t = z / platform_z
            return tower_base_halfdiag * (1 - t) + tower_top_halfdiag * t
        else:
            return tower_top_halfdiag
    base_points = [(0, tower_base_halfdiag), (tower_base_halfdiag, 0), (0, -tower_base_halfdiag), (-tower_base_halfdiag, 0)]
    top_points = [(0, tower_top_halfdiag), (tower_top_halfdiag, 0), (0, -tower_top_halfdiag), (-tower_top_halfdiag, 0)]
    for (x0, y0), (x1, y1) in zip(base_points, top_points):
        ax.plot([x0, x1], [y0, y1], [0, tower_height], color='black', linewidth=2)
    for z in np.arange(1, tower_height, 1):
        r = get_radius(z)
        pts = np.array([[0, r, z], [r, 0, z], [0, -r, z], [-r, 0, z], [0, r, z]])
        ax.plot(pts[:,0], pts[:,1], pts[:,2], color='gray', linewidth=1, alpha=0.7)
    for z_start in np.arange(0, tower_height-0.5, 1):
        z_end = z_start + 1
        r_start = get_radius(z_start)
        r_end = get_radius(z_end)
        A_start, B_start, C_start, D_start = (0, r_start), (r_start, 0), (0, -r_start), (-r_start, 0)
        A_end, B_end, C_end, D_end = (0, r_end), (r_end, 0), (0, -r_end), (-r_end, 0)
        ax.plot([A_start[0], B_end[0]], [A_start[1], B_end[1]], [z_start, z_end], color='black', linewidth=1, alpha=0.7)
        ax.plot([B_start[0], A_end[0]], [B_start[1], A_end[1]], [z_start, z_end], color='black', linewidth=1, alpha=0.7)
        ax.plot([B_start[0], C_end[0]], [B_start[1], C_end[1]], [z_start, z_end], color='black', linewidth=1, alpha=0.7)
        ax.plot([C_start[0], B_end[0]], [C_start[1], B_end[1]], [z_start, z_end], color='black', linewidth=1, alpha=0.7)
        ax.plot([C_start[0], D_end[0]], [C_start[1], D_end[1]], [z_start, z_end], color='black', linewidth=1, alpha=0.7)
        ax.plot([D_start[0], C_end[0]], [D_start[1], C_end[1]], [z_start, z_end], color='black', linewidth=1, alpha=0.7)
        ax.plot([D_start[0], A_end[0]], [D_start[1], A_end[1]], [z_start, z_end], color='black', linewidth=1, alpha=0.7)
        ax.plot([A_start[0], D_end[0]], [A_start[1], D_end[1]], [z_start, z_end], color='black', linewidth=1, alpha=0.7)
    ax.plot([0,0], [0,0], [0, tower_height], color='black', linewidth=1, linestyle='dashed', alpha=0.5)
    
    platform_half = 1.5
    platform_corners = np.array([[-platform_half, -platform_half, platform_z], [platform_half, -platform_half, platform_z], [platform_half, platform_half, platform_z], [-platform_half, platform_half, platform_z], [-platform_half, -platform_half, platform_z]])
    ax.plot(platform_corners[:,0], platform_corners[:,1], platform_corners[:,2], color='blue', linewidth=3)
    verts = [list(zip(platform_corners[:-1,0], platform_corners[:-1,1], platform_corners[:-1,2]))]
    platform_face = Poly3DCollection(verts, alpha=0.3, color='cyan')
    ax.add_collection3d(platform_face)
    ax.set_xlabel('X (istok) [m]')
    ax.set_ylabel('Y (sjever) [m]')
    ax.set_zlabel('Z (visina) [m]')
    ax.grid(True, linestyle='--', alpha=0.5)

# East view (gledano sa istoka: azim=90, elev=0)
fig_east = plt.figure(figsize=(10, 8))
ax_east = fig_east.add_subplot(111, projection='3d')
draw_3d_model(ax_east)
ax_east.view_init(elev=0, azim=90)
ax_east.set_title('Pogled sa istoka (East view)')
plt.tight_layout()
east_image = os.path.join(BASE_PATH, 'SJEDNICA_BILECA_pogled_istok.png')
plt.savefig(east_image, dpi=150)
plt.close(fig_east)

# North view (gledano sa sjevera: azim=0, elev=0)
fig_north = plt.figure(figsize=(10, 8))
ax_north = fig_north.add_subplot(111, projection='3d')
draw_3d_model(ax_north)
ax_north.view_init(elev=0, azim=0)
ax_north.set_title('Pogled sa sjevera (North view)')
plt.tight_layout()
north_image = os.path.join(BASE_PATH, 'SJEDNICA_BILECA_pogled_sjever.png')
plt.savefig(north_image, dpi=150)
plt.close(fig_north)

print("✅ Bočni prikazi sačuvani.")

# ==================== PROCJENA AUTONOMIJE ZA TELEKOM OPREMU (sa i bez RAN) ====================
print("\n🔋 Računam autonomiju sistema za telekomunikacionu opremu – uporedna analiza...")

# Scenario 1: Sa RAN opremom (RRU potrošači)
loads_full = {
    "CISCO ASR 920 Router": {"voltage": 48, "current": 3.1, "power": 150},
    "BTS 5900 (3x RRU)": {"voltage": 48, "current": 25, "power": 1200},
    "Ostali RRU linkovi": {"voltage": 48, "current": 1, "power": 48},
    "Klimatizacija MTS kabineta": {"voltage": 48, "current": 17, "power": 816}
}
total_power_full_w = sum(load['power'] for load in loads_full.values())
daily_consumption_full_kwh = total_power_full_w * 24 / 1000

# Scenario 2: Bez RAN opreme (samo router i klima)
loads_basic = {
    "CISCO ASR 920 Router": {"voltage": 48, "current": 3.1, "power": 150},
    "Klimatizacija MTS kabineta": {"voltage": 48, "current": 17, "power": 816}
}
total_power_basic_w = sum(load['power'] for load in loads_basic.values())
daily_consumption_basic_kwh = total_power_basic_w * 24 / 1000

solar_daily_kwh = total_actual / 365
battery_capacity_kwh = 43.2

deficit_full_kwh = max(0, daily_consumption_full_kwh - solar_daily_kwh)
deficit_basic_kwh = max(0, daily_consumption_basic_kwh - solar_daily_kwh)

autonomy_full_hours = battery_capacity_kwh / total_power_full_w * 1000
autonomy_basic_hours = battery_capacity_kwh / total_power_basic_w * 1000

print(f"\n📊 UPOREDNA ANALIZA:")
print(f"Scenario sa RAN opremom: dnevna potrošnja = {daily_consumption_full_kwh:.1f} kWh, deficit = {deficit_full_kwh:.1f} kWh/dan")
print(f"Scenario bez RAN opreme: dnevna potrošnja = {daily_consumption_basic_kwh:.1f} kWh, deficit = {deficit_basic_kwh:.1f} kWh/dan")
print(f"Autonomija sa RAN: {autonomy_full_hours:.1f} h, bez RAN: {autonomy_basic_hours:.1f} h")

# =========================== PDF IZVJEŠTAJ (sa uporednom analizom) ===========================
print("\n📄 Generišem PDF izvještaj...")
pdf_path = os.path.join(BASE_PATH, 'SJEDNICA_BILECA_izvjestaj.pdf')
with PdfPages(pdf_path) as pdf:
    # ----- NASLOVNA (ista) -----
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.text(0.5, 0.7, 'SJEDNICA, BILECA – SOLARNA OGRADA', fontsize=22, ha='center', weight='bold')
    fig.text(0.5, 0.6, f'Godišnji izvještaj o proizvodnji električne energije\n{datetime.now().strftime("%d.%m.%Y")}', fontsize=14, ha='center')
    fig.text(0.5, 0.4, f'Ukupna stvarna proizvodnja: {total_actual:.0f} kWh/god', fontsize=16, ha='center')
    fig.text(0.5, 0.35, f'Instalisana snaga: 11.12 kWp', fontsize=14, ha='center')
    fig.text(0.5, 0.3, f'Specifična proizvodnja: {total_actual / installed_kwp:.0f} kWh/kWp', fontsize=14, ha='center')
    fig.text(0.5, 0.25, f'Prosječna dnevna proizvodnja: {total_actual / 365:.1f} kWh/dan', fontsize=14, ha='center')
    pdf.savefig(fig); plt.close(fig)
    
    # ----- GRAFIKONI (godišnji) -----
    fig = plt.figure(figsize=(11.69, 8.27))
    ax1 = fig.add_subplot(2,1,1)
    ax1.bar(x - width/2, incident_values, width, label='Incidentna energija (kWh)', color=['gold', 'orange', 'lightgreen', 'lightblue'])
    ax1.bar(x + width/2, actual_values, width, label='Stvarna električna energija (kWh)', color=['darkgoldenrod', 'darkorange', 'forestgreen', 'steelblue'], hatch='//')
    ax1.set_ylabel('kWh/god'); ax1.set_title('Godišnja proizvodnja po stranama'); ax1.set_xticks(x); ax1.set_xticklabels(sides); ax1.legend(); ax1.grid(axis='y', linestyle='--', alpha=0.7)
    ax2 = fig.add_subplot(2,1,2)
    ax2.pie(actual_values, labels=sides, autopct='%1.1f%%', startangle=90, colors=['darkgoldenrod', 'darkorange', 'forestgreen', 'steelblue'])
    ax2.set_title('Udio pojedine strane u stvarnoj energiji')
    pdf.savefig(fig); plt.close(fig)
    
    # ----- 3D MODEL -----
    if os.path.exists(output_image):
        fig = plt.figure(figsize=(11.69, 8.27))
        plt.imshow(plt.imread(output_image)); plt.axis('off'); plt.title('3D model solarne ograde (crveni paneli, nosači, ulaz)')
        pdf.savefig(fig); plt.close(fig)
    
    # ----- BOČNI PRIKAZI (svaki na posebnoj stranici) -----
    if os.path.exists(east_image):
        fig = plt.figure(figsize=(11.69, 8.27))
        plt.imshow(plt.imread(east_image)); plt.axis('off'); plt.title('Pogled sa istoka (East view) – paneli na nosačima 0.5 m od tla')
        pdf.savefig(fig); plt.close(fig)
    if os.path.exists(north_image):
        fig = plt.figure(figsize=(11.69, 8.27))
        plt.imshow(plt.imread(north_image)); plt.axis('off'); plt.title('Pogled sa sjevera (North view)')
        pdf.savefig(fig); plt.close(fig)
    
    # ----- TEHNIČKI PODACI I SOFTVER (ista) -----
    fig = plt.figure(figsize=(11.69, 8.27))
    ax = fig.add_subplot(111); ax.axis('off')
    try:
        import bifacial_radiance
        br_version = bifacial_radiance.__version__
    except:
        br_version = 'instaliran (nepoznata verzija)'
    text = f"""KORIŠTENI SOFTVER I PAKETI ZA SIMULACIJU:
• bifacial_radiance: {br_version}
• Radiance (ray tracing engine) – poziva se kroz bifacial_radiance
• Python: {sys.version.split()[0]}
• NumPy, Pandas, Matplotlib

ULAZNI PODACI:
• EPW fajl: tmy_42.946_18.322_2005_2020.epw (PVGIS TMY)
• Albedo: 0.4 (bijeli kamen)
• Bifacijalnost panela: 0.75
• Efikasnost sistema (PR): 0.21
• Nagib panela: 16° prema van (maksimalno dozvoljen)
• Visina donjeg ruba: 0.5 m
• Gornji frame: 5,8 m (kvadrat zakrenut 45°)
• Betonska baza: 7×7 m (kvadrat zakrenut 45°)
• Platforma za održavanje: 3×3 m na visini 4,2 m (nezakrenuta)

REZULTATI SIMULACIJE:
• Ukupna stvarna godišnja energija: {total_actual:.0f} kWh
• Specifična proizvodnja: {total_actual / installed_kwp:.0f} kWh/kWp
• Instalisana snaga: 11,12 kWp (19 × 585 Wp)
• Prosječna dnevna proizvodnja: {total_actual / 365:.1f} kWh/dan

PREPORUČENA OPREMA:
• MPPT kontroler: Huawei SUN2000-15KTL-M5 (15 kW)
• MTS kabinet: Huawei MTS9510A ili MTS9300A serija
• Baterije: 6 × ESM-48150A3 (LiFePO₄, 48V, 150Ah) → ukupno 43,2 kWh

EKONOMSKI POKAZATELJI (procjena):
• Godišnja ušteda na struji (0,10 EUR/kWh): {total_actual * 0.10:.0f} EUR
• Smanjenje CO₂ emisije (0,5 kg/kWh): {total_actual * 0.5 / 1000:.1f} tona/god
• Jednostavan period povrata (bez subvencija): 6–8 godina

Datum izrade izvještaja: {datetime.now().strftime("%d.%m.%Y %H:%M")}
"""
    ax.text(0.05, 0.95, text, transform=ax.transAxes, fontsize=9, verticalalignment='top', fontfamily='monospace')
    pdf.savefig(fig); plt.close(fig)
    
    # ----- UPOREDNA ANALIZA AUTONOMIJE (sa i bez RAN) -----
    fig_comp = plt.figure(figsize=(11.69, 8.27))
    ax = fig_comp.add_subplot(111)
    ax.axis('off')
    
    comp_text = f"""
================================================================================
         UPOREDNA ANALIZA AUTONOMIJE: SA RAN OPREMOM (RRU) I BEZ NJE
================================================================================

| Parametar                                | Sa RAN opremom | Bez RAN opreme |
|------------------------------------------|----------------|----------------|
| Ukupna vršna snaga (W)                   | {total_power_full_w:.0f}             | {total_power_basic_w:.0f}              |
| Dnevna potrošnja (kWh/dan)               | {daily_consumption_full_kwh:.1f}             | {daily_consumption_basic_kwh:.1f}              |
| Prosječna dnevna proizvodnja (kWh/dan)   | {solar_daily_kwh:.1f}             | {solar_daily_kwh:.1f}              |
| Dnevni deficit (kWh/dan)                 | {deficit_full_kwh:.1f}             | {deficit_basic_kwh:.1f}              |
| Kapacitet baterija (kWh)                 | {battery_capacity_kwh:.1f}             | {battery_capacity_kwh:.1f}              |
| Teorijska autonomija (sati)              | {autonomy_full_hours:.1f}             | {autonomy_basic_hours:.1f}              |
| Teorijska autonomija (dani)              | {autonomy_full_hours/24:.1f}             | {autonomy_basic_hours/24:.1f}              |
================================================================================

ZAKLJUČCI:
• Uključivanjem RAN opreme (RRU), dnevna potrošnja raste za {daily_consumption_full_kwh - daily_consumption_basic_kwh:.1f} kWh.
• Deficit energije pri korištenju RAN opreme iznosi {deficit_full_kwh:.1f} kWh/dan, što znači da baterije ne mogu pokriti potrošnju.
• Bez RAN opreme, deficit je {deficit_basic_kwh:.1f} kWh/dan – sistem je blizu uravnoteženja.
• Autonomija bez RAN opreme je {autonomy_basic_hours:.1f} h ({autonomy_basic_hours/24:.1f} dana), što je značajno duže nego sa RAN ({autonomy_full_hours:.1f} h).

PREPORUKE:
✅ Za rad sa RAN opremom neophodno je:
   - Povećati baterijski kapacitet na minimalno 64.8 kWh (9 baterija)
   - Dodati 2-3 dodatna solarna panela (povećati snagu na ~14 kWp)
✅ Za rad bez RAN opreme (samo router i klima) postojeći sistem je marginalan, ali bi mogao funkcionisati uz povremeno pražnjenje baterija.
✅ Ugraditi inteligentno upravljanje opterećenjem koje isključuje RRU jedinice pri niskom nivou baterije.

Napomena: Gore navedeni proračuni su teorijski. U realnim uslovima, autonomija će biti manja zbog gubitaka, starenja baterija i neidealnih vremenskih uslova.
================================================================================
"""
    ax.text(0.05, 0.95, comp_text, transform=ax.transAxes, fontsize=9, verticalalignment='top', fontfamily='monospace')
    pdf.savefig(fig_comp)
    plt.close(fig_comp)

print(f"\n✅ PDF izvještaj sačuvan: {pdf_path}")

print(f"✅ PDF izvještaj sačuvan: {pdf_path}")
print(f"\n📁 Svi rezultati spremljeni u: {BASE_PATH}")
print("   - Godišnja proizvodnja po stranama: SJEDNICA_BILECA_proizvodnja_po_stranama.png")
print("   - Udio po stranama: SJEDNICA_BILECA_udio_strana.png")
if hourly_data:
    print("   - Kumulativna proizvodnja: SJEDNICA_BILECA_kumulativna.png")
    print("   - Mjesečna proizvodnja: SJEDNICA_BILECA_mjesecna_proizvodnja.png")
print(f"   - 3D model: {output_image}")
print(f"   - PDF izvještaj: {pdf_path}")
print("\n✅ Simulacija, vizualizacija i izvještaj završeni.")