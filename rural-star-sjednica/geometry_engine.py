import os
from typing import Dict, Any, Optional
from logger import log_info, log_success, log_warning

def generate_geometry_files(config: Dict[str, Any], equipment: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """
    Generiše Radiance .rad fajlove za scenu.
    Konfiguracija: 12x Huawei 540W, 2x Standard Ground Mount, Južna orijentacija, 45° nagib.
    """
    log_info("Generišem 3D geometriju za Radiance...")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    rad_dir = os.path.join(base_path, 'radiance_objects')
    os.makedirs(rad_dir, exist_ok=True)
    
    try:
        # Parametri iz konfiguracije
        sys_params = equipment.get('system_parameters', {})
        tilt = sys_params.get('tilt_angle', 45.0)
        azimuth = sys_params.get('azimuth_angle', 180.0) # Jug
        altitude = sys_params.get('altitude', 107)
        
        panel_specs = equipment['panels']['Huawei_IPV540-M1A']
        p_width = panel_specs['dimensions_mm'][1] / 1000.0 # 1.134m
        p_height = panel_specs['dimensions_mm'][0] / 1000.0 # 2.279m
        clearance = sys_params.get('module_clearance_height', 0.5)
        
        # Scenarij A: 12 panela raspoređenih u 2 reda po 6 (2 nosača)
        n_panels_total = 12
        rows = 2
        cols_per_row = 6
        row_spacing = 3.0 # Razmak između redova da se izbjegne sjena
        
        # Kreiranje materijala
        mat_content = f"""# Materijali za Sjednicu (Altitude: {altitude}m)
void plastic ground_mat
0
0
5 0.40 0.40 0.30 0 0

void plastic steel_mount
0
0
5 0.60 0.60 0.60 0 0

void glass pv_module_glass
0
0
3 0.90 0.90 0.90
"""
        with open(os.path.join(rad_dir, 'materials.mat'), 'w') as f:
            f.write(mat_content)
            
        # Kreiranje tla
        ground_content = """# Tlo (Ground Plane)
ground_mat polygon ground_plane
0
0
12
-20 -20 0
20 -20 0
20 20 0
-20 20 0
"""
        with open(os.path.join(rad_dir, 'ground.rad'), 'w') as f:
            f.write(ground_content)
            
        # Kreiranje panela i nosača
        panels_content = f"# Paneli i Nosači (Tilt: {tilt}°, Azimuth: {azimuth}°)\n"
        
        import math
        rad_tilt = math.radians(tilt)
        rad_az = math.radians(azimuth)
        
        # Sinus i kosinus za rotaciju
        sin_t = math.sin(rad_tilt)
        cos_t = math.cos(rad_tilt)
        sin_a = math.sin(rad_az)
        cos_a = math.cos(rad_az)
        
        panel_id = 0
        for r in range(rows):
            for c in range(cols_per_row):
                panel_id += 1
                
                # Pozicija centra panela u lokalnom sistemu (prije rotacije)
                # X ide duž nosača (širina panela), Y ide uz nagib (visina panela)
                # Centriranje niza
                x_offset = (c - (cols_per_row - 1) / 2.0) * p_width
                y_offset = (r - (rows - 1) / 2.0) * row_spacing
                
                # Donji rub panela je na visini 'clearance'
                # Centar panela po Y osi (duž nagiba) je na clearance + (p_height * cos_t) / 2 ? 
                # Ne, centar panela u lokalnom sistemu (0,0) će se rotirati.
                # Definišemo temena panela u lokalnom sistemu (X, Y, Z) gdje je panel u ravni Z=0
                # Temena: BL, BR, TR, TL
                w2, h2 = p_width / 2.0, p_height / 2.0
                local_verts = [
                    (-w2, -h2, 0), (w2, -h2, 0), (w2, h2, 0), (-w2, h2, 0)
                ]
                
                global_verts = []
                for lx, ly, lz in local_verts:
                    # 1. Rotacija oko X ose (Nagib)
                    # y' = y*cos - z*sin, z' = y*sin + z*cos
                    ry = ly * cos_t - lz * sin_t
                    rz = ly * sin_t + lz * cos_t
                    
                    # 2. Rotacija oko Z ose (Azimut)
                    # x'' = x*cos(a) - y'*sin(a) ... Čekaj, azimut 0 je Sjever (Y+). 
                    # Azimut 180 je Jug (Y-). 
                    # Standardna rotacija u Radianceu: X=East, Y=North.
                    # Rotacija za ugao A od Y ose u smjeru kazaljke:
                    # x_new = x * sin(A) + y * cos(A) ?? 
                    # Koristimo standardnu matricu rotacije oko Z za ugao theta = 90 - Azimut?
                    # Najsigurnije: Vektor normale.
                    # Normala (0, 1, 0) nakon nagiba postaje (0, cos_t, sin_t).
                    # Rotiramo tu normalu za azimut.
                    
                    # Jednostavnija transformacija koordinata:
                    # X_global = x_offset + lx * cos_a - ry * sin_a
                    # Y_global = y_offset + lx * sin_a + ry * cos_a
                    # Ovo pretpostavlja da je azimut mjeren od X ose. 
                    # Za azimut od Sjevera (Y):
                    # Ugao od X ose = 90 - Azimut.
                    theta = math.radians(90) - rad_az
                    cos_th = math.cos(theta)
                    sin_th = math.sin(theta)
                    
                    gx = x_offset + lx * cos_th - ry * sin_th
                    gy = y_offset + lx * sin_th + ry * cos_th
                    gz = clearance + rz # Podizanje od tla
                    
                    global_verts.append((gx, gy, gz))
                
                # Upis poligona
                pname = f"panel_{panel_id}"
                panels_content += f"pv_module_glass polygon {pname}\n0\n0\n12\n"
                for vx, vy, vz in global_verts:
                    panels_content += f"  {vx:.4f} {vy:.4f} {vz:.4f}\n"
                
                # Dodavanje jednostavnog nosača (stubovi na uglovima)
                # ... (može se dodati kasnije za detaljniju sjenu)

        with open(os.path.join(rad_dir, 'panels.rad'), 'w') as f:
            f.write(panels_content)
            
        log_success(f"Geometrija generisana: {panel_id} panela u {rad_dir}")
        return {
            'materials': os.path.join(rad_dir, 'materials.mat'),
            'ground': os.path.join(rad_dir, 'ground.rad'),
            'panels': os.path.join(rad_dir, 'panels.rad'),
            'scene_dir': rad_dir
        }
    
    except Exception as e:
        log_error(f"Greška pri generisanju geometrije: {e}")
        return None