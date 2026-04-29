import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
from logger import log_info, log_success, log_error, log_warning


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data():
    base_path = os.path.dirname(os.path.abspath(__file__))

    config_file = os.path.join(base_path, 'site_config.json')
    config = {}
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

    # FIX: run_simulation.py writes to 'results/final_simulation_output.csv'
    # generate_visuals.py was incorrectly reading 'simulation_results.csv'
    candidates = [
        os.path.join(base_path, 'results', 'final_simulation_output.csv'),
        os.path.join(base_path, 'results', 'all_scenarios_comparison.csv'),
        os.path.join(base_path, 'results', 'scenario_A_results.csv'),
        os.path.join(base_path, 'simulation_results.csv'),  # legacy fallback
    ]

    df = None
    for path in candidates:
        if os.path.exists(path):
            df = pd.read_csv(path, index_col=0, parse_dates=True)
            log_success(f"Podaci učitani iz: {os.path.basename(path)}")
            break

    if df is None:
        log_error(
            "Nije pronađen ni jedan results CSV. "
            "Pokreni run_simulation.py ili simulate_all_scenarios() prvo."
        )

    return config, df


# ---------------------------------------------------------------------------
# Representative day selector
# ---------------------------------------------------------------------------

def get_representative_day(df: pd.DataFrame, season_name: str, month: int, day_target: int):
    """
    Picks the highest-production day closest to day_target in the given month.
    Returns (day_df, label) or (None, None).
    """
    df_month = df[df.index.month == month]
    if df_month.empty:
        return None, None

    prod_col = 'production_w' if 'production_w' in df_month.columns else 'pv_w'
    daily_prod = df_month.groupby(df_month.index.day)[prod_col].sum()
    if daily_prod.empty:
        return None, None

    best_day = daily_prod.idxmax()
    day_data  = df[(df.index.month == month) & (df.index.day == best_day)]
    label     = f"{season_name} ({best_day}. {month})"
    return day_data, label


# ---------------------------------------------------------------------------
# Layout diagram
# ---------------------------------------------------------------------------

def plot_layout(config: dict, output_path: str):
    """
    Side-view layout: K2-32m lattice tower + container + Huawei Smart 3.0 panels.
    Geometry derived from 02_Dispozicija_K2_S32_m.pdf and equipment_db.json.
    """
    fig, ax = plt.subplots(figsize=(14, 8))

    tilt_deg = config.get('tilt_angle', 45)
    tilt_rad = np.radians(tilt_deg)
    pw       = 1.134    # panel width  (m)
    ph       = 2.279    # panel height (m)
    clearance = 0.8     # Smart 3.0 ground clearance (m)

    # Panel projections
    dy = ph * np.cos(tilt_rad)
    dz = ph * np.sin(tilt_rad)

    # ---------- TOWER (lattice, simplified as tapered rectangle side-view) ----------
    tower_h   = 32.0
    base_w    = 5.67 / 2   # half-width at base
    top_w     = 0.40 / 2   # half-width at top (approx)
    tower_x   = 0.0        # tower centre
    foundation_w = 5.40

    # Foundation pad
    ax.add_patch(patches.Rectangle(
        (tower_x - foundation_w / 2, -0.3), foundation_w, 0.3,
        color='#888888', label='Betonski temelj (5.4×5.4m)'
    ))

    # Lattice tower outline (trapezoid)
    tower_poly = patches.Polygon([
        (tower_x - base_w, 0),
        (tower_x + base_w, 0),
        (tower_x + top_w, tower_h),
        (tower_x - top_w, tower_h),
    ], closed=True, facecolor='#cccccc', edgecolor='#555555',
       linewidth=1.5, alpha=0.7, label='Rešetkasti stub K2 h=32m')
    ax.add_patch(tower_poly)

    # Lattice diagonals (simplified — 4 visible bays)
    for bay in range(8):
        y0 = bay * 4.0
        y1 = y0 + 4.0
        w0 = base_w - (base_w - top_w) * (y0 / tower_h)
        w1 = base_w - (base_w - top_w) * (y1 / tower_h)
        ax.plot([tower_x - w0, tower_x + w1], [y0, y1], 'k-', linewidth=0.6, alpha=0.5)
        ax.plot([tower_x + w0, tower_x - w1], [y0, y1], 'k-', linewidth=0.6, alpha=0.5)

    # Platform P I at 3m (ice guard / container mount)
    ax.plot([tower_x - base_w - 0.5, tower_x + base_w + 0.5], [3.0, 3.0],
            'b-', linewidth=2, alpha=0.6, label='Platforma P I (h=3m)')

    # Platform P II at 12m (link antennas)
    ax.plot([tower_x - 1.5, tower_x + 1.5], [12.0, 12.0],
            'm--', linewidth=1.5, alpha=0.6, label='Platforma P II (h=12m)')

    # Antenna symbol at top
    ax.annotate('', xy=(tower_x, tower_h + 1.5), xytext=(tower_x, tower_h),
                arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax.text(tower_x + 0.3, tower_h + 1.0, 'Antena', fontsize=8, color='red')

    # ---------- CONTAINER (white, 2.0×3.2×2.3m, south side of tower base) ----------
    container_x = tower_x - foundation_w / 2 - 3.2 - 0.3   # just south of foundation
    ax.add_patch(patches.Rectangle(
        (container_x, 0), 3.2, 2.3,
        facecolor='#f5f5f5', edgecolor='#333333', linewidth=2,
        label='Kontejner (3.2×2.0×2.3m, bijeli)'
    ))
    ax.text(container_x + 1.6, 1.15, 'Kontejner\n(bijeli)', ha='center',
            va='center', fontsize=8, color='#333333')

    # ---------- HUAWEI SMART 3.0 PANELS (2 rows × 6 panels, south of container) ----------
    panels_per_row = 6
    row_width      = panels_per_row * pw
    panel_x_start  = container_x - row_width - 1.0   # 1m gap south of container

    for r in range(2):
        y_base = clearance + r * dz * 1.05   # slight gap between rows
        z_base = clearance + r * dz

        for p in range(panels_per_row):
            px = panel_x_start + p * pw
            poly = patches.Polygon([
                (px,      y_base),
                (px + pw, y_base),
                (px + pw, y_base + dz),
                (px,      y_base + dz),
            ], closed=True,
               facecolor='#1a3a6b' if r == 0 else '#2a5298',
               edgecolor='white', linewidth=0.8, alpha=0.9)
            ax.add_patch(poly)

    ax.text(panel_x_start + row_width / 2, clearance + dz + 0.3,
            '12× Huawei 540W\nSmart 3.0 (45°, Jug)',
            ha='center', va='bottom', fontsize=9, color='#1a3a6b', fontweight='bold')

    # ---------- GROUND ----------
    ax.axhline(0, color='#4a7c2f', linewidth=2.5)
    ax.fill_between([panel_x_start - 1, tower_x + foundation_w / 2 + 1],
                    -0.3, 0, color='#c8e6c9', alpha=0.4)

    # ---------- Shadow arrow (winter sun, ~20° elevation) ----------
    sun_angle = np.radians(20)
    shadow_len = tower_h / np.tan(sun_angle)
    ax.annotate('', xy=(tower_x - shadow_len, 0), xytext=(tower_x, tower_h),
                arrowprops=dict(arrowstyle='->', color='orange',
                                lw=1.5, linestyle='dashed'))
    ax.text(tower_x - shadow_len / 2, 1.5,
            f'Zimska sjena\n(≈{shadow_len:.0f}m)', ha='center',
            fontsize=7, color='darkorange', style='italic')

    # ---------- Annotations ----------
    ax.annotate(f'h=32m', xy=(tower_x + top_w + 0.2, tower_h),
                fontsize=8, va='top')
    ax.set_xlim(panel_x_start - 2, tower_x + foundation_w / 2 + 3)
    ax.set_ylim(-0.8, tower_h + 4)
    ax.set_aspect('equal')
    ax.set_xlabel('Jug ←→ Sjever (m)', fontsize=11)
    ax.set_ylabel('Visina (m)', fontsize=11)
    ax.set_title(
        'RuralStar Sjednica — Bočni presjek sistema\n'
        'Stub K2 h=32m | Huawei Smart 3.0 | Kontejner (bijeli)',
        fontsize=13, fontweight='bold'
    )
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.legend(loc='upper right', fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    log_success(f"Layout sačuvan: {output_path}")


# ---------------------------------------------------------------------------
# Production profile chart
# ---------------------------------------------------------------------------

def create_report(config: dict, df: pd.DataFrame):
    if df is None:
        log_error("Nema podataka za izvještaj.")
        return

    base_path  = os.path.dirname(os.path.abspath(__file__))
    report_dir = os.path.join(base_path, 'report_results')
    os.makedirs(report_dir, exist_ok=True)

    pdf_path    = os.path.join(report_dir, 'RuralStar_Sjednica_FINAL_REPORT.pdf')
    layout_path = os.path.join(report_dir, 'layout.png')

    # Merge flat keys from scenario block into config for convenience
    scenario_cfg = config.get('scenario_A_PowerCube', {})
    merged_cfg   = {**config, **scenario_cfg}

    # 1. Layout
    plot_layout(merged_cfg, layout_path)

    # 2. Monthly balance
    prod_col = 'production_w' if 'production_w' in df.columns else 'pv_w'
    cons_col = 'consumption_w' if 'consumption_w' in df.columns else 'load_w'
    df['month'] = df.index.month
    monthly = df.groupby('month')[[prod_col, cons_col]].sum() / 1000  # kWh

    # 3. Representative days
    seasons = [("Zima", 1, 15), ("Proljeće", 4, 15), ("Ljeto", 7, 15), ("Jesen", 10, 15)]
    days_data = []
    for s_name, m, d in seasons:
        d_data, label = get_representative_day(df, s_name, m, d)
        if d_data is not None:
            days_data.append((label, d_data))

    # 4. Charts
    fig_profiles, axs = plt.subplots(2, 1, figsize=(12, 10))

    x     = np.arange(1, 13)
    width = 0.4
    axs[0].bar(x - width / 2, monthly[prod_col], width,
               label='Proizvodnja (kWh)', color='orange')
    axs[0].bar(x + width / 2, monthly[cons_col], width,
               label='Potrošnja (kWh)', color='red')
    axs[0].set_title("Mjesečni bilans proizvodnje i potrošnje", fontsize=14, fontweight='bold')
    axs[0].set_xticks(x)
    axs[0].set_xticklabels(
        ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
    )
    axs[0].grid(True, axis='y', alpha=0.3)
    axs[0].legend()

    colors_list = ['blue', 'green', 'red', 'purple']
    for i, (label, data) in enumerate(days_data):
        axs[1].plot(data.index.hour, data[prod_col] / 1000,
                    label=label, color=colors_list[i], linewidth=2)
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

    # 5. PDF
    total_prod = df[prod_col].sum() / 1000
    total_cons = df[cons_col].sum() / 1000

    with PdfPages(pdf_path) as pdf:
        fig_title = plt.figure(figsize=(8.5, 11))
        plt.axis('off')
        plt.text(0.5, 0.95, "RURALSTAR SJEDNICA\nFINALNI IZVJEŠTAJ",
                 ha='center', va='center', fontsize=22, fontweight='bold')

        info_text = (
            f"Lokacija: Bileća (Čemerno), BiH\n"
            f"Nadmorska visina: 1076 m\n"
            f"Stub: K2 rešetkasti h=32m\n"
            f"Nosač panela: Huawei Smart 3.0 (tlo)\n"
            f"Instalirana snaga: {scenario_cfg.get('n_panels', 12) * 0.54:.1f} kWp\n\n"
            f"REZULTATI SIMULACIJE:\n"
            f"Godišnja proizvodnja: {total_prod:,.1f} kWh\n"
            f"Godišnja potrošnja:   {total_cons:,.1f} kWh\n"
            f"Bilans:               {total_prod - total_cons:+,.1f} kWh"
        )
        plt.text(0.5, 0.65, info_text, ha='center', va='center', fontsize=13,
                 family='monospace',
                 bbox=dict(boxstyle="round", facecolor="#f0f0f0"))
        pdf.savefig(fig_title)
        plt.close()

        for img_path in [layout_path, profiles_path]:
            if os.path.exists(img_path):
                img = plt.imread(img_path)
                fig = plt.figure(figsize=(11, 8))
                plt.imshow(img)
                plt.axis('off')
                pdf.savefig(fig)
                plt.close()

        fc_path = os.path.join(base_path, 'radiance_results', 'images',
                               'falsecolor_solar_radiance.png')
        if os.path.exists(fc_path):
            img = plt.imread(fc_path)
            fig = plt.figure(figsize=(11, 8))
            plt.imshow(img)
            plt.title("False Color Analiza (Radiance)", fontsize=14, fontweight='bold')
            plt.axis('off')
            pdf.savefig(fig)
            plt.close()

    log_success(f"✅ FINALNI IZVJEŠTAJ: {pdf_path}")


def main():
    log_info("🚀 Generisanje finalnog izvještaja...")
    config, df = load_data()
    create_report(config, df)
    log_success("✅ Proces završen!")


if __name__ == "__main__":
    main()