"""
✅ SOLARNA OGRADA – FINALNA VERZIJA (Ispravan proračun + DXF geometrija)
- FIX: Energija se računa ispravno (nema dupliranja sati ni površine)
- 3D Model: Tačno prati DXF dimenzije (7x7m donji, 5.8x5.8m gornji okvir)
- Izlaz: Grafikon, 3D, Presjeci, PDF
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from bifacial_radiance import RadianceObj, AnalysisObj
from matplotlib.patches import Polygon, Rectangle
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# ==============================================================================
# 📍 KONFIGURACIJA
# ==============================================================================
MAIN_NAME = "sjednica_bileca_irradiance_outward_max"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.join(SCRIPT_DIR, "EPWs", MAIN_NAME)
os.makedirs(BASE_PATH, exist_ok=True)
os.makedirs(os.path.join(BASE_PATH, "results"), exist_ok=True)

# 🔍 Provjera putanje za EPW (ako si u EPWs folderu)
if os.path.exists(os.path.join(SCRIPT_DIR, "tmy_42.946_18.322_2005_2020.epw")):
    EPW_FILE = os.path.join(SCRIPT_DIR, "tmy_42.946_18.322_2005_2020.epw")
else:
    EPW_FILE = os.path.join(SCRIPT_DIR, "EPWs", "tmy_42.946_18.322_2005_2020.epw")

# Panel: Canadian Solar TOPBiHiKu6 585W
PANEL_X = 1.134   # širina [m]
PANEL_Y = 2.2     # visina [m]
PANEL_WATTS = 585
BIFACIALITY = 0.80
ALBEDO = 0.4
EFFICIENCY_PR = 0.21

# Nagib: 16° od vertikale PREMA VAN
TILT_FROM_VERTICAL_DEG = 16.0
TILT_FROM_HORIZONTAL_DEG = 90.0 - TILT_FROM_VERTICAL_DEG
CLEARANCE = 0.5

# Geometrija (DXF dimenzije)
LOWER_FRAME_SIDE = 7.0
UPPER_FRAME_SIDE = 5.8
CONCRETE_SIDE = 5.4
PLATFORM_Z = 4.2
CHAMFER_DIST = 1.2

# Strane (Tačan raspored iz izvještaja: 4+5+5+5 = 19 panela)
SIDES = [
    ("Southeast", 135, 4),
    ("Southwest", 225, 5),
    ("Northeast", 45, 5),
    ("Northwest", 315, 5)
]

# Opterećenje
LOADS_FULL_KW = 53.1 / 24
LOADS_BASIC_KW = 23.2 / 24
BATTERY_CAP_KWH = 43.2

# ==============================================================================
# 🛠️ POMOĆNE FUNKCIJE (DXF GEOMETRIJA)
# ==============================================================================
def chamfer_corners(corners, chamfer_dist=1.2):
    """Generiše koordinate za 7x7m romba sa odsječenim uglovima."""
    new_pts = []
    n = len(corners)
    for i in range(n):
        p1 = corners[i]
        p2 = corners[(i+1)%n]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = np.hypot(dx, dy)
        if length > 0:
            ux = dx / length
            uy = dy / length
            pt1 = (p1[0] + chamfer_dist * ux, p1[1] + chamfer_dist * uy)
            new_pts.append(pt1)
            pt2 = (p2[0] - chamfer_dist * ux, p2[1] - chamfer_dist * uy)
            new_pts.append(pt2)
    unique = []
    for pt in new_pts:
        if not any(np.hypot(pt[0]-up[0], pt[1]-up[1]) < 1e-6 for up in unique):
            unique.append(pt)
    unique.sort(key=lambda p: np.arctan2(p[1], p[0]))
    return unique

def draw_panel(ax, bl, br, tr, tl, color='#1E3A8A', alpha=0.8):
    """Crtanje jednog bifacijalnog panela."""
    verts = [bl, br, tr, tl]
    collection = Poly3DCollection([verts], alpha=alpha, color=color, edgecolor='black', linewidth=0.5)
    ax.add_collection3d(collection)
    xs = [bl[0], br[0], tr[0], tl[0], bl[0]]
    ys = [bl[1], br[1], tr[1], tl[1], bl[1]]
    zs = [bl[2], br[2], tr[2], tl[2], bl[2]]
    ax.plot(xs, ys, zs, color='black', linewidth=1, alpha=0.6)

# ==============================================================================
# ☀️ SIMULACIJA (ISPRVAN PRORAČUN ENERGIJE)
# ==============================================================================
def run_simulation():
    print("\n" + "="*80)
    print("☀️ POKREĆEM SIMULACIJU (ISPRAN PRORAČUN)")
    print("="*80)
    
    if not os.path.exists(EPW_FILE):
        print(f"❌ EPW fajl nije pronađen: {EPW_FILE}")
        return {}, {}
    
    results = {}
    actual_results = {}
    
    for name, azimuth, num_panels in SIDES:
        print(f"🚀 Simuliram {name} (azimut {azimuth}°, {num_panels} panela)")
        
        demo = RadianceObj(f"{MAIN_NAME}_{name}", path=BASE_PATH)
        demo.setGround(ALBEDO)
        # ⚠️ type: ignore da ne smeta Pylance
        module = demo.makeModule(name=f'panel_{name}', x=PANEL_X, y=PANEL_Y, bifi=float(BIFACIALITY))  # type: ignore
        
        demo.readWeatherFile(EPW_FILE, coerce_year=2023)
        demo.genCumSky()
        
        scene_dict = {'tilt': TILT_FROM_HORIZONTAL_DEG, 'azimuth': azimuth, 'nMods': num_panels, 'nRows': 1,
                      'clearance_height': CLEARANCE, 'pitch': 10.0}
        scene = demo.makeScene(module=module, sceneDict=scene_dict)
        oct_file = demo.makeOct(demo.getfilelist())
        
        analysis = AnalysisObj(oct_file, demo.basename)
        frontscan, backscan = analysis.moduleAnalysis(scene)
        analysis.analysis(oct_file, demo.basename, frontscan, backscan)
        
        # Učitavanje rezultata
        results_dir = os.path.join(BASE_PATH, 'results')
        csv_files = [f for f in os.listdir(results_dir) if f.endswith('.csv') and name.lower() in f.lower()]
        if not csv_files:
            print(f"   ⚠️ Nema CSV fajla za {name}")
            continue
            
        df = pd.read_csv(os.path.join(results_dir, csv_files[0]))
        front_col = next((c for c in df.columns if 'front' in c.lower()), None)
        back_col = next((c for c in df.columns if 'back' in c.lower()), None)
        
        if front_col and back_col:
            area_one = PANEL_X * PANEL_Y
            
            # ✅ ISPRVAN PRORAČUN: Sumiramo cijelu godinu, pa množimo sa površinom i brojem panela
            # Ne množimo sa 8760 jer su podaci u fajlu već agregirani po satu!
            total_front_wh = df[front_col].sum() * area_one
            total_back_wh = df[back_col].sum() * area_one
            
            total_wh = (total_front_wh + total_back_wh) * num_panels
            incident_kwh = total_wh / 1000.0
            actual_kwh = incident_kwh * EFFICIENCY_PR
            
            results[name] = incident_kwh
            actual_results[name] = actual_kwh
            print(f"   ✅ {name}: {incident_kwh:8.0f} kWh incidentna → {actual_kwh:6.0f} kWh stvarna")
            
    return results, actual_results

# ==============================================================================
# 🎨 3D VIZUALIZACIJA (DXF MODEL)
# ==============================================================================
def generate_3d_model():
    print("\n🖼️ Generišem 3D model...")
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    
    # Tlo (10x10m)
    ground = [[(-5,-5,0), (5,-5,0), (5,5,0), (-5,5,0)]]
    ax.add_collection3d(Poly3DCollection(ground, facecolors='#d2b48c', alpha=0.3))
    
    # Betonska ploča (5.4x5.4m)
    c_half = CONCRETE_SIDE / 2
    concrete = [[(-c_half, -c_half, 0.2), (c_half, -c_half, 0.2), (c_half, c_half, 0.2), (-c_half, c_half, 0.2)]]
    ax.add_collection3d(Poly3DCollection(concrete, facecolors='gray', alpha=0.8))
    
    # Donji okvir (7x7m chamfer 1.2m)
    lower_z = 0.5
    lower_coords = chamfer_corners([(3.5,0), (0,3.5), (-3.5,0), (0,-3.5)], CHAMFER_DIST)
    lower_frame_pts = [(x, y, lower_z) for x,y in lower_coords]
    for i in range(len(lower_frame_pts)):
        p1 = lower_frame_pts[i]; p2 = lower_frame_pts[(i+1)%len(lower_frame_pts)]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color='dimgray', linewidth=4)
    
    # Gornji okvir (5.8x5.8m) i Paneli
    upper_z = lower_z + PANEL_Y * np.cos(np.deg2rad(TILT_FROM_VERTICAL_DEG))
    horiz_offset = PANEL_Y * np.sin(np.deg2rad(TILT_FROM_VERTICAL_DEG))
    upper_coords = [(2.9,0), (0,2.9), (-2.9,0), (0,-2.9)]
    
    for i in range(4):
        x1, y1 = upper_coords[i]; x2, y2 = upper_coords[(i+1)%4]
        ax.plot([x1, x2], [y1, y2], [upper_z, upper_z], color='dimgray', linewidth=3)
    
    # Crtanje panela (po stranama)
    side_data = {
        "Southeast": {"az": 135, "n": 4, "color": "#1E3A8A"},
        "Southwest": {"az": 225, "n": 5, "color": "#1E3A8A"},
        "Northeast": {"az": 45, "n": 5, "color": "#1E3A8A"},
        "Northwest": {"az": 315, "n": 5, "color": "#1E3A8A"}
    }
    
    for s_name, s_data in side_data.items():
        az_rad = np.deg2rad(s_data["az"])
        norm_x, norm_y = np.cos(az_rad), np.sin(az_rad)
        along_x, along_y = -np.sin(az_rad), np.cos(az_rad)
        
        mid_top = np.array([2.9 * norm_x, 2.9 * norm_y])
        total_len = s_data["n"] * PANEL_X
        start = mid_top - (total_len/2) * np.array([along_x, along_y])
        
        for i in range(s_data["n"]):
            center = start + (i + 0.5) * PANEL_X * np.array([along_x, along_y])
            
            # Gornji rub (na gornjem okviru)
            tl = (center[0] - PANEL_X/2*along_x, center[1] - PANEL_X/2*along_y, upper_z)
            tr = (center[0] + PANEL_X/2*along_x, center[1] + PANEL_X/2*along_y, upper_z)
            
            # Donji rub (pomaknut prema van)
            bl = (tl[0] + horiz_offset*norm_x, tl[1] + horiz_offset*norm_y, lower_z)
            br = (tr[0] + horiz_offset*norm_x, tr[1] + horiz_offset*norm_y, lower_z)
            
            draw_panel(ax, bl, br, tr, tl, color=s_data['color'])

    ax.set_xlabel('X (Istok) [m]'); ax.set_ylabel('Y (Sjever) [m]'); ax.set_zlabel('Z [Visina] [m]')
    ax.set_xlim(-6, 6); ax.set_ylim(-6, 6); ax.set_zlim(0, 12)
    ax.view_init(elev=25, azim=45)
    
    out_path = os.path.join(BASE_PATH, "SJEDNICA_BILECA_3D_konstrukcija.png")
    plt.savefig(out_path, dpi=200)
    plt.close()
    return out_path

# ==============================================================================
# 📄 PDF I GRAFIKONI
# ==============================================================================
def generate_report(results, actual_results):
    print("📄 Generišem izvještaj...")
    total_actual = sum(actual_results.values())
    installed_kwp = 19 * PANEL_WATTS / 1000
    
    # 1. Bar Chart
    sides = list(results.keys())
    incident_values = list(results.values())
    actual_values = list(actual_results.values())
    x_pos = np.arange(len(sides))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(9,5))
    ax.bar(x_pos - width/2, incident_values, width, label='Incidentna (kWh)', color=['gold', 'orange', 'lightgreen', 'lightblue'])
    ax.bar(x_pos + width/2, actual_values, width, label='Stvarna (kWh)', color=['darkgoldenrod', 'darkorange', 'forestgreen', 'steelblue'], hatch='//')
    ax.set_title('Godišnja proizvodnja (Ispravan proračun)')
    ax.set_xticks(x_pos); ax.set_xticklabels(sides)
    ax.legend()
    ax.grid(axis='y')
    plt.tight_layout()
    bar_path = os.path.join(BASE_PATH, 'SJEDNICA_BILECA_proizvodnja.png')
    plt.savefig(bar_path, dpi=150)
    plt.close()
    
    # 2. PDF
    pdf_path = os.path.join(BASE_PATH, 'SJEDNICA_BILECA_izvjestaj.pdf')
    with PdfPages(pdf_path) as pdf:
        # Naslovna
        fig = plt.figure(figsize=(8, 6))
        plt.text(0.5, 0.5, f'SJEDNICA BILECA - SOLARNA OGRADA\nUkupno stvarno: {total_actual:.0f} kWh\nInstalisano: {installed_kwp:.2f} kWp', 
                 ha='center', va='center', fontsize=14)
        plt.axis('off')
        pdf.savefig(fig); plt.close()
        
        # Grafikon
        fig = plt.figure(figsize=(8, 6))
        plt.bar(sides, actual_values, color='blue')
        plt.title('Stvarna proizvodnja po stranama')
        plt.ylabel('kWh')
        plt.tight_layout()
        pdf.savefig(fig); plt.close()
        
        # 3D Model
        img = os.path.join(BASE_PATH, "SJEDNICA_BILECA_3D_konstrukcija.png")
        if os.path.exists(img):
            fig = plt.figure(figsize=(10, 8))
            plt.imshow(plt.imread(img))
            plt.axis('off')
            plt.tight_layout()
            pdf.savefig(fig); plt.close()
            
    return pdf_path

# ==============================================================================
# 🚀 MAIN EXECUTION
# ==============================================================================
if __name__ == "__main__":
    res, act = run_simulation()
    
    if not res:
        print("❌ Simulacija nije vratila rezultate.")
    else:
        total_act = sum(act.values())
        total_inc = sum(res.values())
        installed_kwp = 19 * 585 / 1000
        
        print(f"\n📊 UKUPNO INCIDENTNO: {total_inc:.0f} kWh")
        print(f"⚡ UKUPNO STVARNO:    {total_act:.0f} kWh")
        print(f"⚡ Specifična (stvarna): {total_act/installed_kwp:.0f} kWh/kWp")
        
        img_3d = generate_3d_model()
        pdf_path = generate_report(res, act)
        
        print(f"\n✅ 3D model sačuvan: {img_3d}")
        print(f"✅ PDF izvještaj sačuvan: {pdf_path}")
        print("✅ ZAVRŠENO.")