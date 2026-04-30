import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import json
import os
from logger import log_info, log_success, log_error, log_warning


def load_config():
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    with open(os.path.join(base_path, 'site_config.json'), 'r') as f:
        site = json.load(f)
        
    with open(os.path.join(base_path, 'equipment_db.json'), 'r') as f:
        equip = json.load(f)
        
    return site, equip

def plot_layout(site, equip):
    log_info("Generišem detaljan sistemski layout (Kontejner, Ograda, Paneli)...")
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # --- 1. Parametri iz konfiguracije ---
    # Lokacija i orijentacija
    n_panels = site.get('n_panels', 12)
    tilt = site.get('tilt_angle', 45)
    azimuth = site.get('azimuth_angle', 180) # Jug
    
    # Dimenzije panela (Huawei 540W)
    panel_w = equip['panels']['Huawei_IPV540-M1A']['dimensions_mm'][1] / 1000.0 # Širina (m)
    panel_h = equip['panels']['Huawei_IPV540-M1A']['dimensions_mm'][0] / 1000.0 # Visina (m)
    
    # Postavke nosača
    clearance = site.get('module_clearance_height', 0.5)
    pitch = 3.0 # Razmak redova
    
    # Dimenzije objekta (Procjena na osnovu tipičnog RAN kontejnera ako nije u JSON)
    # Ako imaš tačne dimenzije u JSON, ubaci ih ovdje
    container_w = 2.5 # metara
    container_l = 3.5 # metara
    
    # Ograda (Pretpostavka kvadratne parcele oko objekta)
    fence_size = 15.0 # 15x15 metara
    
    # --- 2. Crtanje Ograde ---
    fence = patches.Rectangle((-fence_size/2, -fence_size/2), fence_size, fence_size, 
                              linewidth=2, edgecolor='gray', facecolor='none', linestyle='--', label='Ograda')
    ax.add_patch(fence)
    
    # --- 3. Crtanje Kontejnera (Centrirano) ---
    # Kontejner je pravougaonik u centru (0,0)
    container = patches.Rectangle((-container_w/2, -container_l/2), container_w, container_l, 
                                  linewidth=2, edgecolor='blue', facecolor='#e0e0ff', label='RAN Kontejner')
    ax.add_patch(container)
    ax.text(0, 0, 'Kontejner', ha='center', va='center', color='blue', fontsize=9, fontweight='bold')
    
    # --- 4. Crtanje Antene (Na vrhu kontejnera ili blizu) ---
    # Simuliramo antenu kao krug/cilindar na vrhu kontejnera
    antenna_x, antenna_y = 0, container_l/2 + 0.5
    antenna = patches.Circle((antenna_x, antenna_y), radius=0.3, color='black', label='Antena')
    ax.add_patch(antenna)
    ax.text(antenna_x, antenna_y+0.5, 'Antena', ha='center', va='bottom', fontsize=8)
    
    # --- 5. Crtanje Panela (12 komada u 1 redu ili 2 reda?) ---
    # Prethodna konfiguracija: 12 panela, 1 red (nRows=1, nMods=12)
    # To znači niz od 12 panela jedan do drugog.
    # Ukupna dužina niza = 12 * panel_w
    # Centriramo niz ispred kontejnera (na jugu, jer je azimuth 180)
    
    total_array_width = n_panels * panel_w
    start_x = -total_array_width / 2
    
    # Pozicija centra panela (ispred kontejnera, recimo 5 metara južno)
    array_center_y = - (container_l/2 + 4.0) 
    array_center_x = 0
    
    # Crtamo svaki panel kao pravougaonik (projekcija na tlo ili stvarna širina)
    # Za Top View, crtamo širinu panela i dubinu koju zauzima (projekcija)
    # Dubina projekcije = panel_h * cos(tilt)
    projected_depth = panel_h * np.cos(np.radians(tilt))
    
    panel_patches = []
    for i in range(n_panels):
        px = start_x + (i * panel_w) + (panel_w/2) # Centar i-tog panela
        py = array_center_y
        
        # Pravougaonik panela (Top View)
        # Širina = panel_w, Visina (u top view) = projected_depth
        # Rotacija? Ako je azimuth 180 (Jug), a mi gledamo odozgo, paneli su vodoravno orijentisani ako je osa rotacije E-W.
        # Pretpostavljamo standardni mounting: dugom stranom horizontalno.
        
        rect = patches.Rectangle((px - panel_w/2, py - projected_depth/2), panel_w, projected_depth, 
                                 linewidth=1, edgecolor='darkgreen', facecolor='#4CAF50', alpha=0.7)
        ax.add_patch(rect)
        panel_patches.append(rect)
        
        # Dodijeli broj panelu
        if i % 2 == 0: # Svakom drugom piši broj da ne bude gužve
            ax.text(px, py, f'{i+1}', ha='center', va='center', color='white', fontsize=7, fontweight='bold')

    # Naslov i legende
    ax.set_title(f'RuralStar Sjednica - Sistemski Layout\n{ n_panels }x Huawei 540W | Tilt: {tilt}° | Azimuth: {azimuth}° (Jug)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Istok <--> Zapad (metri)')
    ax.set_ylabel('Sjever <--> Jug (metri)')
    
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper right')
    
    # Limiti prikaza
    limit = fence_size / 2 + 1
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    
    # Čuvanje slike
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', 'system_layout_detailed.png')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    log_success(f"Detaljni layout sačuvan: {out_path}")
    plt.close()

def plot_production_profile(df_results):
    """Generiše grafikon proizvodnje ako postoje podaci."""
    if df_results is None or df_results.empty:
        log_info("Nema podataka za grafikon proizvodnje.")
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Grupisanje po danima ili mjesecima za preglednost
    df_results['date'] = df_results.index.date
    daily_prod = df_results.groupby('date')['poa_front'].sum() / 1000 # kWh (približno)
    
    ax.bar(range(len(daily_prod)), daily_prod.values, color='orange', alpha=0.7, label='Dnevna Proizvodnja (kWh)')
    ax.set_title('Godišnji Profil Proizvodnje (PVLib Fallback Podaci)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Dan u godini')
    ax.set_ylabel('Energija (kWh)')
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    ax.legend()
    
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', 'production_profile.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    log_success(f"Grafikon proizvodnje sačuvan: {out_path}")
    plt.close()

if __name__ == "__main__":
    try:
        site, equip = load_config()
        plot_layout(site, equip)
        
        # Pokušaj učitavanja rezultata iz CSV-a ako postoji
        # (Ovo je pojednostavljeno, u stvarnosti bi učitali iz run_simulation outputa)
        # Za sada samo crtamo layout.
        log_success("Vizualizacija sistema završena!")
        
    except Exception as e:
        log_error(f"Greška pri vizualizaciji: {e}")
        import traceback
        traceback.print_exc()