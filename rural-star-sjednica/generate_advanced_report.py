import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os
from matplotlib.backends.backend_pdf import PdfPages
from logger import log_info, log_success

def generate_pro_report(df_path, full_config):
    df = pd.read_csv(df_path, index_col=0, parse_dates=True)
    site = full_config.get('site_config', {})
    scenario = full_config.get('scenario_A_PowerCube', {})

    # Metrike
    total_front = df['poa_front'].sum() / 1000 # kWh/m2
    total_back = df['poa_back'].sum() / 1000
    b_gain = (total_back / total_front * 100) if total_front > 0 else 0
    total_yield = df['production_w'].sum() / 1000 # kWh

    plt.style.use('bmh') # Inženjerski stil
    pdf_name = "Bifacial_Yearly_Analysis_Report.pdf"

    with PdfPages(pdf_name) as pdf:
        # STRANA 1: Naslovna i statistika
        fig = plt.figure(figsize=(11, 8.5))
        plt.axis('off')
        header = f"SYSTEM PERFORMANCE REPORT: {scenario.get('description')}\n"
        header += "-"*60 + "\n"
        stats = (
            f"Lokacija: {site.get('latitude')}, {site.get('longitude')}\n"
            f"Ukupno panela: {scenario.get('n_panels')}\n\n"
            f"GODIŠNJI REZULTATI:\n"
            f"----------------------------------\n"
            f"Prednja Irradijanca:  {total_front:,.2f} kWh/m²/y\n"
            f"Zadnja Irradijanca:   {total_back:,.2f} kWh/m²/y\n"
            f"Bifacijalni dobitak:  {b_gain:.2f} %\n"
            f"Ukupna proizvodnja:   {total_yield:,.1f} kWh/y\n"
            f"Rad generatora:       {df['generator_kwh'].sum():,.1f} kWh\n"
        )
        plt.text(0.1, 0.9, header, fontsize=16, fontweight='bold', family='monospace')
        plt.text(0.1, 0.5, stats, fontsize=13, family='monospace')
        pdf.savefig(); plt.close()

        # STRANA 2: Mjesečni podaci (Konzistentno sa bifacial_radiance)
        monthly = df.resample('M').sum() / 1000
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(monthly))
        ax.bar(x - 0.2, monthly['poa_front'], 0.4, label='Front', color='#2c3e50')
        ax.bar(x + 0.2, monthly['poa_back'], 0.4, label='Back', color='#e67e22')
        ax.set_xticks(x)
        ax.set_xticklabels([d.strftime('%b') for d in monthly.index])
        ax.set_title("Monthly Irradiance Distribution [kWh/m²]")
        ax.legend()
        pdf.savefig(); plt.close()

    log_success(f"Izvještaj generisan: {pdf_name}")