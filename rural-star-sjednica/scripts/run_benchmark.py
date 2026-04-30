import os
import json
from matplotlib import patches
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from logger import log_info, log_success, log_error, log_warning

# Konfiguracija matplotliba za bolje fontove
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

def load_simulation_data():
    """Učitava konfiguraciju i rezultate simulacije."""
    log_info("Učitavam podatke za vizualizaciju...")
    
    config_path = 'site_config.json'
    equipment_path = 'equipment_db.json'
    log_path = 'simulation.log'
    
    if not os.path.exists(config_path) or not os.path.exists(equipment_path):
        log_error("Nedostaju konfiguracioni fajlovi.")
        return None, None, None

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    with open(equipment_path, 'r', encoding='utf-8') as f:
        equipment = json.load(f)
        
    df_results = None
    
    # Pokušaj parsiranja log fajla za dobijanje vremenske serije
    if os.path.exists(log_path):
        try:
            data = []
            with open(log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if "Sat:" in line and "PV:" in line:
                        # Parsiraj liniju: "Sat: 2023-01-01 00:00 | PV: 0.0 W | Load: 820.0 W | SOC: 50.0%"
                        parts = line.split('|')
                        if len(parts) >= 4:
                            ts_str = parts[0].split('Sat:')[1].strip()
                            pv = float(parts[1].split('PV:')[1].replace('W', '').strip())
                            load = float(parts[2].split('Load:')[1].replace('W', '').strip())
                            soc = float(parts[3].split('SOC:')[1].replace('%', '').strip())
                            
                            data.append({
                                'timestamp': pd.to_datetime(ts_str),
                                'production': pv / 1000.0, # kW
                                'consumption': load / 1000.0, # kW
                                'soc': soc
                            })
            
            if data:
                df_results = pd.DataFrame(data)
                df_results.set_index('timestamp', inplace=True)
                log_success(f"Učitano {len(df_results)} sati iz loga.")
            else:
                log_warning("Log fajl ne sadrži očekivane podatke. Koristim mock podatke.")
                
        except Exception as e:
            log_error(f"Greška pri čitanju loga: {e}")
    
    # Ako nema podataka iz loga, generiši mock podatke za prikaz geometrije
    if df_results is None:
        log_warning("Nema podataka iz loga. Kreiram privremene podatke za prikaz geometrije.")
        dates = pd.date_range(start="2023-01-01", periods=8760, freq="h")
        df_results = pd.DataFrame(index=dates)
        # Jednostavan sinusni model za proizvodnju
        dti = pd.DatetimeIndex(df_results.index)
        df_results['production'] = np.maximum(0, np.sin((dti.hour - 6) * np.pi / 12) * 5.0) # do 5kW
        df_results['consumption'] = 0.82 + np.random.normal(0, 0.1, len(dates)) # ~820W base
        df_results['soc'] = 50.0 # Fiksni SOC za mock
        
    return config, equipment, df_results

def plot_system_layout(config, equipment):
    """Crtta tlocrt i bočni presjek sistema (2 nosača)."""
    log_info("Generišem 2D projekcije geometrije...")
    
    geom = config.get('geometry_params', {})
    n_mounts = geom.get('n_mounts', 2)
    rows = geom.get('rows_per_mount', 2)
    cols = geom.get('cols_per_mount', 3)
    p_width = geom.get('panel_width', 1.13)
    p_length = geom.get('panel_length', 2.28)
    tilt = geom.get('tilt', 45)
    pitch = geom.get('pitch', 3.5)
    clearance = geom.get('clearance', 0.5)
    
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))
    
    # --- 1. TLOCRT (Top View) ---
    ax1 = axs[0]
    ax1.set_title("Tlocrt sistema (2 nosača)", fontsize=14, fontweight='bold')
    ax1.set_xlabel("Širina (m)")
    ax1.set_ylabel("Dubina (m)")
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    # Crtanje nosača
    for i in range(n_mounts):
        x_start = i * pitch
        # Nosač je širok (cols * p_width)
        width_total = cols * p_width
        rect = patches.Rectangle((x_start, -p_length/2), width_total, p_length, color='#003366', alpha=0.6, label=f'Nosač {i+1}' if i==0 else "")
        ax1.add_patch(rect)
        # Oznaka dimenzija
        ax1.text(x_start + width_total/2, 0, f"N{i+1}\n{width_total:.1f}m", 
                 ha='center', va='center', color='white', fontweight='bold')
        
    ax1.set_xlim(-1, n_mounts * pitch + 1)
    ax1.set_ylim(-2, 2)
    ax1.legend(loc='upper right')
    
    # --- 2. BOČNI PRESJEK (Side View) ---
    ax2 = axs[1]
    ax2.set_title(f"Bočni presjek (Nagib {tilt}°)", fontsize=14, fontweight='bold')
    ax2.set_xlabel("Širina (m)")
    ax2.set_ylabel("Visina (m)")
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    # Parametri za crtanje profila
    # Vertikalna visina panela
    h_proj = p_length * np.sin(np.radians(tilt))
    # Horizontalna dubina projekcije
    d_proj = p_length * np.cos(np.radians(tilt))
    
    # Crtamo profil JEDNOG nosača (ponavlja se)
    # Donji red
    z_base = clearance
    # Gornji red
    row_gap = geom.get('row_gap', 0.05)
    z_top_base = z_base + h_proj + row_gap
    
    # Funkcija za crtanje profila panela (linija od donjeg do gornjeg ruba)
    def draw_panel_profile(ax, x_center, z_base_level, color, label):
        # Donji rub je na (x_center - d_proj/2, z_base_level) - ako je centar u sredini?
        # Pretpostavimo da je x_center sredina nosača po širini.
        # Panel ide od x_left do x_right.
        # Zbog nagiba, donji rub je "ispred" (manji Y u 3D, ali ovdje crtamo X-Z pa je to samo pomak).
        # Za bočni pogled (presjek kroz sredinu nosača):
        # Donji rub: x = x_center - d_proj/2 ? Ne, zavisi kako je definisan centar.
        # Najjednostavnije: Centar panela je na (x_center, z_base + h_proj/2).
        # Donji rub: x = x_center - (d_proj/2), z = z_base
        # Gornji rub: x = x_center + (d_proj/2), z = z_base + h_proj
        
        x_bottom = x_center - (d_proj / 2)
        x_top = x_center + (d_proj / 2)
        
        ax.plot([x_bottom, x_top], [z_base_level, z_base_level + h_proj], 
                color=color, linewidth=3, label=label)
        # Stubovi (pojednostavljeno)
        ax.plot([x_bottom, x_bottom], [0, z_base_level], 'k--', linewidth=1, alpha=0.5)
        ax.plot([x_top, x_top], [0, z_base_level + h_proj], 'k--', linewidth=1, alpha=0.5)

    # Crtamo jedan reprezentativni nosač u presjeku
    center_x = pitch / 2 # Sredina prvog nosača
    
    # Donji red (3 panela jedan do drugog, ali u presjeku se vide kao jedna linija ako su u istoj ravni)
    # U bočnom presjeku vidimo samo profil jedne kolone (ili sve ako su pomjerene, ali ovdje su u istoj ravni po dubini)
    # Dakle, crtamo samo jedan profil za donji i jedan za gornji red.
    
    draw_panel_profile(ax2, center_x, z_base, '#003366', 'Donji red')
    draw_panel_profile(ax2, center_x, z_top_base, '#006699', 'Gornji red')
    
    # Tlo
    ax2.axhline(0, color='green', linewidth=2, label='Tlo')
    
    ax2.set_xlim(-1, pitch + 1)
    ax2.set_ylim(0, z_top_base + h_proj + 1)
    ax2.legend(loc='upper left')
    
    plt.tight_layout()
    save_path = 'report_results/system_layout.png'
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300)
    plt.close()
    log_success(f"Sačuvano: {save_path}")

def plot_daily_profile(df):
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    df_hourly = df.groupby(df.index.hour).mean()
    """Crtta dnevni profil proizvodnje i potrošnje (prosjek dana)."""
    log_info("Generišem dnevni profil...")
    
    # Grupiši po satu i uzmi prosjek
        
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df_hourly.index, df_hourly['production'], 'o-', color='orange', label='Proizvodnja (kW)', linewidth=2)
    ax.plot(df_hourly.index, df_hourly['consumption'], 's-', color='red', label='Potrošnja (kW)', linewidth=2)
    
    ax.set_title("Prosječni dnevni profil (Proizvodnja vs Potrošnja)", fontsize=14, fontweight='bold')
    ax.set_xlabel("Sat u danu")
    ax.set_ylabel("Snaga (kW)")
    ax.set_xticks(range(0, 24))
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()
    
    plt.tight_layout()
    save_path = 'report_results/daily_profile.png'
    plt.savefig(save_path, dpi=300)
    plt.close()
    log_success(f"Sačuvano: {save_path}")

def plot_monthly_balance(df):
    """Crtta mjesečni bilans energije i prosječan SoC."""
    log_info("Generišem mjesečni bilans...")
    
    # Dodaj kolonu mjesec
    df['month'] = df.index.month
    df['year_month'] = df.index.to_period('M')
    
    # Agregacija po mjesecu
    monthly = df.groupby('year_month').agg({
        'production': 'sum', # kWh (ako je u kW * 1h) -> zapravo suma kW * 1h = kWh
        'consumption': 'sum',
        'soc': 'mean'
    }).reset_index()
    
    # Pretvori Period u Timestamp za lakše plotovanje
    monthly['date'] = monthly['year_month'].dt.to_timestamp()
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Stupci za energiju
    width = 0.4
    x = np.arange(len(monthly))
    
    bars1 = ax1.bar(x - width/2, monthly['production'], width, label='Proizvodnja (kWh)', color='#2ca02c', alpha=0.8)
    bars2 = ax1.bar(x + width/2, monthly['consumption'], width, label='Potrošnja (kWh)', color='#d62728', alpha=0.8)
    
    ax1.set_xlabel("Mjesec", fontsize=12)
    ax1.set_ylabel("Energija (kWh)", fontsize=12, color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.set_xticks(x)
    ax1.set_xticklabels(monthly['date'].dt.strftime('%b'), rotation=45)
    ax1.grid(True, axis='y', linestyle='--', alpha=0.3)
    
    # Linija za SoC (desna osa)
    ax2 = ax1.twinx()
    line_soc = ax2.plot(x, monthly['soc'], 'o-', color='blue', label='Prosječan SoC (%)', linewidth=2, markersize=6)
    ax2.set_ylabel("Stanje baterije SoC (%)", fontsize=12, color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    ax2.set_ylim(0, 100)
    
    # Naslov i legende
    plt.title("Mjesečni bilans energije i stanje baterije", fontsize=14, fontweight='bold')
    
    # Spajanje legendi
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')
    
    plt.tight_layout()
    save_path = 'report_results/monthly_balance.png'
    plt.savefig(save_path, dpi=300)
    plt.close()
    log_success(f"Sačuvano: {save_path}")
    
    return monthly

def generate_site_comparison_plot(df_pvgis, df_ladybug, output_path="report_results/comparison_benchmark.png"):
    """
    Kreira uporedni prikaz: 
    1. Line graph: PVGIS Bileća vs Ladybug Čemerno (kWh)
    2. Column graph: Specifična proizvodnja SJEDNICA 12x540W
    """
    # Grupisanje podataka po mjesecima (kWh)
    monthly_pvgis = df_pvgis['production_w'].resample('M').sum() / 1000
    monthly_ladybug = df_ladybug['production_w'].resample('M').sum() / 1000
    
    months = [m.strftime('%b') for m in monthly_pvgis.index]

    # Kreiranje subplota
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    plt.subplots_adjust(hspace=0.3)

    # --- GORNJI GRAFIKON: Line Graph (Poređenje lokacija) ---
    ax1.plot(months, monthly_pvgis, marker='o', linewidth=2, color='#1f77b4', label='Bileća (PVGIS SARAH)')
    ax1.plot(months, monthly_ladybug, marker='s', linewidth=2, color='#ff7f0e', linestyle='--', label='Čemerno (Ladybug TMYx)')
    
    ax1.set_title('Mesečna proizvodnja: Poređenje mikrolokacije vs. Regionalni reper', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Energija (kWh)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # --- DONJI GRAFIKON: Column Graph (SJEDNICA Fokus) ---
    bars = ax2.bar(months, monthly_pvgis, color='#2ca02c', alpha=0.8, label='Sjednica 12x540W (Bileća)')
    
    # Dodavanje vrijednosti iznad kolona
    for bar in bars:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, yval + 5, f'{int(yval)}', ha='center', va='bottom', fontsize=9)

    ax2.set_title('Fokus: SJEDNICA 12x540W (Finalni proračun - Bileća)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Energija (kWh)', fontsize=12)
    ax2.set_xlabel('Mesec', fontsize=12)
    ax2.grid(axis='y', alpha=0.3)
    ax2.legend()

    # Snimanje
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    return output_path

def create_pdf_report(config, df_results, monthly_data,
                      df_results_pvgis=None, df_results_ladybug=None):
    """Kreira PDF izvještaj."""
    log_info("Kreiram PDF izvještaj...")
    
    doc = SimpleDocTemplate("RuralStar_Sjednica_Report.pdf", pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    styles = getSampleStyleSheet()
    
    # Definicija stila za naslove i tekst
    title_style = ParagraphStyle(name='CustomTitle', parent=styles['Heading1'], 
                                 fontSize=18, leading=22, alignment=TA_CENTER, spaceAfter=30)
    heading_style = ParagraphStyle(name='CustomHeading', parent=styles['Heading2'], 
                                   fontSize=14, leading=18, spaceBefore=12, spaceAfter=10)
    normal_style = styles['Normal']
    italic_style = ParagraphStyle(name='CustomItalic', parent=styles['Italic'], alignment=TA_CENTER)
    
    # --- Naslovna stranica ---
    elements.append(Paragraph("Izvještaj o simulaciji RuralStar Sjednica", title_style))
    elements.append(Paragraph(f"Datum generisanja: {datetime.now().strftime('%d.%m.%Y %H:%M')}", 
                              ParagraphStyle(name='DateStyle', parent=normal_style, alignment=TA_CENTER)))
    elements.append(Spacer(1, 0.5*inch))
    
    # --- 1. Konfiguracija sistema ---
    elements.append(Paragraph("1. Konfiguracija Sistema", heading_style))
    
    geom = config.get('geometry_params', {})
    eq = config.get('equipment', {}) # Pretpostavka da je equipment u configu ili globalno
    
    config_data = [
        ["Parametar", "Vrijednost"],
        ["Lokacija", f"{config.get('latitude', 42.94)}° N, {config.get('longitude', 18.32)}° E"],
        ["Nadmorska visina", f"{config.get('altitude', 1076)} m"],
        ["Ukupno panela", f"{geom.get('total_panels', 12)} kom (Huawei 540W)"],
        ["Raspored", f"{geom.get('n_mounts', 2)} nosača x {geom.get('rows_per_mount', 2)} reda x {geom.get('cols_per_mount', 3)} kolone"],
        ["Nagib (Tilt)", f"{geom.get('tilt', 45)}°"],
        ["Orijentacija", "Jug (180°)"],
        ["Baterija", f"{config.get('battery_capacity_kwh', 46.08)} kWh"],
        ["Generator", f"{config.get('gen_power_kw', 13.5)} kW"]
    ]
    
    t_config = Table(config_data, colWidths=[4*cm, 6*cm])
    t_config.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t_config)
    elements.append(Spacer(1, 0.3*inch))
    caption_style = ParagraphStyle(
        name='CaptionStyle',
        parent=styles['Italic'],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.grey
    )
    ##Unutar funkcije koja pravi PDF: 
    img_path = generate_site_comparison_plot(df_results_pvgis, df_results_ladybug)
    elements.append(Image(img_path, width=16*cm, height=14*cm))
    elements.append(Paragraph("Slika 1. Poređenje energetskog prinosa lokacija Bileća i Čemerno", caption_style))
    # --- 2. Vizualizacija Geometrije ---
    elements.append(Paragraph("2. Geometrija Rasporeda", heading_style))
    img_layout = Image("report_results/system_layout.png", width=6.5*inch, height=4*inch)
    elements.append(img_layout)
    elements.append(Paragraph("<i>Slika 1: Tlocrt i bočni presjek sistema (2 nosača).</i>", italic_style))
    elements.append(PageBreak())
    
    # --- 3. Energetski Bilans ---
    elements.append(Paragraph("3. Energetski Bilans", heading_style))
    
    # Dnevni profil
    img_daily = Image("report_results/daily_profile.png", width=6.5*inch, height=4*inch)
    elements.append(img_daily)
    elements.append(Paragraph("<i>Slika 2: Prosječni dnevni profil proizvodnje i potrošnje.</i>", italic_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Mjesečni bilans
    img_monthly = Image("report_results/monthly_balance.png", width=6.5*inch, height=4*inch)
    elements.append(img_monthly)
    elements.append(Paragraph("<i>Slika 3: Mjesečni bilans energije i prosječno stanje baterije (SoC).</i>", italic_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabela mjesečnih rezultata
    elements.append(Paragraph("Detaljni mjesečni podaci:", styles['Normal']))
    month_rows = [["Mjesec", "Proizvodnja (kWh)", "Potrošnja (kWh)", "Višak/Manjak (kWh)", "Prosječan SoC (%)"]]
    for _, row in monthly_data.iterrows():
        diff = row['production'] - row['consumption']
        month_rows.append([
            row['date'].strftime('%B'),
            f"{row['production']:.1f}",
            f"{row['consumption']:.1f}",
            f"{diff:+.1f}",
            f"{row['soc']:.1f}"
        ])
    
    t_monthly = Table(month_rows, colWidths=[2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
    t_monthly.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.beige])
    ]))
    elements.append(t_monthly)
    
    # --- Kraj ---
    elements.append(PageBreak())
    elements.append(Paragraph("Kraj izvještaja.", ParagraphStyle(name='EndStyle', parent=normal_style, alignment=TA_CENTER)))
    
    # Generisanje PDF-a
    doc.build(elements)
    log_success("PDF izvještaj uspješno kreiran: RuralStar_Sjednica_Report.pdf")

def main():
    log_info("🎨 Generisanje finalnog izvještaja...")
    
    config, equipment, df_results = load_simulation_data()
    if not config:
        return

    # 1. Geometrija
    plot_system_layout(config, equipment)
    
    # 2. Profili
    plot_daily_profile(df_results)
    
    # 3. Mjesečni bilans
    monthly_data = plot_monthly_balance(df_results)
    
    # 4. PDF
    create_pdf_report(config, df_results, monthly_data,
                  df_results_pvgis=df_results, df_results_ladybug=df_results)
    
    log_success("✅ Vizualizacije i izvještaj završeni! Provjerite folder 'report_results'.")

if __name__ == "__main__":
    main()