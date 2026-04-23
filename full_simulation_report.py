#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RURALSTAR HYBRID – KOMPLETNA SIMULACIJA + DETALJAN IZVJEŠTAJ
✅ Automatski generiše sve fajlove, pokreće simulaciju i kreira PDF izvještaj
"""
import os
import sys
import subprocess
import numpy as np
import pandas as pd
from math import cos, sin, radians, sqrt
import pvlib
from pvlib import iotools, irradiance, solarposition
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# =============================================================================
# 📁 PUTANJE & KONFIGURACIJA
# =============================================================================
PROJECT_ROOT = r"E:\Radiance_build\moja_solar_ograda"
RAD_BASE = os.path.join(PROJECT_ROOT, "sjednica_bileca_irradiance_outward_max")
os.makedirs(RAD_BASE, exist_ok=True)
for sub in ["materials", "objects", "skies", "results", "EPWs", "reports"]:
    os.makedirs(os.path.join(RAD_BASE, sub), exist_ok=True)

ALTITUDE = 1050.0
LAT_REF = 42.9448
LON_REF = 18.3236

# Paneli
PANEL_L = 2.279
PANEL_W = 1.134
PANEL_AREA = PANEL_L * PANEL_W
TILT_DEG = 16.0
TILT_RAD = radians(TILT_DEG)
MODULE_EFF = 0.21
BIFACIAL_FACTOR = 0.80
ALBEDO = 0.65

# GPS uglovi
gps_corners = [
    (42.94483338639821, 18.323625614573174),
    (42.94480147615224, 18.323706763917354),
    (42.94475532899798, 18.323639027687914),
    (42.944790675757524, 18.323571291458475),
]

m_per_deg_lat = 111320.0
m_per_deg_lon = 111320.0 * cos(radians(LAT_REF))

def gps_to_xy(lat, lon):
    x = (lon - LON_REF) * m_per_deg_lon
    y = (lat - LAT_REF) * m_per_deg_lat
    return x, y

corners_local = []
for lat, lon in gps_corners:
    corners_local.append(gps_to_xy(lat, lon))

cx = sum(p[0] for p in corners_local) / 4
cy = sum(p[1] for p in corners_local) / 4
corners_local = [(x - cx, y - cy) for x, y in corners_local]

SIDES = {
    "MPLS": [(135, 5), (225, 5)],
    "RAN":  [(45, 5),  (315, 4)]
}

# =============================================================================
# ✍️ POMOĆNE FUNKCIJE
# =============================================================================
def write_file(path, content):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)

def write_materials():
    mat = """# Materijali
void plastic ground_mat
0
0
5 0.65 0.65 0.65 0 0

void plastic concrete_mat
0
0
5 0.70 0.70 0.70 0 0

void plastic cabinet_mat
0
0
5 0.5 0.5 0.5 0 0

void glass panel_glass
0
0
3 0.95 0.95 0.95
"""
    write_file(os.path.join(RAD_BASE, "materials", "materials.mat"), mat)

def write_ground_and_slab():
    ground = "# Tlo\nground_mat polygon ground\n0\n0\n12\n"
    for x,y in [(-8,-8),(8,-8),(8,8),(-8,8)]:
        ground += f"  {x:.3f} {y:.3f} 0\n"
    write_file(os.path.join(RAD_BASE, "objects", "ground.rad"), ground)

    slab = "# Betonska ploča\nconcrete_mat polygon slab\n0\n0\n12\n"
    for x,y in corners_local:
        slab += f"  {x:.3f} {y:.3f} 0\n"
    write_file(os.path.join(RAD_BASE, "objects", "slab.rad"), slab)

def _box_polygons(mat, name, xmin, ymin, zmin, dx, dy, dz):
    xmax, ymax, zmax = xmin+dx, ymin+dy, zmin+dz
    v = [
        (xmin,ymin,zmin), (xmax,ymin,zmin), (xmax,ymax,zmin), (xmin,ymax,zmin),
        (xmin,ymin,zmax), (xmax,ymin,zmax), (xmax,ymax,zmax), (xmin,ymax,zmax)
    ]
    faces = [
        (v[0],v[1],v[2],v[3]), (v[4],v[5],v[6],v[7]),
        (v[0],v[3],v[7],v[4]), (v[1],v[2],v[6],v[5]),
        (v[0],v[4],v[5],v[1]), (v[3],v[7],v[6],v[2])
    ]
    out = []
    for face in faces:
        out.extend([f"{mat} polygon {name}", "0", "0", "12"])
        for p in face:
            out.append(f"  {p[0]:.3f} {p[1]:.3f} {p[2]:.3f}")
    return "\n".join(out) + "\n"

def write_cabinets_and_generator():
    objs = []
    objs.append(_box_polygons("cabinet_mat", "mts", -0.7-0.325, -2.0-0.325, 0.2, 0.65, 0.65, 1.6))
    objs.append(_box_polygons("cabinet_mat", "icc", 0.05-0.325, -2.0-0.325, 0.2, 0.65, 0.65, 1.6))
    objs.append(_box_polygons("cabinet_mat", "generator", -0.9-0.9, -3.0-0.45, 0.2, 1.8, 0.9, 1.6))
    write_file(os.path.join(RAD_BASE, "objects", "cabinets.rad"), "\n".join(objs))

def generate_panel_surface(name, center, azimuth_deg):
    w2, h2 = PANEL_W/2, PANEL_L/2
    pts = [(-w2, -h2, 0), (w2, -h2, 0), (w2, h2, 0), (-w2, h2, 0)]
    ct, st = cos(TILT_RAD), sin(TILT_RAD)
    def rot_x(x, y, z): return (x, y*ct - z*st, y*st + z*ct)
    az_rad = radians(azimuth_deg)
    ca, sa = cos(az_rad), sin(az_rad)
    def rot_z(x, y, z): return (x*ca - y*sa, x*sa + y*ca, z)
    
    world = []
    for (x,y,z) in pts:
        xr, yr, zr = rot_x(x, y, z)
        xr, yr, zr = rot_z(xr, yr, zr)
        world.append((xr + center[0], yr + center[1], zr + center[2]))
        
    lines = [f"panel_glass polygon {name}", "0", "0", "12"]
    for p in world:
        lines.append(f"  {p[0]:.4f} {p[1]:.4f} {p[2]:.4f}")
    return "\n".join(lines)

def write_panels():
    panels_path = os.path.join(RAD_BASE, "objects", "panels.rad")
    sensors_path = os.path.join(RAD_BASE, "objects", "sensors.txt")
    
    with open(panels_path, 'w', encoding='utf-8') as fpan, \
         open(sensors_path, 'w', encoding='utf-8') as fsen:
        
        fpan.write("# Paneli MPLS (10) + RAN (9)\n")
        panel_id = 0
        scale = 7.0 / 5.8
        Z_LOWER = 0.5
        VERT_PROJ = PANEL_L * cos(TILT_RAD)
        
        for system, sides in SIDES.items():
            for az, count in sides:
                az_rad = radians(az)
                nx, ny = sin(az_rad), cos(az_rad)
                
                if az == 135: p1, p2 = corners_local[1], corners_local[2]
                elif az == 225: p1, p2 = corners_local[2], corners_local[3]
                elif az == 45: p1, p2 = corners_local[0], corners_local[1]
                elif az == 315: p1, p2 = corners_local[3], corners_local[0]
                else: continue
                
                mid_x = (p1[0] + p2[0]) / 2
                mid_y = (p1[1] + p2[1]) / 2
                dx, dy = p2[0] - p1[0], p2[1] - p1[1]
                length = sqrt(dx*dx + dy*dy)
                if length == 0: continue
                ux, uy = dx/length, dy/length
                
                lp1 = (p1[0]*scale, p1[1]*scale)
                lp2 = (p2[0]*scale, p2[1]*scale)
                low_mid_x = (lp1[0] + lp2[0]) / 2
                low_mid_y = (lp1[1] + lp2[1]) / 2
                
                start_offset = -(count - 1) * PANEL_W / 2
                for i in range(count):
                    panel_id += 1
                    offset = start_offset + i * PANEL_W
                    
                    up_x = mid_x + offset * ux
                    up_y = mid_y + offset * uy
                    low_x = low_mid_x + offset * ux
                    low_y = low_mid_y + offset * uy
                    
                    center_x = (up_x + low_x) / 2
                    center_y = (up_y + low_y) / 2
                    center_z = Z_LOWER + VERT_PROJ / 2
                    
                    panel_name = f"panel_{panel_id}"
                    fpan.write(generate_panel_surface(panel_name, (center_x, center_y, center_z), az) + "\n")
                    
                    n_x = nx * sin(TILT_RAD)
                    n_y = ny * sin(TILT_RAD)
                    n_z = cos(TILT_RAD)
                    
                    fsen.write(f"{center_x + 0.01*n_x:.4f} {center_y + 0.01*n_y:.4f} {center_z + 0.01*n_z:.4f} {n_x:.4f} {n_y:.4f} {n_z:.4f}\n")
                    fsen.write(f"{center_x - 0.01*n_x:.4f} {center_y - 0.01*n_y:.4f} {center_z - 0.01*n_z:.4f} {-n_x:.4f} {-n_y:.4f} {-n_z:.4f}\n")
    
    return panel_id

# =============================================================================
# 🌤️ VREMENSKI PODACI
# =============================================================================
def fetch_and_prepare_weather():
    print("\n🌍 Preuzimam PVGIS TMY podatke...")
    df, meta = pvlib.iotools.get_pvgis_tmy(LAT_REF, LON_REF, map_variables=True)
    df = df.replace(9999, np.nan)
    
    solpos = solarposition.get_solarposition(df.index, LAT_REF, LON_REF)
    df['zenith'] = solpos['apparent_zenith']
    
    missing = df['dni'].isna() | df['dhi'].isna()
    if missing.any():
        disc = irradiance.disc(ghi=df['ghi'], solar_zenith=df['zenith'], datetime_or_doy=df.index)
        df.loc[missing, 'dni'] = disc['dni'].loc[missing].values
        df.loc[missing, 'dhi'] = disc['dhi'].loc[missing].values
    
    # WEa fajl
    wea_lines = [f'site "Bileca" {LAT_REF:.4f} {LON_REF:.4f} 1 {int(ALTITUDE)}',
                 'ground 0.2 0.2',
                 'date time DNI DHI']
    for ts, row in df.iterrows():
        m, d, h = ts.month, ts.day, ts.hour + 0.5
        dni = max(0.0, float(row.get('dni', 0) or 0))
        dhi = max(0.0, float(row.get('dhi', 0) or 0))
        wea_lines.append(f"{m:d} {d:d} {h:.1f} {dni:.1f} {dhi:.1f}")
    
    wea_path = os.path.join(RAD_BASE, "skies", "weather.wea")
    with open(wea_path, 'w', encoding='ascii', newline='\n') as f:
        f.write('\n'.join(wea_lines) + '\n')
    
    print(f"✅ Vremenski podaci: {len(df)} sati")
    return df, wea_path

# =============================================================================
# 🚀 RADIANCE SIMULACIJA
# =============================================================================
def run_radiance(wea_path):
    os.chdir(RAD_BASE)
    
    for f in ["scene.oct", "skies/annual.smx", "results/annual_irrad.txt"]:
        if os.path.exists(f): os.remove(f)
    
    sky_file = os.path.join("skies", "annual.smx")
    sky_abs = os.path.abspath(sky_file)
    wea_abs = os.path.abspath(wea_path)
    
    print("\n☀️ Generišem godišnji sky vektor...")
    cmd = f'gendaymtx -O 1 "{wea_abs}" > "{sky_abs}"'
    try:
        subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ gendaymtx greška: {e.stderr.strip()}")
        return False
    
    scene_files = [
        os.path.abspath("materials/materials.mat"),
        os.path.abspath("objects/ground.rad"),
        os.path.abspath("objects/slab.rad"),
        os.path.abspath("objects/cabinets.rad"),
        os.path.abspath("objects/panels.rad"),
    ]
    scene_oct = os.path.abspath("scene.oct")
    cmd_oconv = f'oconv {" ".join(scene_files)} > "{scene_oct}"'
    subprocess.run(cmd_oconv, shell=True, capture_output=True, text=True, check=True)
    print("✅ scene.oct kreiran")
    
    sensors_file = os.path.join(RAD_BASE, "objects", "sensors.txt")
    output_txt = os.path.join(RAD_BASE, "results", "annual_irrad.txt")
    n_sensors = 38
    
    print("🔍 Pokrećem rtrace (ovo može trajati nekoliko minuta)...")
    cmd_rtrace = (f'rtrace -h -I -ab 5 -ad 2048 -lw 1e-5 -aa 0.1 -y {n_sensors} -n 4 "{scene_oct}" < "{sensors_file}" '
                  f'| rcalc -e "$1+$2+$3" > "{output_txt}"')
    
    try:
        subprocess.run(cmd_rtrace, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ rtrace greška")
        return False
    
    print(f"✅ Rezultati sačuvani")
    return True

# =============================================================================
# 📊 OBRADA REZULTATA
# =============================================================================
def process_results(weather_df):
    irrad_file = os.path.join(RAD_BASE, "results", "annual_irrad.txt")
    if not os.path.exists(irrad_file):
        print(f"❌ Nema rezultata")
        return None
    
    irrad_data = np.loadtxt(irrad_file)
    if irrad_data.ndim == 1:
        irrad_data = irrad_data.reshape(-1, 1)
    
    n_hours, n_sensors = irrad_data.shape
    print(f"\n📈 Učitano: {n_hours} sati, {n_sensors} senzora")
    
    panel_ids = list(range(1, 20))
    cols = [f"panel_{pid}_{side}" for pid in panel_ids for side in ['front', 'back']]
    df_irr = pd.DataFrame(irrad_data, index=weather_df.index[:n_hours], columns=cols)
    
    # Proračun snage
    for pid in panel_ids:
        front_col = f"panel_{pid}_front"
        back_col = f"panel_{pid}_back"
        df_irr[f"P_{pid}_front"] = df_irr[front_col] * PANEL_AREA * MODULE_EFF
        df_irr[f"P_{pid}_back"] = df_irr[back_col] * PANEL_AREA * MODULE_EFF * BIFACIAL_FACTOR * ALBEDO
        df_irr[f"P_{pid}_total"] = df_irr[f"P_{pid}_front"] + df_irr[f"P_{pid}_back"]
    
    mpls_cols = [f"P_{pid}_total" for pid in range(1, 11)]
    ran_cols = [f"P_{pid}_total" for pid in range(11, 20)]
    df_irr['MPLS_DC_W'] = df_irr[mpls_cols].sum(axis=1)
    df_irr['RAN_DC_W'] = df_irr[ran_cols].sum(axis=1)
    
    # Baterije
    V_nom = 48.0
    capacity_kwh = V_nom * 450 / 1000.0
    load_mpls, load_ran, climate_w = 200/1000, 500/1000, 150/1000
    ssu_eff = 0.96
    
    soc_mpls = np.zeros(n_hours)
    soc_ran = np.zeros(n_hours)
    e_mpls = e_ran = capacity_kwh * 0.5
    soc_mpls[0] = soc_ran[0] = 0.5
    temp_air = weather_df.get('temp_air', pd.Series(20, index=df_irr.index)).reindex(df_irr.index).values
    
    for i in range(1, n_hours):
        pv_m = df_irr['MPLS_DC_W'].iloc[i] * ssu_eff / 1000
        net_m = pv_m - (load_mpls + (climate_w if temp_air[i] > 25 else 0))
        e_mpls = min(e_mpls + net_m, capacity_kwh) if net_m > 0 else max(e_mpls + net_m, 0.1*capacity_kwh)
        soc_mpls[i] = e_mpls / capacity_kwh
        
        pv_r = df_irr['RAN_DC_W'].iloc[i] * ssu_eff / 1000
        net_r = pv_r - load_ran
        e_ran = min(e_ran + net_r, capacity_kwh) if net_r > 0 else max(e_ran + net_r, 0.1*capacity_kwh)
        soc_ran[i] = e_ran / capacity_kwh
    
    df_irr['MPLS_SoC'] = soc_mpls
    df_irr['RAN_SoC'] = soc_ran
    
    return df_irr

# =============================================================================
# 📄 GENERISANJE IZVJEŠTAJA
# =============================================================================
def generate_report(df_irr, weather_df):
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    
    print("\n📄 Generišem detaljan izvještaj...")
    
    total_mpls = df_irr['MPLS_DC_W'].sum() / 1000
    total_ran = df_irr['RAN_DC_W'].sum() / 1000
    total_combined = total_mpls + total_ran
    
    installed_kwp = 19 * (PANEL_L * PANEL_W) * MODULE_EFF
    
    pdf_path = os.path.join(RAD_BASE, "reports", "SIMULACIJA_IZVJESTAJ.pdf")
    
    with PdfPages(pdf_path) as pdf:
        # Naslovna strana
        fig = plt.figure(figsize=(8.5, 11))
        plt.text(0.5, 0.95, 'RURALSTAR HYBRID\nSOLARNA OGRADA - SIMULACIJA', 
                 ha='center', va='top', fontsize=18, fontweight='bold')
        plt.text(0.5, 0.85, f'Lokacija: Bileća, BiH\nGPS: {LAT_REF:.4f}°, {LON_REF:.4f}°\nNadmorska visina: {ALTITUDE:.0f} m', 
                 ha='center', va='top', fontsize=12)
        plt.text(0.5, 0.75, f'Datum simulacije: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 
                 ha='center', va='top', fontsize=10)
        
        plt.text(0.5, 0.60, 'REZULTATI', ha='center', va='top', fontsize=14, fontweight='bold')
        results_text = f"""
Instalisana snaga: {installed_kwp:.2f} kWp
Ukupno panela: 19 (MPLS: 10, RAN: 9)

GODIŠNJA PROIZVODNJA:
├─ MPLS sistem: {total_mpls:,.0f} kWh DC
├─ RAN sistem:  {total_ran:,.0f} kWh DC
└─ UKUPNO:      {total_combined:,.0f} kWh DC

Specifična proizvodnja: {total_combined/installed_kwp:,.0f} kWh/kWp
Prosjek dnevno: {total_combined/365:.1f} kWh
        """
        plt.text(0.5, 0.45, results_text, ha='center', va='top', fontsize=10, family='monospace')
        
        battery_text = f"""
BATERIJSKI SISTEM (450Ah, 48V = {48*450/1000:.1f} kWh):
┌─────────────┬──────────────┬──────────────┐
│ Sistem      │ Min SoC      │ Prosječno    │
├─────────────┼──────────────┼──────────────┤
│ MPLS        │ {df_irr['MPLS_SoC'].min()*100:.1f}%          │ {df_irr['MPLS_SoC'].mean()*100:.1f}%           │
│ RAN         │ {df_irr['RAN_SoC'].min()*100:.1f}%          │ {df_irr['RAN_SoC'].mean()*100:.1f}%           │
└─────────────┴──────────────┴──────────────┘

⚠️ Sati sa SoC < 15%:
   MPLS: {(df_irr['MPLS_SoC']<0.15).sum()} h ({(df_irr['MPLS_SoC']<0.15).sum()/8760*100:.1f}%)
   RAN:  {(df_irr['RAN_SoC']<0.15).sum()} h ({(df_irr['RAN_SoC']<0.15).sum()/8760*100:.1f}%)
        """
        plt.text(0.5, 0.20, battery_text, ha='center', va='top', fontsize=9, family='monospace')
        plt.axis('off')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Mjesečna proizvodnja
        fig, ax = plt.subplots(figsize=(10, 6))
        monthly_mpls = df_irr['MPLS_DC_W'].resample('ME').sum() / 1000
        monthly_ran = df_irr['RAN_DC_W'].resample('ME').sum() / 1000
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        x = np.arange(12)
        width = 0.35
        ax.bar(x - width/2, monthly_mpls.values, width, label='MPLS', color='steelblue')
        ax.bar(x + width/2, monthly_ran.values, width, label='RAN', color='darkorange')
        ax.set_xlabel('Mjesec')
        ax.set_ylabel('Proizvodnja (kWh)')
        ax.set_title('Mjesečna proizvodnja po sistemima')
        ax.set_xticks(x)
        ax.set_xticklabels(months, rotation=45)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Dnevni profil (prosjek)
        fig, ax = plt.subplots(figsize=(10, 6))
        df_irr['hour'] = df_irr.index.hour
        hourly_mpls = df_irr.groupby('hour')['MPLS_DC_W'].mean() / 1000
        hourly_ran = df_irr.groupby('hour')['RAN_DC_W'].mean() / 1000
        hours = np.arange(24)
        ax.plot(hours, hourly_mpls.reindex(hours).fillna(0), 'b-', linewidth=2, label='MPLS')
        ax.plot(hours, hourly_ran.reindex(hours).fillna(0), 'orange', linewidth=2, label='RAN')
        ax.fill_between(hours, hourly_mpls.reindex(hours).fillna(0), alpha=0.3, color='blue')
        ax.fill_between(hours, hourly_ran.reindex(hours).fillna(0), alpha=0.3, color='orange')
        ax.set_xlabel('Sat u danu')
        ax.set_ylabel('Snaga (kW)')
        ax.set_title('Prosječni dnevni profil proizvodnje')
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # SoC baterija
        fig, axes = plt.subplots(2, 1, figsize=(10, 8))
        axes[0].plot(df_irr.index, df_irr['MPLS_SoC']*100, 'b-', linewidth=0.5, label='MPLS SoC')
        axes[0].axhline(y=15, color='red', linestyle='--', label='Min dozvoljeni (15%)')
        axes[0].axhline(y=100, color='green', linestyle='--', label='Maksimum')
        axes[0].set_ylabel('SoC (%)')
        axes[0].set_title('Stanje punjenja baterija - tokom godine')
        axes[0].legend(loc='upper right')
        axes[0].grid(alpha=0.3)
        
        axes[1].plot(df_irr.index, df_irr['RAN_SoC']*100, 'orange', linewidth=0.5, label='RAN SoC')
        axes[1].axhline(y=15, color='red', linestyle='--')
        axes[1].axhline(y=100, color='green', linestyle='--')
        axes[1].set_xlabel('Datum')
        axes[1].set_ylabel('SoC (%)')
        axes[1].legend(loc='upper right')
        axes[1].grid(alpha=0.3)
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Histogram SoC
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        axes[0].hist(df_irr['MPLS_SoC']*100, bins=20, color='steelblue', edgecolor='black', alpha=0.7)
        axes[0].set_xlabel('SoC (%)')
        axes[0].set_ylabel('Broj sati')
        axes[0].set_title('Distribucija SoC - MPLS')
        axes[0].grid(alpha=0.3)
        
        axes[1].hist(df_irr['RAN_SoC']*100, bins=20, color='darkorange', edgecolor='black', alpha=0.7)
        axes[1].set_xlabel('SoC (%)')
        axes[1].set_ylabel('Broj sati')
        axes[1].set_title('Distribucija SoC - RAN')
        axes[1].grid(alpha=0.3)
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Paneli po panelu
        fig, ax = plt.subplots(figsize=(12, 6))
        panel_totals = []
        for pid in range(1, 20):
            col = f"P_{pid}_total"
            panel_totals.append(df_irr[col].sum() / 1000)
        
        x = np.arange(19)
        colors = ['steelblue']*10 + ['darkorange']*9
        labels = [f'M{p}' for p in range(1,11)] + [f'R{p}' for p in range(1,10)]
        bars = ax.bar(x, panel_totals, color=colors, edgecolor='black')
        ax.set_xlabel('Panel ID')
        ax.set_ylabel('Godišnja proizvodnja (kWh)')
        ax.set_title('Proizvodnja po pojedinačnim panelima')
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45)
        ax.grid(axis='y', alpha=0.3)
        
        for i, v in enumerate(panel_totals):
            ax.text(i, v, f'{v:.0f}', ha='center', va='bottom', fontsize=8)
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    print(f"✅ PDF izvještaj sačuvan: {pdf_path}")
    return pdf_path

# =============================================================================
# 🎯 MAIN
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("RURALSTAR HYBRID – KOMPLETNA SIMULACIJA + IZVJEŠTAJ")
    print("=" * 70)
    
    # 1. Generiši geometriju
    print("\n🏗️ Generišem 3D geometriju...")
    write_materials()
    write_ground_and_slab()
    write_cabinets_and_generator()
    num_panels = write_panels()
    print(f"✅ Geometrija kreirana ({num_panels} panela)")
    
    # 2. Vremenski podaci
    weather_df, wea_path = fetch_and_prepare_weather()
    
    # 3. Radiance simulacija
    if not run_radiance(wea_path):
        print("\n❌ Simulacija nije uspjela")
        sys.exit(1)
    
    # 4. Obrada rezultata
    df_results = process_results(weather_df)
    if df_results is None:
        print("\n❌ Obrada rezultata nije uspjela")
        sys.exit(1)
    
    # 5. Generiši izvještaj
    pdf_path = generate_report(df_results, weather_df)
    
    # 6. Sažetak u konzoli
    total_mpls = df_results['MPLS_DC_W'].sum() / 1000
    total_ran = df_results['RAN_DC_W'].sum() / 1000
    
    print("\n" + "=" * 70)
    print("📊 KONAČNI REZULTATI")
    print("=" * 70)
    print(f"MPLS (10 panela): {total_mpls:,.0f} kWh/god")
    print(f"RAN (9 panela):   {total_ran:,.0f} kWh/god")
    print(f"UKUPNO:           {total_mpls+total_ran:,.0f} kWh/god")
    print(f"\n🔋 Baterije:")
    print(f"   MPLS: min SoC {df_results['MPLS_SoC'].min()*100:.1f}%, prosjek {df_results['MPLS_SoC'].mean()*100:.1f}%")
    print(f"   RAN:  min SoC {df_results['RAN_SoC'].min()*100:.1f}%, prosjek {df_results['RAN_SoC'].mean()*100:.1f}%")
    print(f"\n✅ Izvještaj: {pdf_path}")
    print("=" * 70)
