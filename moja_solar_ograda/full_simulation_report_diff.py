#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RURALSTAR HYBRID – FINALNA SIMULACIJA (KONSOLIDOVANA VERZIJA)
✅ Fix: WEa format, Subprocess pipeline, Varijable, Geometrija
"""
import os
import sys
import subprocess
import numpy as np
import pandas as pd
from math import cos, sin, radians, sqrt
import pvlib
from pvlib import solarposition, irradiance
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# =============================================================================
# 📁 KONFIGURACIJA I PUTANJE
# =============================================================================
PROJECT_ROOT = r"E:\Radiance_build\moja_solar_ograda"
SIM_NAME = "sjednica_bileca_irradiance_outward_max"
RAD_BASE = os.path.join(PROJECT_ROOT, SIM_NAME)

# Kreiranje foldera
for sub in ["materials", "objects", "skies", "results", "EPWs"]:
    os.makedirs(os.path.join(RAD_BASE, sub), exist_ok=True)

# Parametri lokacije i sistema
LAT_REF = 42.9448
LON_REF = 18.3236
ALTITUDE = 1050.0
ALBEDO = 0.20  # Standardni albedo za WEa

# Panel dimenzije
PANEL_L = 2.279  # Dužina (visina kada stoji)
PANEL_W = 1.134  # Širina
TILT_DEG = 16.0
Z_LOWER = 0.5

# Raspored strana (MPLS: Jug/Istok-Zapad, RAN: Sjever/Istok-Zapad)
# Azimuti: 135 (SE), 225 (SW), 45 (NE), 315 (NW)
SIDES_CONFIG = [
    {"name": "MPLS_SE", "az": 135, "count": 5},
    {"name": "MPLS_SW", "az": 225, "count": 5},
    {"name": "RAN_NE",  "az": 45,  "count": 5},
    {"name": "RAN_NW",  "az": 315, "count": 4},
]

# GPS Uglovi (za lokalne koordinate)
GPS_CORNERS = [
    (42.94483338639821, 18.323625614573174),  # N
    (42.94480147615224, 18.323706763917354),  # E
    (42.94475532899798, 18.323639027687914),  # S
    (42.944790675757524, 18.323571291458475), # W
]

# =============================================================================
# ✍️ POMOĆNE FUNKCIJE ZA PISANJE FAJLOVA
# =============================================================================
def write_file(path, content):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)

def generate_materials():
    mat_content = """# RuralStar Materials
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
    write_file(os.path.join(RAD_BASE, "materials", "materials.mat"), mat_content)

def generate_geometry():
    # 1. Lokalne koordinate
    m_per_deg_lat = 111320.0
    m_per_deg_lon = 111320.0 * cos(radians(LAT_REF))
    
    local_pts = []
    for lat, lon in GPS_CORNERS:
        x = (lon - LON_REF) * m_per_deg_lon
        y = (lat - LAT_REF) * m_per_deg_lat
        local_pts.append((x, y))
    
    # Centriranje
    cx = sum(p[0] for p in local_pts) / 4
    cy = sum(p[1] for p in local_pts) / 4
    corners_local = [(p[0]-cx, p[1]-cy) for p in local_pts]
    
    # 2. Tlo i Ploča
    ground_rad = "# Ground\nground_mat polygon ground\n0\n0\n12\n"
    for x, y in [(-8,-8), (8,-8), (8,8), (-8,8)]:
        ground_rad += f"  {x:.3f} {y:.3f} 0\n"
    write_file(os.path.join(RAD_BASE, "objects", "ground.rad"), ground_rad)
    
    slab_rad = "# Concrete Slab\nconcrete_mat polygon slab\n0\n0\n12\n"
    for x, y in corners_local:
        slab_rad += f"  {x:.3f} {y:.3f} 0\n"
    write_file(os.path.join(RAD_BASE, "objects", "slab.rad"), slab_rad)
    
    # 3. Kabineti (pojednostavljeno)
    cab_rad = "# Cabinets\ncabinet_mat polygon mts\n0\n0\n12\n"
    # Jednostavan box za MTS
    bx, by, bz = -0.7, -2.0, 0.2
    bw, bd, bh = 0.65, 0.65, 1.6
    verts = [(bx,by,bz), (bx+bw,by,bz), (bx+bw,by+bd,bz), (bx,by+bd,bz),
             (bx,by,bz+bh), (bx+bw,by,bz+bh), (bx+bw,by+bd,bz+bh), (bx,by+bd,bz+bh)]
    faces = [(0,1,2,3), (4,5,6,7), (0,3,7,4), (1,2,6,5), (0,4,5,1), (3,7,6,2)]
    for f in faces:
        cab_rad += f"cabinet_mat polygon mts_face_{f[0]}\n0\n0\n12\n"
        for idx in f:
            v = verts[idx]
            cab_rad += f"  {v[0]:.3f} {v[1]:.3f} {v[2]:.3f}\n"
    write_file(os.path.join(RAD_BASE, "objects", "cabinets.rad"), cab_rad)

    # 4. Paneli i Senzori
    panels_rad = "# Panels\n"
    sensors_txt = ""
    
    tilt_rad = radians(TILT_DEG)
    vert_proj = PANEL_L * cos(tilt_rad)
    scale_factor = 7.0 / 5.8  # Omjer donjeg i gornjeg okvira
    
    panel_id = 0
    for side in SIDES_CONFIG:
        az = side["az"]
        count = side["count"]
        az_rad = radians(az)
        
        # Određivanje ivice okvira na osnovu azimuta
        # 135 (SE) -> između Istok(1) i Jug(2) indeksa u listi corners_local? 
        # Naša lista: 0:N, 1:E, 2:S, 3:W
        if az == 135: p1, p2 = corners_local[1], corners_local[2] # E-S
        elif az == 225: p1, p2 = corners_local[2], corners_local[3] # S-W
        elif az == 45: p1, p2 = corners_local[0], corners_local[1] # N-E
        elif az == 315: p1, p2 = corners_local[3], corners_local[0] # W-N
        else: continue
        
        # Gornji okvir (originalne koordinate)
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        length = sqrt(dx*dx + dy*dy)
        if length == 0: continue
        ux, uy = dx/length, dy/length # Vektor duž ivice
        
        # Donji okvir (skaliran prema unutra za 7.0/5.8 faktor ako je potrebno, 
        # ali ovdje koristimo geometriju nagiba)
        # Za trapeznu ogradu: donji okvir je širi. 
        # Koordinatni sistem: centar je 0,0. 
        # Skaliramo poziciju sredine donjeg dijela ako je potrebno, 
        # ali ovdje ćemo jednostavno projicirati panel.
        
        # Pretpostavka: Gornji okvir je 5.8m, Donji je 7.0m.
        # Sredina strane se pomjera.
        lp1 = (p1[0] * scale_factor, p1[1] * scale_factor)
        lp2 = (p2[0] * scale_factor, p2[1] * scale_factor)
        low_mid_x = (lp1[0] + lp2[0]) / 2
        low_mid_y = (lp1[1] + lp2[1]) / 2
        
        start_offset = -(count - 1) * PANEL_W / 2
        
        for i in range(count):
            panel_id += 1
            offset = start_offset + i * PANEL_W
            
            # Pozicija centra panela
            up_x = mid_x + offset * ux
            up_y = mid_y + offset * uy
            low_x = low_mid_x + offset * ux
            low_y = low_mid_y + offset * uy
            
            cen_x = (up_x + low_x) / 2
            cen_y = (up_y + low_y) / 2
            cen_z = Z_LOWER + vert_proj / 2
            
            # Generisanje poligona panela
            # Lokalni koordinatni sistem panela prije rotacije
            w2, h2 = PANEL_W / 2, PANEL_L / 2
            # Temena: BL, BR, TR, TL (u lokalnom sistemu gdje je Y visina panela)
            # Ali mi želimo da nagib bude oko X ose (donja ivica niže)
            # Definišemo temena u ravni panela (z=0), pa rotiramo
            
            # Redoslijed temena za Radiance polygon: A B C D
            # Donja lijeva, Donja desna, Gornja desna, Gornja lijeva (gledano sprijeda)
            local_pts_panel = [
                (-w2, -h2, 0), (w2, -h2, 0), (w2, h2, 0), (-w2, h2, 0)
            ]
            
            # Rotacija oko X ose (nagib)
            ct, st = cos(tilt_rad), sin(tilt_rad)
            # Nagib prema van znači da se vrh pomiče u smjeru normale strane
            # Normala strane (azimut) je (sin(az), cos(az)).
            # Rotacija: y' = y*cos - z*sin, z' = y*sin + z*cos
            # Ovdje je 'y' u lokalnom sistemu panela zapravo visina (h2)
            
            rotated_pts = []
            for (x, y, z) in local_pts_panel:
                # 1. Rotacija nagiba (oko lokalne X ose)
                # y je duž panela (od -h2 do h2). Želimo da -h2 bude dole, h2 gore.
                # Ako je nagib 16 od vertikale, to znači da je panel nagnut nazad.
                # Standardna rotacija:
                ry = y * ct - z * st
                rz = y * st + z * ct
                xr, yr, zr = x, ry, rz
                
                # 2. Rotacija azimuta (oko globalne Z ose)
                # Azimut 0 je Sjever (Y osa). Azimut 90 je Istok (X osa).
                # Naša formula za azimut: 0=N, 90=E.
                # Rotacija: x'' = x'*cos - y'*sin, y'' = x'*sin + y'*cos
                # Ali azimut u Radianceu je od Sjevera u smjeru kazaljke.
                ca, sa = cos(az_rad), sin(az_rad)
                # Pažnja: koordinatni sistem. X=East, Y=North.
                # Azimut 90 (East) -> normala (1, 0). 
                # Rotacija tačke (xr, yr):
                xf = xr * ca - yr * sa # Ovo rotira za -az? 
                # Probajmo obrnuto za standardni azimut (od Y ose):
                # x_new = x * sin(az) + y * cos(az) ? Ne.
                # Standardna rotacija u XY ravni za ugao theta od X ose:
                # Mi imamo azimut od Y (Sjever). 
                # Ugao od X ose = 90 - az.
                # Hajde da koristimo vektor orijentacije.
                # Normala panela treba da gleda pod azimutom 'az'.
                # Ako je panel u ravni YZ (az=0), normala je (0,1,0).
                # Rotiramo oko Z za (90-az)?
                # Jednostavnije: Rotirajmo koordinate tako da se Y osa poklopi sa azimutom.
                # x' = x * cos(90-az) - y * sin(90-az) ... komplikovano.
                
                # Koristimo direktnu transformaciju:
                # Globalni X = x_local * cos(az) - y_local * sin(az) ? Ne.
                # Azimut 0 (N): X=0, Y=1. 
                # Azimut 90 (E): X=1, Y=0.
                # Transformacija: 
                # Xg = xr * sin(az) + yr * cos(az)
                # Yg = xr * cos(az) - yr * sin(az) ? 
                # Provjera: xr=0, yr=1 (vrh panela koji gleda na N). Xg=0, Yg=1. OK.
                # xr=1, yr=0 (desna strana panela koji gleda na N). Xg=1, Yg=0. To je Istok. OK.
                
                Xg = xr * sa + yr * ca
                Yg = xr * ca - yr * sa # Obrnuto predznake? 
                # Probajmo standardnu rotaciju za ugao fi od Y ose u smjeru kazaljke:
                # x' = x cos(fi) + y sin(fi) ??
                # Hajde da koristimo gotovu logiku iz prethodnog koda koja je radila vizuelno:
                # x_rot = x * cos(az) - y * sin(az) (ovo je rotacija od X ose)
                # Ako je az=90 (Istok), cos=0, sin=1. x' = -y. 
                # Ako je panel okrenut istoku, njegova "prednja" strana je +X.
                
                # Ispravna logika za azimut od Sjevera (Y):
                # X_global = x_local * cos(az_rad) - y_local * sin(az_rad) -> NE
                # Koristimo: 
                X_final = xr * sin(az_rad) + yr * cos(az_rad)
                Y_final = xr * cos(az_rad) - yr * sin(az_rad) # Ovo možda treba minus
                
                # Hajde da pojednostavimo: koristimo vektore.
                # Vektor "gore" u lokalnom sistemu je (0, 1, 0) prije nagiba.
                # Vektor "desno" je (1, 0, 0).
                # Nakon nagiba (rotacija oko X): Gore = (0, ct, st).
                # Rotacija oko Z za azimut (od Sjevera, u smjeru kazaljke):
                # Rz = [[cos(90-az), -sin(90-az)], [sin(90-az), cos(90-az)]] ?
                # Azimut 0 (N): cos(90)=0, sin(90)=1. Matrica: [[0, -1], [1, 0]].
                # (x,y) -> (-y, x). To je rotacija za 90 stepeni. 
                # Ako je vektor (0,1) (Sjever), postaje (-1, 0) (Zapad). GREŠKA.
                
                # KORISTIMO OVO (provjereno u prethodnim iteracijama):
                # az_rad je od Sjevera u smjeru kazaljke.
                # x_new = x * cos(theta) - y * sin(theta) gdje je theta od X ose.
                # Theta = 90 - az.
                theta = radians(90) - az_rad
                ca_t, sa_t = cos(theta), sin(theta)
                Xf = xr * ca_t - yr * sa_t
                Yf = xr * sa_t + yr * ca_t
                
                rotated_pts.append((Xf + cen_x, Yf + cen_y, zr + cen_z))
            
            # Upis panela
            pname = f"panel_{panel_id}"
            panels_rad += f"panel_glass polygon {pname}\n0\n0\n12\n"
            for p in rotated_pts:
                panels_rad += f"  {p[0]:.4f} {p[1]:.4f} {p[2]:.4f}\n"
            
            # Senzori (Front i Back)
            # Normala panela: u lokalnom sistemu (0, 1, 0) -> nakon nagiba (0, ct, st)
            # Nakon rotacije azimuta:
            nx_l, ny_l, nz_l = 0.0, ct, st
            Nx = nx_l * ca_t - ny_l * sa_t
            Ny = nx_l * sa_t + ny_l * ca_t
            Nz = nz_l
            
            # Front sensor (pomaknut za 1cm u smjeru normale)
            sensors_txt += f"{cen_x + 0.01*Nx:.4f} {cen_y + 0.01*Ny:.4f} {cen_z + 0.01*Nz:.4f} {Nx:.4f} {Ny:.4f} {Nz:.4f}\n"
            # Back sensor (suprotno)
            sensors_txt += f"{cen_x - 0.01*Nx:.4f} {cen_y - 0.01*Ny:.4f} {cen_z - 0.01*Nz:.4f} {-Nx:.4f} {-Ny:.4f} {-Nz:.4f}\n"

    write_file(os.path.join(RAD_BASE, "objects", "panels.rad"), panels_rad)
    write_file(os.path.join(RAD_BASE, "objects", "sensors.txt"), sensors_txt)
    return panel_id

# =============================================================================
# 🌤️ VREMENSKI PODACI
# =============================================================================
def get_weather_data():
    print("🌍 Preuzimam PVGIS TMY podatke...")
    try:
        df, meta = pvlib.iotools.get_pvgis_tmy(LAT_REF, LON_REF, map_variables=True)
        print(f"✅ Podaci preuzeti: {len(df)} sati.")
        return df
    except Exception as e:
        print(f"❌ Greška pri preuzimanju: {e}")
        # Fallback na dummy podatke ako mreža ne radi (za test)
        print("⚠️ Kreiram dummy podatke za test...")
        dates = pd.date_range(start="2023-01-01", periods=8760, freq="h")
        df = pd.DataFrame(index=dates)
        df['ghi'] = 0.0
        df['dni'] = 0.0
        df['dhi'] = 0.0
        df['temp_air'] = 20.0
        return df

def create_wea_file(df):
    wea_path = os.path.join(RAD_BASE, "skies", "weather.wea")
    lines = [
        f'site "Bileca" {LAT_REF:.4f} {LON_REF:.4f} 1 {int(ALTITUDE)}',
        f'ground {ALBEDO:.2f}',
        'date time DNI DHI'
    ]
    
    # Priprema podataka (popunjavanje nedostajućih vrijednosti)
    df = df.copy()
    if 'dni' not in df.columns or df['dni'].isna().any():
        solpos = solarposition.get_solarposition(df.index, LAT_REF, LON_REF)
        df['zenith'] = solpos['apparent_zenith']
        disc = irradiance.disc(df['ghi'], df['zenith'], df.index)
        df['dni'] = disc['dni'].fillna(0).clip(lower=0)
        df['dhi'] = (df['ghi'] - df['dni'] * np.cos(np.radians(df['zenith']))).clip(lower=0)
    
    for ts in df.index:
        row = df.loc[ts]
        # Format: M D HH.MMM DNI DHI
        # HH.MMM: sat + minut/60. Za satne podatke koristi se sat + 0.5 (sredina sata)
        hour_dec = ts.hour + 0.5
        dni = max(0.0, float(row.get('dni', 0) or 0))
        dhi = max(0.0, float(row.get('dhi', 0) or 0))
        lines.append(f"{ts.month} {ts.day} {hour_dec:.1f} {dni:.1f} {dhi:.1f}")
    
    content = "\n".join(lines)
    with open(wea_path, 'w', encoding='ascii', newline='\n') as f:
        f.write(content)
    
    print(f"✅ WEa fajl kreiran: {wea_path} ({len(lines)} linija)")
    return wea_path

# =============================================================================
# ☀️ RADIANCE SIMULACIJA (FIXED PIPELINE)
# =============================================================================
def run_radiance(wea_path):
    os.chdir(RAD_BASE)
    
    sky_file = os.path.join("skies", "annual.smx")
    oct_file = os.path.join("scene.oct")
    res_file = os.path.join("results", "annual_irrad.txt")
    sensors_file = os.path.join("objects", "sensors.txt")
    
    # 1. Gendaymtx
    print("☀️ Generišem sky vektor (gendaymtx)...")
    # Komanda kao lista, bez shell=True, bez redirecta
    cmd_sky = ["gendaymtx", "-O", "1", wea_path]
    
    try:
        with open(sky_file, 'w') as f_out:
            proc = subprocess.run(cmd_sky, stdout=f_out, stderr=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.strip() if e.stderr else "Nepoznata greška"
        print(f"❌ gendaymtx greška: {err_msg}")
        
        # Dijagnostika
        if os.path.exists(wea_path):
            with open(wea_path, 'r') as f:
                first_lines = [next(f) for _ in range(5)]
            print("   📄 WEa sadržaj (prvih 5 linija):")
            for l in first_lines: print(f"      {l.strip()}")
        return False
    except FileNotFoundError:
        print("❌ gendaymtx nije pronađen! Provjeri PATH varijablu.")
        return False

    # 2. Oconv
    print("🏗️ Kompajliram scenu (oconv)...")
    mats = os.path.join("materials", "materials.mat")
    objs = [
        os.path.join("objects", "ground.rad"),
        os.path.join("objects", "slab.rad"),
        os.path.join("objects", "cabinets.rad"),
        os.path.join("objects", "panels.rad")
    ]
    cmd_oct = ["oconv", mats] + objs
    
    try:
        with open(oct_file, 'w') as f_out:
            subprocess.run(cmd_oct, stdout=f_out, check=True)
    except Exception as e:
        print(f"❌ oconv greška: {e}")
        return False

    # 3. Rtrace + Rcalc
    print("🔦 Računam irradijancu (rtrace)...")
    # Broj senzora
    n_sensors = sum(s["count"] for s in SIDES_CONFIG) * 2 # front + back
    
    cmd_rtrace = [
        "rtrace", "-h", "-I", "-ab", "5", "-ad", "2048", "-lw", "1e-5", 
        "-aa", "0.1", "-y", str(n_sensors), "-n", "4", oct_file
    ]
    
    cmd_rcalc = ["rcalc", "-e", "$1+$2+$3"]
    
    try:
        with open(sensors_file, 'r') as f_in, \
             open(res_file, 'w') as f_out:
            
            # Pokreni rtrace
            p1 = subprocess.Popen(cmd_rtrace, stdin=f_in, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Pokreni rcalc
            p2 = subprocess.Popen(cmd_rcalc, stdin=p1.stdout, stdout=f_out, stderr=subprocess.PIPE)
            
            p1.stdout.close() # Allow p1 to receive SIGPIPE if p2 exits.
            _, err2 = p2.communicate()
            
            if p2.returncode != 0:
                raise Exception(err2.decode('utf-8', errors='ignore'))
                
    except Exception as e:
        print(f"❌ rtrace/rcalc greška: {e}")
        return False

    print(f"✅ Simulacija uspješna! Rezultati: {res_file}")
    return True

# =============================================================================
# 📊 ANALIZA REZULTATA
# =============================================================================
def analyze_results(weather_df):
    res_file = os.path.join(RAD_BASE, "results", "annual_irrad.txt")
    if not os.path.exists(res_file):
        print("❌ Rezultati ne postoje za analizu.")
        return

    print("📊 Obrađujem rezultate...")
    data = np.loadtxt(res_file)
    if data.ndim == 1: data = data.reshape(-1, 1)
    
    n_hours, n_sensors = data.shape
    n_panels = len(SIDES_CONFIG) # Ukupno panela? Ne, suma count.
    total_panels = sum(s["count"] for s in SIDES_CONFIG)
    
    # Reshape: svaki panel ima 2 senzora (front, back)
    # Data shape: (hours, panels*2)
    if n_sensors != total_panels * 2:
        print(f"⚠️ Upozorenje: Očekivano {total_panels*2} senzora, dobijeno {n_sensors}")
        # Prilagodi ako je moguće, inače nastavi
        total_panels = n_sensors // 2

    panel_area = PANEL_L * PANEL_W
    eff = 0.21
    bifaciality = 0.80
    
    results_summary = []
    total_kwh = 0.0
    
    for i in range(total_panels):
        idx_front = i * 2
        idx_back = i * 2 + 1
        
        irr_front = data[:, idx_front] # W/m2
        irr_back = data[:, idx_back]   # W/m2
        
        # Snaga (W)
        p_front = irr_front * panel_area * eff
        p_back = irr_back * panel_area * eff * bifaciality # Albedo već uračunat u raytracing? 
        # Napomena: rtrace vraća irradijancu na površinu. Ako je ground reflectance postavljen, 
        # back irradiance već uključuje odbijeno svjetlo. Bifaciality faktor se primjenjuje na efikasnost ćelije.
        # Dakle: P_back = Irr_back * Area * Eff_Cell_Bifacial? 
        # Standard: P_total = (Irr_front * Eff_front + Irr_back * Eff_back) * Area
        # Eff_back = Eff_front * Bifaciality.
        
        p_total = p_front + p_back
        
        # Energija (kWh)
        e_kwh = np.sum(p_total) / 1000.0 # Suma Watt-sati / 1000
        total_kwh += e_kwh
        
        results_summary.append(e_kwh)

    print("\n" + "="*60)
    print("📈 REZULTATI PROIZVODNJE")
    print("="*60)
    print(f"Ukupno panela: {total_panels}")
    print(f"Ukupno sati: {n_hours}")
    print(f"UKUPNA GODIŠNJA PROIZVODNJA: {total_kwh:,.1f} kWh")
    print(f"Specifična proizvodnja: {total_kwh/(total_panels*585/1000):,.1f} kWh/kWp")
    print("="*60)
    
    # Generisanje jednostavnog izvještaja
    report_path = os.path.join(RAD_BASE, "results", "izvjestaj.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"RURALSTAR HYBRID - IZVJEŠTAJ\n")
        f.write(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"Lokacija: {LAT_REF}, {LON_REF}\n")
        f.write(f"Ukupna proizvodnja: {total_kwh:,.1f} kWh\n\n")
        f.write("Detalji po panelima (kWh):\n")
        for i, e in enumerate(results_summary):
            f.write(f"Panel {i+1}: {e:.2f} kWh\n")
    
    print(f"📄 Detaljan izvještaj sačuvan: {report_path}")

# =============================================================================
# 🚀 MAIN
# =============================================================================
if __name__ == "__main__":
    print("="*60)
    print("RURALSTAR HYBRID – KOMPLETNA SIMULACIJA")
    print("="*60)
    
    # 1. Geometrija
    print("\n🏗️ Generišem geometriju...")
    n_panels = generate_geometry()
    print(f"✅ Generisano {n_panels} panela.")
    
    # 2. Materijali
    generate_materials()
    
    # 3. Vrijeme
    weather_df = get_weather_data()
    wea_path = create_wea_file(weather_df)
    
    # 4. Simulacija
    if run_radiance(wea_path):
        # 5. Analiza
        analyze_results(weather_df)
        print("\n✅ SIMULACIJA ZAVRŠENA.")
    else:
        print("\n❌ SIMULACIJA PREKINUTA.")