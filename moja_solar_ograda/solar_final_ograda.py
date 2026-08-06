#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RURALSTAR HYBRID – RADIANCE SIMULACIJA (Self-Shading + Bifacial)
✅ KONAČNA POPRAVKA: uklonjen invalidan -y flag, fiksirana gendaymtx sintaksa, alt=1050m
"""
import os
import sys
import subprocess
import numpy as np
import pandas as pd
from math import cos, sin, radians, sqrt
import pvlib
from pvlib import iotools, irradiance, solarposition

# =============================================================================
# 🌐 WINDOWS UTF-8 & KONZOLA
# =============================================================================
if sys.platform == "win32":
    import io
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'English_United States.1252')
    
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding='utf-8', errors='replace')

# =============================================================================
# 📁 PUTANJE & KONFIGURACIJA
# =============================================================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
RAD_BASE = os.path.join(PROJECT_ROOT, "sjednica_bileca_irradiance_outward_max")
os.makedirs(RAD_BASE, exist_ok=True)
for sub in ["materials", "objects", "skies", "results", "EPWs"]:
    os.makedirs(os.path.join(RAD_BASE, sub), exist_ok=True)

ALTITUDE = 1050.0  # Nadmorska visina objekta (m)

# =============================================================================
# 🗺️ GPS → LOKALNE KOORDINATE
# =============================================================================
gps_corners = [
    (42.94483338639821, 18.323625614573174),  # Sjever
    (42.94480147615224, 18.323706763917354),  # Istok
    (42.94475532899798, 18.323639027687914),  # Jug
    (42.944790675757524, 18.323571291458475), # Zapad
]
lat_ref = sum(p[0] for p in gps_corners) / 4
lon_ref = sum(p[1] for p in gps_corners) / 4
m_per_deg_lat = 111320.0
m_per_deg_lon = 111320.0 * cos(radians(lat_ref))

def gps_to_xy(lat, lon):
    x = (lon - lon_ref) * m_per_deg_lon
    y = (lat - lat_ref) * m_per_deg_lat
    return x, y

corners_local = []
for lat, lon in gps_corners:
    corners_local.append(gps_to_xy(lat, lon))

cx = sum(p[0] for p in corners_local) / 4
cy = sum(p[1] for p in corners_local) / 4
corners_local = [(x - cx, y - cy) for x, y in corners_local]

print("Dimenzije gornjeg rama (m):")
for i in range(4):
    j = (i+1)%4
    d = sqrt((corners_local[i][0]-corners_local[j][0])**2 + (corners_local[i][1]-corners_local[j][1])**2)
    print(f"  Stranica {i+1}: {d:.3f}")

# =============================================================================
# 🏗️ PANELI I KONSTRUKCIJA
# =============================================================================
PANEL_L = 2.279
PANEL_W = 1.134
TILT_DEG = 16.0
TILT_RAD = radians(TILT_DEG)
Z_LOWER = 0.5
VERT_PROJ = PANEL_L * cos(TILT_RAD)
scale = 7.0 / 5.8

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
    ground = "# Tlo (tampon 0.65)\nground_mat polygon ground\n0\n0\n12\n"
    for x,y in [(-8,-8),(8,-8),(8,8),(-8,8)]:
        ground += f"  {x:.3f} {y:.3f} 0\n"
    write_file(os.path.join(RAD_BASE, "objects", "ground.rad"), ground)

    slab = "# Betonska AB ploča\nconcrete_mat polygon slab\n0\n0\n12\n"
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

# =============================================================================
# 🌤️ VREMENSKI PODACI & WEATHER FILES
# =============================================================================
def fetch_weather_from_pvgis(lat, lon, year_start=None, year_end=None):
    if year_start is not None and year_end is not None:
        print(f"🌍 Preuzimam PVGIS satne podatke za period {year_start}–{year_end}...")
        df, meta = pvlib.iotools.get_pvgis_hourly(lat, lon, start=year_start, end=year_end, map_variables=True)
    else:
        print("🌍 Preuzimam PVGIS TMY podatke...")
        pvgis_result = pvlib.iotools.get_pvgis_tmy(lat, lon, map_variables=True)
        df, meta = pvgis_result[0], pvgis_result[1]
    print(f"✅ Podaci preuzeti. Broj sati: {len(df)}")
    return df, meta

def prepare_weather_files(df, lat, lon):
    df = df.replace(9999, np.nan)
    solpos = solarposition.get_solarposition(df.index, lat, lon)
    df['zenith'] = solpos['apparent_zenith']
    missing = df['dni'].isna() | df['dhi'].isna()
    if missing.any():
        disc = irradiance.disc(ghi=df['ghi'], solar_zenith=df['zenith'], datetime_or_doy=df.index)
        df.loc[missing, 'dni'] = disc['dni'].loc[missing].values
        df.loc[missing, 'dhi'] = disc['dhi'].loc[missing].values

    # 1. EPW (arhiva)
    epw_path = os.path.join(RAD_BASE, "EPWs", "weather.epw")
    header = (f"LOCATION,Bileca,,BIH,PVGIS,{lat:.4f},{lon:.4f},{ALTITUDE},0\n"
              "DESIGN CONDITIONS,0\nTYPICAL/EXTREME PERIODS,0\nGROUND TEMPERATURES,0\n"
              "HOLIDAYS/DAYLIGHT SAVING,No,0,0,0\nCOMMENTS 1,Generated by pvlib\nCOMMENTS 2,\n"
              "DATA PERIODS,1,1,Data,Sunday, 1/ 1,12/31\n")
    lines = []
    for ts, row in df.iterrows():
        dni = max(0.0, float(row.get('dni', 0) or 0))
        dhi = max(0.0, float(row.get('dhi', 0) or 0))
        ghi = max(0.0, float(row.get('ghi', 0) or 0))
        line = (f"{ts.year},{ts.month},{ts.day},{ts.hour},60,1,"
                "9999,9999,9999,9999,9999,9999,9999,9999,9999,9999,9999,9999,"
                "9999,9999,9999,9999,9999,9999,9999,9999,9999,9999,9999,9999,"
                f"{dni:.2f},{dhi:.2f},{ghi:.2f}\n")
        lines.append(line)
    with open(epw_path, 'w', encoding='utf-8') as f:
        f.write(header)
        f.writelines(lines)

    # 2. WEa fajl (ZA gendaymtx - ASCII + Unix \n)
    wea_path = os.path.join(RAD_BASE, "skies", "weather.wea")
    wea_lines = [f'site "Bileca" {lat:.4f} {lon:.4f} 1 {int(ALTITUDE)}',
                 'ground 0.2 0.2',
                 'date time DNI DHI']
    for ts, row in df.iterrows():
        m, d, h = ts.month, ts.day, ts.hour + 0.5
        dni = max(0.0, float(row.get('dni', 0) or 0))
        dhi = max(0.0, float(row.get('dhi', 0) or 0))
        wea_lines.append(f"{m:d} {d:d} {h:.1f} {dni:.1f} {dhi:.1f}")
        
    with open(wea_path, 'w', encoding='ascii', newline='\n') as f:
        f.write('\n'.join(wea_lines) + '\n')

    print(f"✅ EPW sačuvan ({ALTITUDE} m): {epw_path}")
    print(f"✅ WEa sačuvan (ASCII, \\n): {wea_path}")
    return epw_path, wea_path, df

# =============================================================================
# 🚀 RADIANCE SIMULACIJA
# =============================================================================
def run_radiance_simulation(wea_path):
    os.chdir(RAD_BASE)
    
    # 🧹 Čišćenje prethodnih pokušaja
    for f in ["scene.oct", "skies/annual.smx", "results/annual_irrad.txt"]:
        if os.path.exists(f): os.remove(f)
        
    sky_file = os.path.join("skies", "annual.smx")
    sky_abs = os.path.abspath(sky_file)
    wea_abs = os.path.abspath(wea_path)
    
    print("Generišem godišnji sky vektor...")
    
    # ✅ MINIMALNA SINTAKSA: radi na 99% Windows build-ova
    # -O 1 = output irradiance matrix, bez -m, -of, -y koji lome parser
    cmd = f'gendaymtx -O 1 "{wea_abs}" > "{sky_abs}"'
    print(f"🔄 Komanda: {cmd}")
    
    try:
        # shell=True je ovde nužan za ">" redirect na Windowsu
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ gendaymtx greška: {e.stderr.strip()}")
        print("💡 Proveri da li .wea fajl ima tačan format (ASCII, \\n, 8760 redova)")
        return False
    except FileNotFoundError:
        print("❌ gendaymtx nije pronađen. Dodaj Radiance\\bin u sistemski PATH.")
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
    res = subprocess.run(cmd_oconv, shell=True, capture_output=True, text=True, check=True)
    print("✅ scene.oct kreiran.")

    sensors_file = os.path.join(RAD_BASE, "objects", "sensors.txt")
    output_txt = os.path.join(RAD_BASE, "results", "annual_irrad.txt")
    n_sensors = 38
    
    # rtrace + rcalc pipeline
    cmd_rtrace = (f'rtrace -h -I -ab 5 -ad 2048 -lw 1e-5 -aa 0.1 -y {n_sensors} -n 4 "{scene_oct}" < "{sensors_file}" '
                  f'| rcalc -e "$1+$2+$3" > "{output_txt}"')
    
    print("Pokrećem rtrace... (ovo može trajati nekoliko minuta)")
    try:
        subprocess.run(cmd_rtrace, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ rtrace/rcalc greška: {e.stderr.strip() if hasattr(e, 'stderr') else 'Proveri sensors.txt format'}")
        return False
        
    print(f"✅ Rezultati sačuvani u {output_txt}")
    return True# =============================================================================
# 📊 OBRADA REZULTATA
# =============================================================================
def process_irradiance_results(weather_df):
    irrad_file = os.path.join(RAD_BASE, "results", "annual_irrad.txt")
    if not os.path.exists(irrad_file):
        print(f"❌ Fajl {irrad_file} ne postoji.")
        return

    try:
        irrad_data = np.loadtxt(irrad_file)
    except Exception as e:
        print(f"Greška pri čitanju {irrad_file}: {e}")
        return

    if irrad_data.ndim == 1:
        irrad_data = irrad_data.reshape(-1, 1)
    n_hours, n_sensors = irrad_data.shape
    print(f"Učitano {n_hours} sati, {n_sensors} senzora.")

    panel_ids = list(range(1, 20))
    cols = [f"panel_{pid}_{side}" for pid in panel_ids for side in ['front', 'back']]
    df_irr = pd.DataFrame(irrad_data, index=weather_df.index[:n_hours], columns=cols)

    panel_area = PANEL_L * PANEL_W
    module_efficiency = 0.21
    bifacial_factor = 0.80
    albedo = 0.65

    for pid in panel_ids:
        front_col = f"panel_{pid}_front"
        back_col = f"panel_{pid}_back"
        df_irr[f"P_{pid}_front"] = df_irr[front_col] * panel_area * module_efficiency
        df_irr[f"P_{pid}_back"] = df_irr[back_col] * panel_area * module_efficiency * bifacial_factor * albedo
        df_irr[f"P_{pid}_total"] = df_irr[f"P_{pid}_front"] + df_irr[f"P_{pid}_back"]

    mpls_cols = [f"P_{pid}_total" for pid in range(1, 11)]
    ran_cols = [f"P_{pid}_total" for pid in range(11, 20)]
    df_irr['MPLS_DC_W'] = df_irr[mpls_cols].sum(axis=1)
    df_irr['RAN_DC_W'] = df_irr[ran_cols].sum(axis=1)

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

    df_irr['MPLS_SoC'], df_irr['RAN_SoC'] = soc_mpls, soc_ran

    total_mpls = df_irr['MPLS_DC_W'].sum() / 1000
    total_ran = df_irr['RAN_DC_W'].sum() / 1000
    print("\n" + "="*50 + "\n📈 GODIŠNJI REZULTATI\n" + "="*50)
    print(f"MPLS sistem (10 panela): {total_mpls:,.0f} kWh DC")
    print(f"RAN sistem (9 panela):   {total_ran:,.0f} kWh DC")
    print(f"UKUPNO: {total_mpls+total_ran:,.0f} kWh DC")
    print(f"Prosečan dnevni prinos: {(total_mpls+total_ran)/(n_hours/24):.1f} kWh")
    print(f"\n🔋 Baterije (450Ah):")
    print(f"MPLS: min SoC {soc_mpls.min()*100:.1f}%, pros. SoC {soc_mpls.mean()*100:.1f}%")
    print(f"RAN:  min SoC {soc_ran.min()*100:.1f}%, pros. SoC {soc_ran.mean()*100:.1f}%")
    print(f"\n⚠️  Sati sa SoC < 15%: MPLS = {(soc_mpls<0.15).sum()} h, RAN = {(soc_ran<0.15).sum()} h")

# =============================================================================
# 🎯 MAIN
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("RURALSTAR HYBRID – RADIANCE SIMULACIJA (PVGIS)")
    print("=" * 60)
    
    try:
        lat_in = input("Unesi geografsku širinu (podrazumevano 42.9448): ").strip()
        lat = float(lat_in) if lat_in else 42.9448
        lon_in = input("Unesi geografsku dužinu (podrazumevano 18.3236): ").strip()
        lon = float(lon_in) if lon_in else 18.3236
    except ValueError:
        lat, lon = 42.9448, 18.3236

    use_tmy = input("Koristiti PVGIS TMY? (d/n, podrazumevano d): ").strip().lower() != 'n'
    if use_tmy:
        year_start = year_end = None
    else:
        try:
            year_start = int(input("Početna godina: "))
            year_end = int(input("Krajnja godina: "))
        except ValueError:
            year_start = year_end = None

    write_materials()
    write_ground_and_slab()
    write_cabinets_and_generator()
    write_panels()
    print("✅ Svi .rad fajlovi generisani.")

    df_weather, meta = fetch_weather_from_pvgis(lat, lon, year_start, year_end)
    epw_path, wea_path, df_weather = prepare_weather_files(df_weather, lat, lon)

    if run_radiance_simulation(wea_path):
        process_irradiance_results(df_weather)
    else:
        print("\n⏳ Simulacija prekinuta. Proveri da li je 'gendaymtx' u sistemskom PATH-u.")