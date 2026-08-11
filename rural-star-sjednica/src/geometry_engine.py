import os
import math
import subprocess
from typing import Dict, Any, cast, List
from logger import log_info, log_success


def _gen_box(material: str, name: str, x0: float, y0: float, z0: float,
             sx: float, sy: float, sz: float) -> str:
    """
    Build an axis-aligned box via Radiance's own genbox + xform, rather than a
    hand-written 'box' primitive - Radiance has no built-in box primitive, only
    polygon/sphere/cylinder/etc, so 'material box name ...' is invalid syntax and
    fails at oconv (found 2026-08-08 running this for the first time with Radiance
    actually installed). genbox emits real polygons from (0,0,0) to (sx,sy,sz);
    xform -t translates it to the box's origin corner.
    """
    box = subprocess.run(
        ["genbox", material, name, f"{sx}", f"{sy}", f"{sz}"],
        capture_output=True, text=True, check=True).stdout
    placed = subprocess.run(
        ["xform", "-t", f"{x0}", f"{y0}", f"{z0}"],
        input=box, capture_output=True, text=True, check=True).stdout
    return placed


def generate_geometry_files(config: Dict[str, Any], equipment: Dict[str, Any]):
    """
    Konačna geometrija - Huawei Standard 3.0 (2-High Portrait):
    - Jedna kompaktna konstrukcija sa 12 panela (2 reda po 6).
    - Paneli u redu su jedan iznad drugog (leđa uz leđa po visini).
    - Sve je južno od stuba/kontejnera.
    - Sjeverna (najviša) ivica cijelog sistema je tik uz temelj.
    """
    log_info("📐 Konstruisanje: Huawei Standard 3.0 (2-High Portrait, 2x6 panela)...")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    scene_path = os.path.join(base_path, 'radiance_scene')
    os.makedirs(scene_path, exist_ok=True)

    # Dimenzije Huawei 585W panela (iPV585-M2A) - stvarni modul u ovoj izvedbi;
    # blok od 12 panela (2 reda x 6 kolona) je pojednostavljena reprezentacija za
    # proračun samozasjenjenja, nezavisna od stvarnog broja nosača (3 x 4 modula,
    # svi u istom nizu bez preklapanja sjever-jug) - v. cad/design.json.
    panel_dims = equipment['panels']['Huawei_IPV585-M2A']['dimensions_mm']
    pw = float(panel_dims[1]) / 1000.0  # Širina (~1.134m)
    ph = float(panel_dims[0]) / 1000.0  # Visina (~2.278m)

    tilt = float(config.get('site_config', config).get('tilt_angle', 45.0))
    tilt_rad = math.radians(tilt)

    # Projekcija JEDNOG panela
    dy = ph * math.cos(tilt_rad)
    dz = ph * math.sin(tilt_rad)

    # Projekcija CIJELOG sistema (2 panela po visini)
    total_dy = 2 * dy
    total_dz = 2 * dz
    clearance = 1.5 # Donja ivica panela - v. review/07-calculations.md F.6 (3x4 redizajn)

    rad_content = [
        "# Materijali",
        "void plastic panel_mat 0 0 5 0.1 0.1 0.1 0.05 0.1",
        "void plastic steel_mat 0 0 5 0.6 0.6 0.6 0.1 0.0",
        "void plastic concrete_mat 0 0 5 0.6 0.6 0.6 0.0 0.0"
    ]

    # 1. SJEVERNI OBJEKTI (Temelj, Stub, Kontejner)
    rad_content.append("\n# Temelj")
    rad_content.append(_gen_box("concrete_mat", "foundation", -2.9, -2.9, 0, 5.8, 5.8, 0.2))
    rad_content.append("\n# Stub")
    rad_content.append(_gen_box("steel_mat", "tower_base", -2.835, -2.835, 0.2, 5.67, 5.67, 5.0))
    rad_content.append("\n# Kontejner")
    rad_content.append(_gen_box("concrete_mat", "container", -1.5, -1.1, 0.2, 3.0, 2.2, 2.4))

    # 2. KOMPAKTNI SISTEM PANELA (2 reda po 6)
    panels_per_row = 6
    row_width = panels_per_row * pw
    start_x = -row_width / 2
    
    # Pozicioniranje: Najviša ivica (sjeverna) je na Y = -3.0
    y_top_limit = -3.0
    y_bottom_limit = y_top_limit - total_dy

    # Glavne noseće šine (Rails) - idu ispod cijelog sistema
    # Postavljamo 3 šine: dole, sredina (spoj panela), gore
    for rail_pos in [0.1, 1.0, 1.9]: # Pozicije u odnosu na visinu panela
        ry = y_bottom_limit + (rail_pos * dy)
        rz = clearance + (rail_pos * dz)
        rad_content.append(_gen_box("steel_mat", f"rail_{rail_pos}".replace(".", "_"),
                                     start_x, ry, rz - 0.05, row_width, 0.06, 0.06))

    # Paneli: r=0 je donji (južni), r=1 je gornji (sjeverni)
    for r in range(2):
        y_low = y_bottom_limit + (r * dy)
        z_low = clearance + (r * dz)
        
        for p in range(panels_per_row):
            cx = start_x + (p * pw)
            name = f"panel_row{r}_{p}"
            rad_content.append(f"\npanel_mat polygon {name}\n0 0 12")
            # Donje tačke reda
            rad_content.append(f"  {cx:.3f} {y_low:.3f} {z_low:.3f}")
            rad_content.append(f"  {cx + pw:.3f} {y_low:.3f} {z_low:.3f}")
            # Gornje tačke reda
            rad_content.append(f"  {cx + pw:.3f} {y_low + dy:.3f} {z_low + dz:.3f}")
            rad_content.append(f"  {cx:.3f} {y_low + dy:.3f} {z_low + dz:.3f}")

    output_file = os.path.join(scene_path, 'objects.rad')
    with open(output_file, 'w') as f:
        f.write("\n".join(rad_content))

    # Center point and outward normal of the panel field, for the caller's sensor
    # placement - computed from the same geometry as the panels themselves, not a
    # separately hardcoded guess (found 2026-08-08: the previous hardcoded sensor
    # at z=0.5m sat below the entire panel field once clearance was raised to 1.5m).
    center = (0.0, y_top_limit - total_dy / 2.0, clearance + total_dz / 2.0)
    normal = (0.0, -math.sin(tilt_rad), math.cos(tilt_rad))

    log_success(f"✅ Geometrija završena: 2x6 panela u kompaktnom bloku južno od stuba.")
    return output_file, {"center": center, "normal": normal}

def generate_sensor_points(panels_geostats: List[Dict[str, Any]]) -> str:
    """
    Kreira fajl sa koordinatama (X Y Z) i vektorima (nX nY nZ) 
    za svaki panel (prednja i zadnja strana).
    """
    sensors_path = "radiance_scene/sensors.pts"
    with open(sensors_path, "w") as f:
        for p in panels_geostats:
            # Centar panela
            cx, cy, cz = p['center']
            nx, ny, nz = p['normal'] # Normala prednje strane
            
            # Prednja strana
            f.write(f"{cx} {cy} {cz} {nx} {ny} {nz}\n")
            # Zadnja strana (obrnuta normala za bifacijalni dobitak)
            f.write(f"{cx} {cy} {cz} {-nx} {-ny} {-nz}\n")
            
    return sensors_path