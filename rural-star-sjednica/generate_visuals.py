import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
from logger import log_info, log_success, log_error, log_warning # Dodano log_warning

def load_data():
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(base_path, 'site_config.json')
    config = {}
    if os.path.exists(config_file):
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
    results_file = os.path.join(base_path, 'simulation_results.csv')
    if os.path.exists(results_file):
        df = pd.read_csv(results_file, index_col=0, parse_dates=True)
        log_success("Podaci uspješno učitani.")
        return config, df
    else:
        log_error("Fajl simulation_results.csv nije pronađen!")
        return config, None

def get_representative_day(df, season_name, month, day_target):
    """
    Bira najbolji dan za prikaz iz zadatog mjeseca.
    Prioritet: Dan sa najvećom proizvodnjom koji je najbliži target datumu.
    """
    # Filtriraj mjesec
    df_month = df[df.index.month == month]
    if df_month.empty:
        return None, None
        
    # Grupiši po danu
    df_month['day_of_month'] = df_month.index.day
    daily_prod = df_month.groupby('day_of_month')['production_w'].sum()
    
    # Nađi dan sa max proizvodnjom
    if daily_prod.empty:
        return None, None
        
    best_day = daily_prod.idxmax()
    
    # Vrati podatke za taj dan
    day_data = df[df.index.day == best_day]
    # Provjeri da li je baš taj mjesec (sigurnosna provjera)
    if len(day_data) == 0 or day_data.index[0].month != month:
        # Fallback: uzmi prvi dan u mjesecu
        best_day = df_month.index[0].day
        day_data = df[df.index.day == best_day]
        
    label = f"{season_name} ({best_day}. {month})"
    return day_data, label

def plot_layout(config, output_path):
    fig, ax = plt.subplots(figsize=(10, 6))
    tilt = config.get('tilt_angle', 45)
    pitch = 3.0
    w, h = 1.134, 2.278 
    
    rad = np.radians(tilt)
    dx, dz = h * np.cos(rad), h * np.sin(rad)
    clearance = 0.5
    
    # Paneli (2 reda)
    for r in range(2):
        base_x = r * pitch
        poly_coords = [(base_x, clearance), (base_x + dx, clearance + dz), 
                       (base_x + dx + 0.1, clearance + dz), (base_x + 0.1, clearance)]
        polygon = patches.Polygon(poly_coords, closed=True, color='#003366', edgecolor='white', linewidth=2)
        ax.add_patch(polygon)
        
    # Kontejner (ispred)
    ax.add_patch(patches.Rectangle((-5, 0), 4, 2.6, color='#555555', label='Kontejner'))
    ax.text(-3, 1.3, "Kontejner", ha='center', va='center', color='white', fontweight='bold')
    
    # Ograda
    ax.plot([-6, 12], [2.5, 2.5], 'k-', linewidth=3, label='Ograda')
    ax.fill_between([-6, 12], 0, 2.5, color='#eeeeee', alpha=0.5)
    
    ax.set_xlim(-6, 15); ax.set_ylim(0, 6); ax.set_aspect('equal')
    ax.set_title(f"Sistem Layout (Pogled sa strane)", fontsize=14, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper right')
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    log_success(f"Layout sačuvan: {output_path}")

def create_report(config, df):
    if df is None:
        log_error("Nema podataka za izvještaj.")
        return

    base_path = os.path.dirname(os.path.abspath(__file__))
    report_dir = os.path.join(base_path, 'report_results')
    os.makedirs(report_dir, exist_ok=True)
    
    pdf_path = os.path.join(report_dir, 'RuralStar_Sjednica_FINAL_REPORT.pdf')
    layout_path = os.path.join(report_dir, 'layout.png')
    
    # 1. Layout
    plot_layout(config, layout_path)
    
    # 2. Priprema podataka za grafikone
    # Mjesečni bilans
    df['month'] = df.index.month
    monthly = df.groupby('month')[['production_w', 'consumption_w']].sum() / 1000 # kWh
    
    # Dnevni profili (Reprezentativni dani)
    # Zima (Jan, 15), Proljece (Apr, 15), Ljeto (Jul, 15), Jesen (Okt, 15)
    days_data = []
    seasons = [
        ("Zima", 1, 15),
        ("Proljeće", 4, 15),
        ("Ljeto", 7, 15),
        ("Jesen", 10, 15)
    ]
    
    for s_name, m, d in seasons:
        d_data, label = get_representative_day(df, s_name, m, d)
        if d_data is not None:
            days_data.append((label, d_data))
    
    # 3. Crtanje grafikona
    fig_profiles, axs = plt.subplots(2, 1, figsize=(12, 10))
    
    # A) Mjesečni bilans
    x = np.arange(1, 13)
    width = 0.4
    axs[0].bar(x - width/2, monthly['production_w'], width, label='Proizvodnja (kWh)', color='orange')
    axs[0].bar(x + width/2, monthly['consumption_w'], width, label='Potrošnja (kWh)', color='red')
    axs[0].set_title("Mjesečni bilans proizvodnje i potrošnje", fontsize=14, fontweight='bold')
    axs[0].set_xticks(x)
    axs[0].set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec'])
    axs[0].grid(True, axis='y', alpha=0.3)
    axs[0].legend()
    
    # B) Dnevni profili
    colors = ['blue', 'green', 'red', 'purple']
    for i, (label, data) in enumerate(days_data):
        hour = data.index.hour
        prod = data['production_w'] / 1000 # kW
        axs[1].plot(hour, prod, label=label, color=colors[i], linewidth=2)
        
    axs[1].set_title("Dnevni profil proizvodnje (Karakteristični dani)", fontsize=14, fontweight='bold')
    axs[1].set_xlabel("Sat u danu")
    axs[1].set_ylabel("Snaga (kW)")
    axs[1].set_xticks(range(24))
    axs[1].grid(True, alpha=0.3)
    axs[1].legend()
    
    plt.tight_layout()
    profiles_path = os.path.join(report_dir, 'profiles.png')
    plt.savefig(profiles_path, dpi=300, bbox_inches='tight')
    plt.close()
    log_success(f"Grafikoni sačuvani: {profiles_path}")
    
    # 4. Kreiranje PDF-a
    with PdfPages(pdf_path) as pdf:
        # Naslovna
        fig_title = plt.figure(figsize=(8.5, 11))
        plt.axis('off')
        plt.text(0.5, 0.95, "RURALSTAR SJEDNICA\nFINALNI IZVJEŠTAJ", ha='center', va='center', fontsize=22, fontweight='bold')
        
        total_prod = df['production_w'].sum() / 1000
        total_cons = df['consumption_w'].sum() / 1000
        
        info_text = (
            f"Lokacija: Bileća (Cemerno), BiH\n"
            f"Nadmorska visina: 1076 m\n"
            f"Instalirana snaga: {config.get('n_panels', 12) * 0.54:.1f} kWp\n\n"
            f"REZULTATI SIMULACIJE:\n"
            f"Godišnja proizvodnja: {total_prod:,.1f} kWh\n"
            f"Godišnja potrošnja: {total_cons:,.1f} kWh\n"
            f"Višak energije: {total_prod - total_cons:,.1f} kWh"
        )
        plt.text(0.5, 0.7, info_text, ha='center', va='center', fontsize=14, family='monospace', bbox=dict(boxstyle="round", facecolor="#f0f0f0"))
        pdf.savefig(fig_title); plt.close()
        
        # Layout
        if os.path.exists(layout_path):
            img = plt.imread(layout_path)
            fig = plt.figure(figsize=(10, 6)); plt.imshow(img); plt.axis('off'); pdf.savefig(fig); plt.close()
            
        # Grafikoni
        if os.path.exists(profiles_path):
            img = plt.imread(profiles_path)
            fig = plt.figure(figsize=(10, 8)); plt.imshow(img); plt.axis('off'); pdf.savefig(fig); plt.close()
            
        # Heatmap / False Color (ako postoji)
        fc_path = os.path.join(base_path, 'radiance_results', 'images', 'falsecolor_solar_radiance.png')
        if os.path.exists(fc_path):
            img = plt.imread(fc_path)
            fig = plt.figure(figsize=(10, 8))
            plt.imshow(img)
            plt.title("False Color Analiza (Radiance)", fontsize=14, fontweight='bold')
            plt.axis('off')
            pdf.savefig(fig); plt.close()
            
    log_success(f"✅ FINALNI IZVJEŠTAJ KREIRAN: {pdf_path}")

def main():
    log_info("🚀 Generisanje finalnog izvještaja...")
    config, df = load_data()
    create_report(config, df)
    log_success("✅ Proces završen!")

if __name__ == "__main__":
    main()