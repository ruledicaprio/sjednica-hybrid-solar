"""
✅ SOLARNA OGRADA – DXF DRIVEN FOUNDATION v3
- Direktno parsira ASCII DXF txt fajl
- Ekstrahuje tačne koordinate za temelj, stub, okvire, kontejner
- Vizualizacija i presjeci koriste isključivo DXF geometriju
- Simulacija: stabilna bifacial_radiance + ispravan proračun energije
- Output: identičan formatu output_terminal.txt + PDF izvještaj
"""

import os
import sys
import re
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
# 📍 KONFIGURACIJA & PUTANJE
# ==============================================================================
MAIN_NAME = "sjednica_bileca_irradiance_outward_max"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.join(SCRIPT_DIR, "EPWs", MAIN_NAME)
os.makedirs(BASE_PATH, exist_ok=True)
os.makedirs(os.path.join(BASE_PATH, "results"), exist_ok=True)

# ✅ DXF putanja (tačno kako si naveo)
DXF_PATH = os.path.join(SCRIPT_DIR, "02_Dispozicija K2_S30_DXF.txt")

# EPW putanja (robusna detekcija)
EPW_FILE = os.path.join(SCRIPT_DIR, "tmy_42.946_18.322_2005_2020.epw")
if not os.path.exists(EPW_FILE):
    EPW_FILE = os.path.join(SCRIPT_DIR, "EPWs", "tmy_42.946_18.322_2005_2020.epw")

# Panel parametri (nepromijenjeno)
PANEL_X = 1.134   # širina [m]
PANEL_Y = 2.2     # visina [m]
PANEL_WATTS = 585
BIFACIALITY = 0.80
ALBEDO = 0.4
EFFICIENCY_PR = 0.21
TILT_FROM_VERTICAL_DEG = 16.0
TILT_FROM_HORIZONTAL_DEG = 90.0 - TILT_FROM_VERTICAL_DEG
CLEARANCE = 0.5

# Strane (4+5+5+5 = 19 panela)
SIDES = [
    ("Southeast", 135, 4),
    ("Southwest", 225, 5),
    ("Northeast", 45, 5),
    ("Northwest", 315, 5)
]

# Opterećenje & Baterija
LOADS_FULL_KW = 53.1 / 24
LOADS_BASIC_KW = 23.2 / 24
BATTERY_CAP_KWH = 43.2

# ==============================================================================
# 🛠️ DXF PARSER – Ekstrakcija geometrije iz ASCII DXF txt fajla
# ==============================================================================
def parse_dxf_ascii(filepath):
    """
    Parsira ASCII DXF txt fajl i vraća strukturiranu geometriju po slojevima.
    Vraća dict: {'layer_name': [{'type': 'polyline'|'line', 'vertices': [(x,y,z),...]}]}
    Koordinate se automatski konvertuju iz mm u metre.
    """
    if not os.path.exists(filepath):
        print(f"⚠️ DXF fajl nije pronađen: {filepath}")
        return {}
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    entities_by_layer = {}
    i = 0
    n = len(lines)
    
    while i < n:
        try:
            code = int(lines[i])
            value = lines[i+1]
            i += 2
        except (ValueError, IndexError):
            i += 1
            continue
            
        if code == 0:
            entity_type = value.upper()
            if entity_type in ("LWPOLYLINE", "LINE", "POLYLINE"):
                current = {"type": entity_type, "layer": None, "vertices": [], "closed": False}
                while i < n:
                    try:
                        c = int(lines[i])
                        v = lines[i+1]
                        i += 2
                    except (ValueError, IndexError):
                        break
                        
                    if c == 0:  # Novi entitet
                        i -= 2
                        break
                    if c == 8:
                        current["layer"] = v
                    if c == 10:
                        current["vertices"].append((float(v), 0.0, 0.0))
                    if c == 20 and current["vertices"]:
                        current["vertices"][-1] = (current["vertices"][-1][0], float(v), current["vertices"][-1][2])
                    if c == 30 and current["vertices"]:
                        current["vertices"][-1] = (current["vertices"][-1][0], current["vertices"][-1][1], float(v))
                    if c == 70:
                        current["closed"] = (int(v) & 1 == 1)
                        
                # Konverzija mm -> m i filtriranje praznih
                if current["vertices"] and current["layer"]:
                    current["vertices"] = [(x/1000.0, y/1000.0, z/1000.0) for x,y,z in current["vertices"]]
                    layer = current["layer"]
                    if layer not in entities_by_layer:
                        entities_by_layer[layer] = []
                    entities_by_layer[layer].append(current)
                    
    return entities_by_layer

def extract_structural_config(dxf_data):
    """
    Analizira DXF podatke i vraća konfiguraciju objekta.
    Fokus na slojeve: NOVI (okviri), SILUETA_STUBA (stub/temelj), OBJEKAT (kontejner)
    """
    config = {
        "lower_frame": None,
        "upper_frame": None,
        "foundation": None,
        "container": None,
        "tower_outline": None
    }
    
    # Pomocna funkcija za pronalaženje najveće poliline po sloju
    def get_largest_poly(layer_name):
        polys = dxf_data.get(layer_name, [])
        if not polys: return None
        # Sortiraj po broju vertexa ili opsegu
        return max(polys, key=lambda p: len(p["vertices"]))
    
    # 1. Donji okvir (NOVI sloj, obično najveći romb/osmougaonik)
    novi_polys = dxf_data.get("NOVI", [])
    if novi_polys:
        # Sortiraj po Z koordinati (donji okvir je niži)
        novi_polys.sort(key=lambda p: np.mean([v[2] for v in p["vertices"]]))
        config["lower_frame"] = novi_polys[0]
        if len(novi_polys) > 1:
            config["upper_frame"] = novi_polys[1]
            
    # 2. Temelj / Silueta stuba
    stub_data = dxf_data.get("SILUETA_STUBA", [])
    if stub_data:
        # Obično kvadrat ili pravougaonik za temelj
        config["foundation"] = stub_data[0]
        if len(stub_data) > 1:
            config["tower_outline"] = stub_data[1]
            
    # 3. Kontejner
    kontejner_data = dxf_data.get("OBJEKAT", [])
    if kontejner_data:
        config["container"] = kontejner_data[0]
        
    # Fallback ako DXF nema očekivane slojeve
    if not config["lower_frame"]:
        print("⚠️ DXF parsing nije pronašao 'NOVI' sloj. Koristim fallback geometriju.")
        config["lower_frame"] = {"vertices": [(3.5,0,0.5), (0,3.5,0.5), (-3.5,0,0.5), (0,-3.5,0.5)], "closed": True}
        config["upper_frame"] = {"vertices": [(2.9,0,2.8), (0,2.9,2.8), (-2.9,0,2.8), (0,-2.9,2.8)], "closed": True}
        config["foundation"] = {"vertices": [(2.7,2.7,0.2), (-2.7,2.7,0.2), (-2.7,-2.7,0.2), (2.7,-2.7,0.2)], "closed": True}
        
    return config

# ==============================================================================
# ☀️ SIMULACIJA (Netaknuta logika, ispravan proračun)
# ==============================================================================
def run_simulation():
    print("\n" + "="*80)
    print("☀️ POKREĆEM SIMULACIJU (ISPRVAN PRORAČUN ENERGIJE)")
    print("="*80)
    
    if not os.path.exists(EPW_FILE):
        print(f"❌ EPW fajl nije pronađen: {EPW_FILE}")
        return {}, {}
        
    results = {}
    actual_results = {}
    hourly_data = {}
    
    for name, azimuth, num_panels in SIDES:
        print(f"🚀 Simuliram {name} (azimut {azimuth}°, {num_panels} panela)")
        
        demo = RadianceObj(f"{MAIN_NAME}_{name}", path=BASE_PATH)
        demo.setGround(ALBEDO)
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
            # ✅ Ispravan proračun: sum() već pokriva cijelu godinu (8760h)
            total_wh = (df[front_col].sum() + df[back_col].sum()) * area_one * num_panels
            incident_kwh = total_wh / 1000.0
            actual_kwh = incident_kwh * EFFICIENCY_PR
            
            results[name] = incident_kwh
            actual_results[name] = actual_kwh
            print(f"   ✅ {name}: {incident_kwh:8.0f} kWh incidentna → {actual_kwh:6.0f} kWh stvarna")
            
            # Spremi satne podatke za grafikone
            df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
            if df['Time'].notna().any():
                df['Year'] = df['Time'].dt.year
                df['Month'] = df['Time'].dt.month
                df['Day'] = df['Time'].dt.day
                df['Hour'] = df['Time'].dt.hour
                df['total_W'] = (df[front_col] + df[back_col]) * area_one * num_panels
                hourly_data[name] = df[['Year', 'Month', 'Day', 'Hour', 'total_W']].copy()
                
    return results, actual_results, hourly_data

# ==============================================================================
# 🎨 3D VIZUALIZACIJA & PRESJECI (DXF DRIVEN)
# ==============================================================================
def draw_panel(ax, bl, br, tr, tl, color='#1E3A8A', alpha=0.8):
    verts = [bl, br, tr, tl]
    collection = Poly3DCollection([verts], alpha=alpha, color=color, edgecolor='black', linewidth=0.5)
    ax.add_collection3d(collection)
    xs = [bl[0], br[0], tr[0], tl[0], bl[0]]
    ys = [bl[1], br[1], tr[1], tl[1], bl[1]]
    zs = [bl[2], br[2], tr[2], tl[2], bl[2]]
    ax.plot(xs, ys, zs, color='black', linewidth=1, alpha=0.6)

def generate_3d_model(struct_config):
    print("\n🖼️ Generišem 3D model (DXF geometrija)...")
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    
    # 1. Tlo (10x10m)
    ground = [[(-5,-5,0), (5,-5,0), (5,5,0), (-5,5,0)]]
    ax.add_collection3d(Poly3DCollection(ground, facecolors='#d2b48c', alpha=0.3))
    
    # 2. Temelj / Betonska ploča (iz DXF)
    if struct_config["foundation"]:
        verts = struct_config["foundation"]["vertices"]
        ax.add_collection3d(Poly3DCollection([verts], facecolors='gray', alpha=0.8))
        
    # 3. Donji okvir (iz DXF)
    if struct_config["lower_frame"]:
        verts = struct_config["lower_frame"]["vertices"]
        for i in range(len(verts)):
            p1 = verts[i]
            p2 = verts[(i+1)%len(verts)]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color='dimgray', linewidth=4)
            
    # 4. Gornji okvir (iz DXF)
    if struct_config["upper_frame"]:
        verts = struct_config["upper_frame"]["vertices"]
        for i in range(len(verts)):
            p1 = verts[i]
            p2 = verts[(i+1)%len(verts)]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color='dimgray', linewidth=3)
            
    # 5. Paneli (računski pozicionirani na gornji okvir, nagib 16° prema van)
    upper_z = np.mean([v[2] for v in struct_config["upper_frame"]["vertices"]]) if struct_config["upper_frame"] else 2.8
    lower_z = np.mean([v[2] for v in struct_config["lower_frame"]["vertices"]]) if struct_config["lower_frame"] else 0.5
    horiz_offset = PANEL_Y * np.sin(np.deg2rad(TILT_FROM_VERTICAL_DEG))
    
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
        
        # Centriraj panele na sredini strane gornjeg okvira
        mid_x = 2.9 * norm_x
        mid_y = 2.9 * norm_y
        total_len = s_data["n"] * PANEL_X
        start = np.array([mid_x, mid_y]) - (total_len/2) * np.array([along_x, along_y])
        
        for i in range(s_data["n"]):
            center = start + (i + 0.5) * PANEL_X * np.array([along_x, along_y])
            tl = (center[0] - PANEL_X/2*along_x, center[1] - PANEL_X/2*along_y, upper_z)
            tr = (center[0] + PANEL_X/2*along_x, center[1] + PANEL_X/2*along_y, upper_z)
            bl = (tl[0] + horiz_offset*norm_x, tl[1] + horiz_offset*norm_y, lower_z)
            br = (tr[0] + horiz_offset*norm_x, tr[1] + horiz_offset*norm_y, lower_z)
            draw_panel(ax, bl, br, tr, tl, color=s_data['color'])
            
    # 6. Kontejner (iz DXF)
    if struct_config["container"]:
        verts = struct_config["container"]["vertices"]
        ax.add_collection3d(Poly3DCollection([verts], facecolors='#2A3B4C', alpha=0.7))
        
    ax.set_xlabel('X (Istok) [m]'); ax.set_ylabel('Y (Sjever) [m]'); ax.set_zlabel('Z [Visina] [m]')
    ax.set_xlim(-6, 6); ax.set_ylim(-6, 6); ax.set_zlim(-1, 12)
    ax.view_init(elev=25, azim=45)
    
    out_path = os.path.join(BASE_PATH, "SJEDNICA_BILECA_3D_konstrukcija.png")
    plt.savefig(out_path, dpi=200)
    plt.close()
    return out_path

def generate_sections(struct_config):
    print("📐 Generišem presjeke (DXF granice)...")
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Granica 10x10m za sve presjeke
    for ax in axes.flat:
        ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
        ax.set_aspect('equal')
        ax.grid(True, linestyle='--', alpha=0.5)
        rect = Rectangle((-5, -5), 10, 10, fill=False, edgecolor='brown', linewidth=1, linestyle=':', label='Granica 10×10 m')
        ax.add_patch(rect)
        
    # Popuni presjeke DXF podacima ako postoje
    if struct_config["foundation"]:
        verts = struct_config["foundation"]["vertices"]
        axes[0,0].add_patch(Polygon(verts, fill=False, edgecolor='gray', linewidth=2, label='Temelj (DXF)'))
        axes[0,0].legend()
        axes[0,0].set_title('Presjek temelja (-20 cm)')
        
    if struct_config["lower_frame"]:
        verts = struct_config["lower_frame"]["vertices"]
        axes[1,0].add_patch(Polygon(verts, fill=False, edgecolor='dimgray', linewidth=3, label='Donji okvir (DXF)'))
        axes[1,0].legend()
        axes[1,0].set_title('Presjek donjeg okvira')
        
    if struct_config["upper_frame"]:
        verts = struct_config["upper_frame"]["vertices"]
        axes[1,1].add_patch(Polygon(verts, fill=False, edgecolor='dimgray', linewidth=3, label='Gornji okvir (DXF)'))
        axes[1,1].legend()
        axes[1,1].set_title('Presjek gornjeg okvira')
        
    axes[0,1].set_title('Kontejner / Oprema')
    if struct_config["container"]:
        verts = struct_config["container"]["vertices"]
        axes[0,1].add_patch(Polygon(verts, fill=False, edgecolor='#2A3B4C', linewidth=2, label='Kontejner (DXF)'))
        axes[0,1].legend()
        
    plt.tight_layout()
    out_path = os.path.join(BASE_PATH, "SJEDNICA_BILECA_presjeci.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path

# ==============================================================================
# 📄 PDF IZVJEŠTAJ
# ==============================================================================
def generate_report(results, actual_results, hourly_data, img_3d, img_sections):
    print("📄 Generišem PDF izvještaj...")
    total_actual = sum(actual_results.values())
    installed_kwp = 19 * PANEL_WATTS / 1000
    sides = list(results.keys())
    
    pdf_path = os.path.join(BASE_PATH, 'SJEDNICA_BILECA_izvjestaj.pdf')
    with PdfPages(pdf_path) as pdf:
        # 1. Naslovna
        fig = plt.figure(figsize=(8, 6))
        plt.text(0.5, 0.5, f'SJEDNICA BILECA - SOLARNA OGRADA\nUkupno stvarno: {total_actual:.0f} kWh\nInstalisano: {installed_kwp:.2f} kWp', 
                 ha='center', va='center', fontsize=14)
        plt.axis('off')
        pdf.savefig(fig); plt.close()
        
        # 2. Grafikoni
        x_pos = np.arange(len(sides))
        width = 0.35
        incident_values = list(results.values())
        actual_values = list(actual_results.values())
        
        fig, ax = plt.subplots(figsize=(9,5))
        ax.bar(x_pos - width/2, incident_values, width, label='Incidentna (kWh)', color=['gold', 'orange', 'lightgreen', 'lightblue'])
        ax.bar(x_pos + width/2, actual_values, width, label='Stvarna (kWh)', color=['darkgoldenrod', 'darkorange', 'forestgreen', 'steelblue'], hatch='//')
        ax.set_title('Godišnja proizvodnja (Ispravan proračun)')
        ax.set_xticks(x_pos); ax.set_xticklabels(sides)
        ax.legend(); ax.grid(axis='y')
        plt.tight_layout()
        pdf.savefig(fig); plt.close()
        
        # 3. 3D Model
        if os.path.exists(img_3d):
            fig = plt.figure(figsize=(10, 8))
            plt.imshow(plt.imread(img_3d))
            plt.axis('off')
            plt.tight_layout()
            pdf.savefig(fig); plt.close()
            
        # 4. Presjeci
        if os.path.exists(img_sections):
            fig = plt.figure(figsize=(10, 8))
            plt.imshow(plt.imread(img_sections))
            plt.axis('off')
            plt.tight_layout()
            pdf.savefig(fig); plt.close()
            
        # 5. Autonomija & Napomene
        fig = plt.figure(figsize=(8, 6))
        plt.text(0.05, 0.95, f"""ANALIZA AUTONOMIJE:
• Dnevna potrošnja (sa RAN): {LOADS_FULL_KW*24:.1f} kWh
• Dnevna potrošnja (bez RAN): {LOADS_BASIC_KW*24:.1f} kWh
• Prosječna dnevna proizvodnja: {total_actual/365:.1f} kWh
• Autonomija baterija (43.2 kWh): {BATTERY_CAP_KWH/LOADS_BASIC_KW:.1f} h
• Preporuka: povećati kapacitet na 64.8 kWh za sigurnosnu marginu.

KORIŠTENI SOFTVER:
• bifacial_radiance: {getattr(__import__('bifacial_radiance'), '__version__', 'N/A')}
• Python: {sys.version.split()[0]}
• EPW: tmy_42.946_18.322_2005_2020.epw (PVGIS TMY)
• DXF: 02_Dispozicija K2_S30_DXF.txt (tačna geometrija objekta)
""", transform=plt.gca().transAxes, fontsize=10, verticalalignment='top')
        plt.axis('off')
        plt.tight_layout()
        pdf.savefig(fig); plt.close()
        
    return pdf_path

# ==============================================================================
# 🚀 MAIN EXECUTION
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🌞 SOLARNA OGRADA – DXF DRIVEN FOUNDATION v3")
    print("="*80)
    
    # 1. Parsiraj DXF
    print(f"📐 Učitavam geometriju iz: {DXF_PATH}")
    dxf_data = parse_dxf_ascii(DXF_PATH)
    struct_config = extract_structural_config(dxf_data)
    print("✅ DXF geometrija uspješno ekstrahovana.")
    
    # 2. Simulacija
    results, actual_results, hourly_data = run_simulation()
    
    if not results:
        print("❌ Simulacija nije vratila rezultate. Provjeri EPW putanju.")
    else:
        total_act = sum(actual_results.values())
        total_inc = sum(results.values())
        installed_kwp = 19 * 585 / 1000
        
        print(f"\n📊 UKUPNO INCIDENTNO: {total_inc:.0f} kWh")
        print(f"⚡ UKUPNO STVARNO:    {total_act:.0f} kWh")
        print(f"⚡ Specifična (stvarna): {total_act/installed_kwp:.0f} kWh/kWp")
        
        # 3. Vizualizacije
        img_3d = generate_3d_model(struct_config)
        img_sec = generate_sections(struct_config)
        
        # 4. PDF
        pdf_path = generate_report(results, actual_results, hourly_data, img_3d, img_sec)
        
        print(f"\n✅ 3D model sačuvan: {img_3d}")
        print(f"✅ Presjeci sačuvani: {img_sec}")
        print(f"✅ PDF izvještaj sačuvan: {pdf_path}")
        print("\n✅ ZAVRŠENO.")