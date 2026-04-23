#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GENERATOR DETALJNOG PDF IZVJEŠTAJA
Čita rezultate simulacije i kreira profesionalni PDF sa grafikonima, tabelama i analizom.
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# Konfiguracija
PROJECT_ROOT = r"E:\Radiance_build\moja_solar_ograda"
RAD_BASE = os.path.join(PROJECT_ROOT, "sjednica_bileca_irradiance_outward_max")
RESULTS_FILE = os.path.join(RAD_BASE, "results", "annual_irrad.txt")
WEATHER_FILE = os.path.join(RAD_BASE, "EPWs", "weather.epw") # Treba nam za vremensku seriju

# Parametri sistema (moraju biti isti kao u simulaciji)
PANEL_L = 2.279
PANEL_W = 1.134
MODULE_EFFICIENCY = 0.21
BIFACIAL_FACTOR = 0.80
ALBEDO = 0.65
V_NOM = 48.0
BATTERY_AH = 450
CAPACITY_KWH = V_NOM * BATTERY_AH / 1000.0

def load_results():
    """Učitava rezultate iz txt fajla."""
    if not os.path.exists(RESULTS_FILE):
        print(f"❌ Rezultati nisu pronađeni: {RESULTS_FILE}")
        return None
    
    try:
        data = np.loadtxt(RESULTS_FILE)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        return data
    except Exception as e:
        print(f"Greška pri čitanju: {e}")
        return None

def create_monthly_table(df):
    """Kreira tabelu mjesečne proizvodnje."""
    df['Month'] = df.index.month
    df['Year'] = df.index.year
    
    monthly = df.groupby(['Year', 'Month'])[['MPLS_DC_W', 'RAN_DC_W']].sum() / 1000.0 # kWh
    monthly.columns = ['MPLS (kWh)', 'RAN (kWh)']
    monthly['Ukupno (kWh)'] = monthly['MPLS (kWh)'] + monthly['RAN (kWh)']
    monthly['Specifično (kWh/kWp)'] = monthly['Ukupno (kWh)'] / (19 * PANEL_L * PANEL_W * MODULE_EFFICIENCY * 1000 / 1000) # Approx kWp
    
    return monthly

def plot_daily_profiles(df, ax):
    """Crtanje prosječnog dnevnog profila po mjesecima."""
    df['Hour'] = df.index.hour
    df['Month'] = df.index.month
    
    fig_months = [1, 4, 7, 10] # Jan, Apr, Jul, Oct
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for i, month in enumerate(fig_months):
        month_data = df[df['Month'] == month].groupby('Hour')['MPLS_DC_W', 'RAN_DC_W'].mean() / 1000.0
        total = month_data['MPLS_DC_W'] + month_data['RAN_DC_W']
        ax.plot(total, label=f'Mjesec {month}', color=colors[i], linewidth=2)
    
    ax.set_title('Prosječni dnevni profil proizvodnje (kW)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Sat u danu')
    ax.set_ylabel('Snaga (kW)')
    ax.legend()
    ax.grid(True, alpha=0.3)

def plot_soc_distribution(df, ax):
    """Histogram stanja punjenja baterija."""
    bins = np.linspace(0, 1, 21)
    ax.hist(df['MPLS_SoC'], bins=bins, alpha=0.6, label='MPLS', color='blue', edgecolor='black')
    ax.hist(df['RAN_SoC'], bins=bins, alpha=0.6, label='RAN', color='orange', edgecolor='black')
    ax.set_title('Distribucija stanja punjenja baterija (SoC)', fontsize=12, fontweight='bold')
    ax.set_xlabel('SoC (%)')
    ax.set_ylabel('Broj sati')
    ax.legend()
    ax.grid(True, alpha=0.3)

def plot_monthly_production(monthly_df, ax):
    """Stubičasti dijagram mjesečne proizvodnje."""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
    x = np.arange(len(months))
    width = 0.35
    
    # Uzmi prosjek za više godina ako postoji
    if isinstance(monthly_df.index, pd.MultiIndex):
        monthly_avg = monthly_df.groupby('Month').mean()
    else:
        monthly_avg = monthly_df
        
    rects1 = ax.bar(x - width/2, monthly_avg['MPLS (kWh)'], width, label='MPLS', color='#1f77b4')
    rects2 = ax.bar(x + width/2, monthly_avg['RAN (kWh)'], width, label='RAN', color='#ff7f0e')
    
    ax.set_title('Mjesečna proizvodnja energije', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(months, rotation=45)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Dodaj vrijednosti na stubiće
    for rect in rects1 + rects2:
        height = rect.get_height()
        ax.annotate(f'{height:.0f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)

def generate_pdf_report():
    """Generiše kompletan PDF izvještaj."""
    print("📊 Učitavam rezultate...")
    data = load_results()
    if data is None:
        return
    
    # Kreiramo privremeni DataFrame za analizu (simulira strukturu iz glavne skripte)
    # Napomena: Ovo je pojednostavljeno jer nemamo originalni df_weather ovdje
    n_hours, n_sensors = data.shape
    dates = pd.date_range(start='2023-01-01', periods=n_hours, freq='h')
    
    # Rekonstrukcija kolona (pretpostavka redoslijeda iz glavne skripte)
    panel_ids = list(range(1, 20))
    cols = [f"panel_{pid}_{side}" for pid in panel_ids for side in ['front', 'back']]
    
    if len(cols) != n_sensors:
        print(f"⚠️ Upozorenje: Očekivano {len(cols)} senzora, a ima {n_sensors}. Prilagođavam...")
        # Ako se broj ne poklapa, koristimo onoliko koliko imamo
        cols = cols[:n_sensors] if n_sensors < len(cols) else cols + [f"extra_{i}" for i in range(n_sensors - len(cols))]
    
    df = pd.DataFrame(data, index=dates, columns=cols)
    
    # Ponovni proračun snage (isti kao u glavnoj skripti)
    panel_area = PANEL_L * PANEL_W
    for pid in panel_ids:
        if pid > len(panel_ids): break # Safety check
        front_col = f"panel_{pid}_front" if f"panel_{pid}_front" in df.columns else None
        back_col = f"panel_{pid}_back" if f"panel_{pid}_back" in df.columns else None
        
        if front_col and back_col:
            df[f"P_{pid}_total"] = (df[front_col] + df[back_col] * BIFACIAL_FACTOR * ALBEDO) * panel_area * MODULE_EFFICIENCY
    
    # Suma po sistemima (pretpostavka: 1-10 MPLS, 11-19 RAN)
    mpls_cols = [f"P_{pid}_total" for pid in range(1, 11) if f"P_{pid}_total" in df.columns]
    ran_cols = [f"P_{pid}_total" for pid in range(11, 20) if f"P_{pid}_total" in df.columns]
    
    if mpls_cols:
        df['MPLS_DC_W'] = df[mpls_cols].sum(axis=1)
    else:
        df['MPLS_DC_W'] = 0
        
    if ran_cols:
        df['RAN_DC_W'] = df[ran_cols].sum(axis=1)
    else:
        df['RAN_DC_W'] = 0
    
    # Simulacija baterija (pojednostavljena verzija)
    load_mpls, load_ran, climate_w = 200/1000, 500/1000, 150/1000
    ssu_eff = 0.96
    e_mpls = e_ran = CAPACITY_KWH * 0.5
    soc_mpls = []
    soc_ran = []
    
    # Pretpostavka temperature (prosta sinusoida)
    temp_air = 15 + 10 * np.sin(2 * np.pi * (np.arange(n_hours) - 2000) / 8760)
    
    for i in range(n_hours):
        pv_m = df['MPLS_DC_W'].iloc[i] * ssu_eff / 1000 if isinstance(df['MPLS_DC_W'].iloc[i], (int, float)) else 0
        net_m = pv_m - (load_mpls + (climate_w if temp_air[i] > 25 else 0))
        e_mpls = min(e_mpls + net_m, CAPACITY_KWH) if net_m > 0 else max(e_mpls + net_m, 0.1*CAPACITY_KWH)
        soc_mpls.append(e_mpls / CAPACITY_KWH)
        
        pv_r = df['RAN_DC_W'].iloc[i] * ssu_eff / 1000 if isinstance(df['RAN_DC_W'].iloc[i], (int, float)) else 0
        net_r = pv_r - load_ran
        e_ran = min(e_ran + net_r, CAPACITY_KWH) if net_r > 0 else max(e_ran + net_r, 0.1*CAPACITY_KWH)
        soc_ran.append(e_ran / CAPACITY_KWH)
    
    df['MPLS_SoC'] = soc_mpls
    df['RAN_SoC'] = soc_ran
    
    # Kalkulacije
    total_mpls = df['MPLS_DC_W'].sum() / 1000
    total_ran = df['RAN_DC_W'].sum() / 1000
    total_energy = total_mpls + total_ran
    installed_kwp = 19 * PANEL_L * PANEL_W * MODULE_EFFICIENCY * 1000 # W -> kW? Ne, efficiency je već faktor. 
    # Ispravka: P_nom = Area * Irradiance_std * Efficiency. Ali ovdje nemamo standardnu iradijancu.
    # Koristimo nazivnu snagu panela ako je poznata. Canadian Solar 585W?
    # U ovoj skripti koristimo dimenzije. Pretpostavimo 1000 W/m2 za STC.
    # P_nom = 19 * (2.279 * 1.134) * 0.21 * 1000 = ~5140 W = 5.14 kWp
    p_nom_per_panel = PANEL_L * PANEL_W * 1000 * MODULE_EFFICIENCY
    installed_kwp = 19 * p_nom_per_panel / 1000
    
    specific_yield = total_energy / installed_kwp if installed_kwp > 0 else 0
    
    # Mjesečna tabela
    monthly_df = create_monthly_table(df)
    
    # Kreiranje PDF-a
    pdf_path = os.path.join(RAD_BASE, "IZVJESTAJ_PROIZVODNJA.pdf")
    print(f"📝 Generišem PDF izvještaj: {pdf_path}")
    
    with PdfPages(pdf_path) as pdf:
        # --- STRANICA 1: Naslovna i Sažetak ---
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        
        title_text = (
            f"DE TALJNI IZVJEŠTAJ O PROIZVODNJI\n"
            f"SOLARNA OGRADA – RURALSTAR HYBRID\n\n"
            f"Lokacija: Bileća, BiH (42.94°N, 18.32°E)\n"
            f"Datum generisanja: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"Nadmorska visina: 1050 m\n\n"
            f"{'='*40}\n"
            f"SAŽETAK PERFORMANSI\n"
            f"{'='*40}\n\n"
            f"Instalisana snaga:          {installed_kwp:.2f} kWp\n"
            f"Ukupna godišnja proizvodnja: {total_energy:,.0f} kWh\n"
            f"Specifična proizvodnja:      {specific_yield:,.0f} kWh/kWp\n"
            f"Prosjek dnevno:              {total_energy / 365:.1f} kWh\n\n"
            f"Proizvodnja po sistemu:\n"
            f"  • MPLS (10 panela): {total_mpls:,.0f} kWh ({total_mpls/total_energy*100:.1f}%)\n"
            f"  • RAN  (9 panela):  {total_ran:,.0f} kWh ({total_ran/total_energy*100:.1f}%)\n\n"
            f"Stanje baterija (450Ah, 48V):\n"
            f"  • MPLS: Min SoC {min(soc_mpls)*100:.1f}%, Prosjek {np.mean(soc_mpls)*100:.1f}%\n"
            f"  • RAN:  Min SoC {min(soc_ran)*100:.1f}%, Prosjek {np.mean(soc_ran)*100:.1f}%\n"
            f"  • Sati sa kritičnim SoC (<15%): MPLS={sum(s<0.15 for s in soc_mpls)}, RAN={sum(s<0.15 for s in soc_ran)}\n"
        )
        ax.text(0.5, 0.95, title_text, transform=ax.transAxes, fontsize=11, verticalalignment='top', horizontalalignment='center', family='monospace')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # --- STRANICA 2: Mjesečna proizvodnja (Tabela + Grafikon) ---
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.5, 11))
        
        # Tabela
        ax1.axis('off')
        table_text = "MJSEČNA PROIZVODNJA ENERGIJE (kWh)\n\n"
        # Formatiranje tabele za prikaz
        if isinstance(monthly_df.index, pd.MultiIndex):
            display_df = monthly_df.reset_index()
        else:
            display_df = monthly_df.copy()
            display_df['Month'] = display_df.index
            
        # Kreiranje stringa za tabelu
        table_rows = []
        for _, row in display_df.iterrows():
            if isinstance(row.get('Year'), float):
                table_rows.append(f"{int(row['Month']):2d}   {row['MPLS (kWh)']:7.1f}   {row['RAN (kWh)']:7.1f}   {row['Ukupno (kWh)']:7.1f}")
            else:
                table_rows.append(f"{int(row['Month']):2d}   {row['MPLS (kWh)']:7.1f}   {row['RAN (kWh)']:7.1f}   {row['Ukupno (kWh)']:7.1f}")
        
        header = "Mj  MPLS     RAN      UKUPNO\n" + "-"*30 + "\n"
        body = "\n".join(table_rows)
        footer = "\n" + "-"*30 + f"\nΣ   {monthly_df['MPLS (kWh)'].sum():7.1f}   {monthly_df['RAN (kWh)'].sum():7.1f}   {monthly_df['Ukupno (kWh)'].sum():7.1f}"
        
        ax1.text(0.1, 0.8, header + body + footer, transform=ax1.transAxes, fontsize=10, verticalalignment='top', family='monospace')
        ax1.set_title("Tabela 1: Mjesečna proizvodnja", fontsize=14, fontweight='bold', pad=20)
        
        # Grafikon
        plot_monthly_production(monthly_df, ax2)
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # --- STRANICA 3: Dnevni profili i SoC ---
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.5, 11))
        plot_daily_profiles(df, ax1)
        plot_soc_distribution(df, ax2)
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # --- STRANICA 4: Tehnički podaci ---
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        
        tech_text = (
            "TEHNIČKI PODACI O SISTEMU\n\n"
            "-------------------------\n"
            "PANELI:\n"
            f"  - Tip: Bifacial Glass-Glass\n"
            f"  - Dimenzije: {PANEL_L*100:.0f} cm x {PANEL_W*100:.0f} cm\n"
            f"  - Površina jednog: {PANEL_L*PANEL_W:.2f} m²\n"
            f"  - Efikasnost modula: {MODULE_EFFICIENCY*100:.1f}%\n"
            f"  - Bifacial faktor: {BIFACIAL_FACTOR*100:.0f}%\n"
            f"  - Ukupan broj: 19 kom (10 MPLS + 9 RAN)\n\n"
            "KONSTRUKCIJA:\n"
            "  - Nagib: 16° od vertikale (prema van)\n"
            "  - Visina donjeg ruba: 0.5 m\n"
            "  - Albedo (tlo): 0.65 (svijetli tampon)\n\n"
            "BATERIJE:\n"
            f"  - Kapacitet: {CAPACITY_KWH:.1f} kWh (48V, 450Ah)\n"
            f"  - Dubina pražnjenja (DoD): 90% (min SoC 10%)\n\n"
            "OPTEREĆENJE:\n"
            "  - MPLS: 200W (osnovno) + 150W (klima ako T>25°C)\n"
            "  - RAN: 500W (konstantno)\n\n"
            "SIMULACIJA:\n"
            "  - Engine: Radiance (gendaymtx, rtrace)\n"
            "  - Vremenski podaci: PVGIS TMY\n"
            "  - Rezolucija: 1 sat\n"
            "  - Ukupno sati: 8760\n"
        )
        ax.text(0.5, 0.95, tech_text, transform=ax.transAxes, fontsize=11, verticalalignment='top', horizontalalignment='center', family='monospace')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    print(f"✅ PDF izvještaj uspješno kreiran: {pdf_path}")
    print(f"📂 Lokacija: {pdf_path}")

if __name__ == "__main__":
    generate_pdf_report()
