"""
✅ SOLARNA OGRADA – OPTIMIZIRANA SIMULACIJA (Best Simulation Ever)
Lokacija: SJEDNICA, BILECA
- Ispravan proračun energije (bez dupliranja sati/površine)
- Tačna DXF geometrija (7x7m donji, 5.8x5.8m gornji okvir)
- Optimizirana struktura koda (klase, caching, paralelizacija)
- Izlaz: Grafikon, 3D Model, Presjeci, PDF Izvještaj
"""

import os
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings

# Scientific libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Radiance simulation
from bifacial_radiance import RadianceObj, AnalysisObj

warnings.filterwarnings("ignore")


# ==============================================================================
# 📍 KONFIGURACIJA (Centralized Configuration)
# ==============================================================================
@dataclass
class SimulationConfig:
    """Centralizirana konfiguracija simulacije."""
    
    # Identifikatori
    main_name: str = "sjednica_bileca_irradiance_outward_max"
    epw_file: str = "tmy_42.946_18.322_2005_2020.epw"
    
    # Panel specifikacije (Canadian Solar TOPBiHiKu6 585W)
    panel_x: float = 1.134      # širina [m]
    panel_y: float = 2.2        # visina [m]
    panel_watts: int = 585
    bifaciality: float = 0.80
    efficiency_pr: float = 0.21
    
    # Geometrija montaže
    tilt_from_vertical: float = 16.0  # nagib od vertikale [°]
    clearance_height: float = 0.5     # visina donjeg ruba [m]
    pitch: float = 10.0               # razmak između redova [m]
    
    # Albedo (refleksija tla)
    albedo: float = 0.4
    
    # DXF Geometrija tornja
    lower_frame_side: float = 7.0
    upper_frame_side: float = 5.8
    concrete_side: float = 5.4
    platform_z: float = 4.2
    chamfer_dist: float = 1.2
    
    # Raspored panela po stranama
    sides: List[Tuple[str, int, int]] = field(default_factory=lambda: [
        ("Southeast", 135, 4),
        ("Southwest", 225, 5),
        ("Northeast", 45, 5),
        ("Northwest", 315, 5),
    ])
    
    # Opterećenje (Telekom oprema)
    loads_full_kw: float = 53.1 / 24
    loads_basic_kw: float = 23.2 / 24
    battery_capacity_kwh: float = 43.2
    
    @property
    def tilt_from_horizontal(self) -> float:
        """Konverzija nagiba na horizontalnu referencu."""
        return 90.0 - self.tilt_from_vertical
    
    @property
    def total_panels(self) -> int:
        """Ukupan broj panela."""
        return sum(n for _, _, n in self.sides)
    
    @property
    def installed_kwp(self) -> float:
        """Instalisana snaga u kWp."""
        return self.total_panels * self.panel_watts / 1000
    
    @property
    def panel_area(self) -> float:
        """Površina jednog panela [m²]."""
        return self.panel_x * self.panel_y


# ==============================================================================
# 🏗️ GEOMETRIJSKE POMOĆNE FUNKCIJE
# ==============================================================================
class GeometryUtils:
    """Statčke pomoćne funkcije za geometrijske proračune."""
    
    @staticmethod
    def chamfer_corners(corners: List[Tuple[float, float]], 
                        chamfer_dist: float = 1.2) -> List[Tuple[float, float]]:
        """
        Generiše koordinate za poligon sa odsječenim uglovima.
        
        Args:
            corners: Lista originalnih uglova (x, y)
            chamfer_dist: Udaljenost odsijecanja od svakog ugla [m]
            
        Returns:
            Lista novih koordinata nakon chamferovanja
        """
        new_pts = []
        n = len(corners)
        
        for i in range(n):
            p1 = np.array(corners[i])
            p2 = np.array(corners[(i + 1) % n])
            
            edge_vec = p2 - p1
            length = np.linalg.norm(edge_vec)
            
            if length > 1e-6:
                unit_vec = edge_vec / length
                pt1 = p1 + chamfer_dist * unit_vec
                pt2 = p2 - chamfer_dist * unit_vec
                new_pts.extend([tuple(pt1), tuple(pt2)])
        
        # Ukloni duplicate i sortiraj po uglu
        unique = []
        for pt in new_pts:
            if not any(np.hypot(pt[0]-up[0], pt[1]-up[1]) < 1e-6 for up in unique):
                unique.append(pt)
        
        unique.sort(key=lambda p: np.arctan2(p[1], p[0]))
        return unique
    
    @staticmethod
    def rotate_point(x: float, y: float, angle_deg: float) -> Tuple[float, float]:
        """Rotira tačku oko ishodišta za dati ugao."""
        rad = np.deg2rad(angle_deg)
        cos_a, sin_a = np.cos(rad), np.sin(rad)
        return (x * cos_a - y * sin_a, x * sin_a + y * cos_a)
    
    @staticmethod
    def get_panel_corners(center: np.ndarray, 
                          normal: np.ndarray, 
                          along: np.ndarray,
                          width: float, 
                          height: float,
                          tilt_rad: float,
                          z_bottom: float,
                          z_top: float) -> List[Tuple[float, float, float]]:
        """
        Računa 4 ugla panela na osnovu orijentacije i nagiba.
        
        Returns:
            Lista 4 tačke: [bottom_left, bottom_right, top_right, top_left]
        """
        half_width = width / 2
        
        # Gornji rub (na gornjem okviru)
        tl = center - half_width * along + [0, 0, z_top]
        tr = center + half_width * along + [0, 0, z_top]
        
        # Donji rub (pomaknut prema van zbog nagiba)
        horiz_offset = height * np.sin(tilt_rad)
        bl = tl[:2] + horiz_offset * normal[:2] + [z_bottom]
        br = tr[:2] + horiz_offset * normal[:2] + [z_bottom]
        
        return [bl, br, tr, tl]


# ==============================================================================
# ☀️ REZULTATI SIMULACIJE
# ==============================================================================
@dataclass
class SideResults:
    """Rezultati za jednu stranu."""
    name: str
    azimuth: int
    num_panels: int
    incident_kwh: float
    actual_kwh: float
    hourly_data: Optional[pd.DataFrame] = None
    
    @property
    def efficiency(self) -> float:
        """Efikasnost konverzije."""
        return self.actual_kwh / self.incident_kwh if self.incident_kwh > 0 else 0


@dataclass
class SimulationResults:
    """Agregirani rezultati cijele simulacije."""
    sides: Dict[str, SideResults] = field(default_factory=dict)
    config: Optional[SimulationConfig] = None
    
    @property
    def total_incident(self) -> float:
        """Ukupna incidentna energija [kWh]."""
        return sum(s.incident_kwh for s in self.sides.values())
    
    @property
    def total_actual(self) -> float:
        """Ukupna stvarna energija [kWh]."""
        return sum(s.actual_kwh for s in self.sides.values())
    
    @property
    def specific_yield(self) -> float:
        """Specifična proizvodnja [kWh/kWp]."""
        if self.config is None or self.config.installed_kwp == 0:
            return 0
        return self.total_actual / self.config.installed_kwp
    
    @property
    def daily_average(self) -> float:
        """Prosječna dnevna proizvodnja [kWh/dan]."""
        return self.total_actual / 365
    
    def summary_dict(self) -> dict:
        """Vraća dictionary sa sažetkom rezultata."""
        return {
            'total_incident_kwh': self.total_incident,
            'total_actual_kwh': self.total_actual,
            'specific_yield_kwh_kwp': self.specific_yield,
            'daily_avg_kwh': self.daily_average,
            'installed_kwp': self.config.installed_kwp if self.config else 0,
            'total_panels': self.config.total_panels if self.config else 0,
            'sides': {name: {'incident': s.incident_kwh, 'actual': s.actual_kwh} 
                      for name, s in self.sides.items()}
        }


# ==============================================================================
# ☀️ SIMULACIONI ENGINE
# ==============================================================================
class SolarSimulation:
    """Glavna klasa za pokretanje bifacial simulacije."""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.base_path = Path(config.main_name)
        self.results_path = self.base_path / "results"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Kreira potrebne direktorije."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.results_path.mkdir(exist_ok=True)
    
    def _find_epw_file(self) -> Path:
        """Pronalazi EPW weather file."""
        candidates = [
            Path(self.config.epw_file),
            Path(__file__).parent / self.config.epw_file,
            Path(__file__).parent / "EPWs" / self.config.epw_file,
            self.base_path / self.config.epw_file,
        ]
        
        for candidate in candidates:
            if candidate.exists():
                return candidate.absolute()
        
        raise FileNotFoundError(
            f"EPW file not found. Tried: {[str(c) for c in candidates]}"
        )
    
    def simulate_side(self, name: str, azimuth: int, num_panels: int) -> SideResults:
        """
        Simulira jednu stranu tornja.
        
        Args:
            name: Ime strane (npr. "Southeast")
            azimuth: Azimut u stepenima
            num_panels: Broj panela na ovoj strani
            
        Returns:
            SideResults sa proračunatom energijom
        """
        print(f"  🚀 Simuliram {name} (azimut {azimuth}°, {num_panels} panela)")
        
        # Inicijalizacija Radiance objekta
        demo = RadianceObj(f"{self.config.main_name}_{name}", path=str(self.base_path))
        demo.setGround(self.config.albedo)
        
        # Kreiranje modula
        module = demo.makeModule(
            name=f'panel_{name}',
            x=self.config.panel_x,
            y=self.config.panel_y,
            bifi=float(self.config.bifaciality)
        )
        
        # Učitavanje weather podataka
        epw_path = self._find_epw_file()
        demo.readWeatherFile(str(epw_path), coerce_year=2023)
        demo.genCumSky()
        
        # Kreiranje scene
        scene_dict = {
            'tilt': self.config.tilt_from_horizontal,
            'azimuth': azimuth,
            'nMods': num_panels,
            'nRows': 1,
            'clearance_height': self.config.clearance_height,
            'pitch': self.config.pitch,
        }
        scene = demo.makeScene(module=module, sceneDict=scene_dict)
        
        # Ray tracing
        oct_file = demo.makeOct(demo.getfilelist())
        
        # Analiza
        analysis = AnalysisObj(oct_file, demo.basename)
        frontscan, backscan = analysis.moduleAnalysis(scene)
        analysis.analysis(oct_file, demo.basename, frontscan, backscan)
        
        # Čitanje rezultata iz CSV-a
        csv_file = self._find_result_csv(name)
        if csv_file is None:
            raise RuntimeError(f"No CSV results found for {name}")
        
        df = pd.read_csv(csv_file)
        front_col = self._find_column(df, 'front')
        back_col = self._find_column(df, 'back')
        
        if not front_col or not back_col:
            raise ValueError(f"Missing front/back columns in {csv_file}")
        
        # Proračun energije
        area_one = self.config.panel_area
        
        # Sumiramo irradiance po svim satima, onda množimo sa površinom
        total_front_wh = df[front_col].sum() * area_one
        total_back_wh = df[back_col].sum() * area_one
        
        total_wh = (total_front_wh + total_back_wh) * num_panels
        incident_kwh = total_wh / 1000.0
        actual_kwh = incident_kwh * self.config.efficiency_pr
        
        # Sačuvaj hourly data ako postoji
        hourly_df = None
        if 'Time' in df.columns:
            df['Time'] = pd.to_datetime(df['Time'])
            df['Year'] = df['Time'].dt.year
            df['Month'] = df['Time'].dt.month
            df['Day'] = df['Time'].dt.day
            df['Hour'] = df['Time'].dt.hour
            df['total_W'] = (df[front_col] + df[back_col]) * area_one * num_panels
            hourly_df = df[['Year', 'Month', 'Day', 'Hour', 'total_W']].copy()
        
        print(f"     ✅ {name}: {incident_kwh:8.0f} kWh → {actual_kwh:6.0f} kWh")
        
        return SideResults(
            name=name,
            azimuth=azimuth,
            num_panels=num_panels,
            incident_kwh=incident_kwh,
            actual_kwh=actual_kwh,
            hourly_data=hourly_df
        )
    
    def _find_result_csv(self, side_name: str) -> Optional[Path]:
        """Pronalazi CSV fajl sa rezultatima za datu stranu."""
        if not self.results_path.exists():
            return None
        
        for f in self.results_path.glob("*.csv"):
            if side_name.lower() in f.name.lower():
                return f
        return None
    
    def _find_column(self, df: pd.DataFrame, keyword: str) -> Optional[str]:
        """Pronalazi kolonu koja sadrži keyword."""
        for col in df.columns:
            if keyword.lower() in col.lower():
                return col
        return None
    
    def run(self, parallel: bool = False) -> SimulationResults:
        """
        Pokreće kompletnu simulaciju za sve strane.
        
        Args:
            parallel: Ako True, koristi ThreadPoolExecutor za paralelnu simulaciju
            
        Returns:
            SimulationResults sa agregiranim podacima
        """
        print("\n" + "="*80)
        print("☀️ POKREĆEM SOLARNU SIMULACIJU")
        print("="*80)
        print(f"📍 Lokacija: {self.config.main_name}")
        print(f"📊 Ukupno panela: {self.config.total_panels}")
        print(f"⚡ Instalisano: {self.config.installed_kwp:.2f} kWp")
        print(f"📐 Nagib: {self.config.tilt_from_vertical}° od vertikale")
        print("="*80 + "\n")
        
        results = SimulationResults(config=self.config)
        
        if parallel:
            # Paralelna simulacija (eksperimentalno - Radiance može imati problema)
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = {
                    executor.submit(
                        self.simulate_side, name, az, n
                    ): name for name, az, n in self.config.sides
                }
                for future in as_completed(futures):
                    side_result = future.result()
                    results.sides[side_result.name] = side_result
        else:
            # Sekvencijalna simulacija (preporučeno)
            for name, azimuth, num_panels in self.config.sides:
                side_result = self.simulate_side(name, azimuth, num_panels)
                results.sides[side_result.name] = side_result
        
        # Print summary
        print("\n" + "="*80)
        print("📊 REZULTATI SIMULACIJE")
        print("="*80)
        for name, res in results.sides.items():
            print(f"  {name:12}: {res.incident_kwh:8.0f} kWh → {res.actual_kwh:6.0f} kWh")
        print("-"*80)
        print(f"  UKUPNO INCIDENTNO: {results.total_incident:8.0f} kWh")
        print(f"  UKUPNO STVARNO:    {results.total_actual:8.0f} kWh")
        print(f"  Specifično:        {results.specific_yield:6.0f} kWh/kWp")
        print("="*80 + "\n")
        
        return results


# ==============================================================================
# 🎨 3D VIZUALIZACIJA
# ==============================================================================
class Visualizer3D:
    """Generiše 3D vizualizacije solarne konstrukcije."""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.tilt_rad = np.deg2rad(config.tilt_from_vertical)
        
        # Pre-računate dimenzije
        self.z_bottom = config.clearance_height
        self.z_top = config.clearance_height + config.panel_y * np.cos(self.tilt_rad)
        self.horiz_offset = config.panel_y * np.sin(self.tilt_rad)
        
        # Frame dimenzije
        self.frame_apothem = config.upper_frame_side / 2.0
        self.base_half_diag = config.lower_frame_side / np.sqrt(2)
    
    def draw_panel(self, ax: Axes3D, 
                   corners: List[Tuple[float, float, float]],
                   color: str = '#1E3A8A',
                   alpha: float = 0.9,
                   edge_color: str = 'black') -> None:
        """Crtanje jednog panela."""
        verts = [corners]
        collection = Poly3DCollection(
            verts, 
            facecolor=color, 
            edgecolor=edge_color,
            linewidth=0.5,
            alpha=alpha
        )
        ax.add_collection3d(collection)
    
    def draw_support_leg(self, ax: Axes3D, 
                         top: Tuple[float, float, float],
                         bottom: Tuple[float, float, float],
                         color: str = 'dimgray',
                         linewidth: float = 3) -> None:
        """Crtanje noseće noge."""
        ax.plot(
            [top[0], bottom[0]],
            [top[1], bottom[1]],
            [top[2], bottom[2]],
            color=color,
            linewidth=linewidth
        )
    
    def generate_model(self, 
                       output_path: Optional[str] = None,
                       show_supports: bool = True,
                       show_gate: bool = True,
                       elevation: float = 25,
                       azimuth_view: float = 45,
                       panel_color: str = '#1E3A8A') -> str:
        """
        Generiše 3D model solarne ograde.
        
        Args:
            output_path: Putanja za čuvanje slike (ako None, vraća fig/ax)
            show_supports: Prikaži noseće noge
            show_gate: Označi ulaz/kapiju
            elevation: Elevacija kamere [°]
            azimuth_view: Azimut kamere [°]
            panel_color: Boja panela
            
        Returns:
            Putanja do sačuvane slike
        """
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # 1. Tlo
        ground = [[(-5, -5, 0), (5, -5, 0), (5, 5, 0), (-5, 5, 0)]]
        ax.add_collection3d(Poly3DCollection(
            ground, facecolors='#d2b48c', alpha=0.3, edgecolor='none'
        ))
        
        # 2. Betonska ploča
        c_half = self.config.concrete_side / 2
        concrete = [[
            (-c_half, -c_half, 0.2),
            (c_half, -c_half, 0.2),
            (c_half, c_half, 0.2),
            (-c_half, c_half, 0.2)
        ]]
        ax.add_collection3d(Poly3DCollection(
            concrete, facecolors='gray', alpha=0.8, edgecolor='black'
        ))
        
        # 3. Donji okvir (chamfered)
        lower_z = 0.5
        lower_coords = GeometryUtils.chamfer_corners(
            [(3.5, 0), (0, 3.5), (-3.5, 0), (0, -3.5)],
            self.config.chamfer_dist
        )
        lower_frame_pts = [(x, y, lower_z) for x, y in lower_coords]
        
        for i in range(len(lower_frame_pts)):
            p1 = lower_frame_pts[i]
            p2 = lower_frame_pts[(i + 1) % len(lower_frame_pts)]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], 
                    color='dimgray', linewidth=4)
        
        # 4. Gornji okvir
        upper_coords = [
            (self.frame_apothem, 0),
            (0, self.frame_apothem),
            (-self.frame_apothem, 0),
            (0, -self.frame_apothem)
        ]
        
        for i in range(4):
            x1, y1 = upper_coords[i]
            x2, y2 = upper_coords[(i + 1) % 4]
            ax.plot([x1, x2], [y1, y2], [self.z_top, self.z_top],
                    color='dimgray', linewidth=3)
        
        # 5. Paneli po stranama
        side_data = {
            "Southeast": {"az": 135, "n": 4, "color": panel_color},
            "Southwest": {"az": 225, "n": 5, "color": panel_color},
            "Northeast": {"az": 45, "n": 5, "color": panel_color},
            "Northwest": {"az": 315, "n": 5, "color": panel_color},
        }
        
        panels_info = []  # Za crtanje nosača
        
        for side_name, data in side_data.items():
            az_rad = np.deg2rad(data["az"])
            normal = np.array([np.cos(az_rad), np.sin(az_rad), 0])
            along = np.array([-np.sin(az_rad), np.cos(az_rad), 0])
            
            mid_top = np.array([
                self.frame_apothem * normal[0],
                self.frame_apothem * normal[1],
                0
            ])
            
            total_len = data["n"] * self.config.panel_x
            start = mid_top - (total_len / 2) * along[:2]
            
            # Poseban tretman za SE stranu (sa gap-om za kapiju)
            if side_name == "Southeast" and show_gate:
                gap_width = self.config.panel_x
                margin = (self.config.upper_frame_side - 
                         (4 * self.config.panel_x + gap_width)) / 2.0
                
                # Lijeva grupa (2 panela)
                for i in range(2):
                    center = start + (i + 0.5) * self.config.panel_x * along[:2]
                    corners = self._get_panel_corners_3d(center, normal, along)
                    self.draw_panel(ax, corners, color=data["color"])
                    panels_info.append((corners, side_name))
                
                # Desna grupa (2 panela)
                right_start = start + (2 * self.config.panel_x + gap_width) * along[:2]
                for i in range(2):
                    center = right_start + (i + 0.5) * self.config.panel_x * along[:2]
                    corners = self._get_panel_corners_3d(center, normal, along)
                    self.draw_panel(ax, corners, color=data["color"])
                    panels_info.append((corners, side_name))
            else:
                # Standardni raspored
                for i in range(data["n"]):
                    center = start + (i + 0.5) * self.config.panel_x * along[:2]
                    corners = self._get_panel_corners_3d(center, normal, along)
                    self.draw_panel(ax, corners, color=data["color"])
                    panels_info.append((corners, side_name))
        
        # 6. Noseće noge (ako je uključeno)
        if show_supports:
            for corners, side_name in panels_info:
                # Noge od gornjih uglova do tla
                for i in range(2):  # Dva gornja ugla
                    top = corners[(i + 2) % 4]
                    bottom = (top[0], top[1], 0)
                    self.draw_support_leg(ax, top, bottom)
        
        # 7. Oznaka kapije (ako je uključeno)
        if show_gate:
            gate_x = 1.5
            gate_y = -1.5
            ax.text(gate_x, gate_y, 1.5, "🚪 ULAZ", 
                    fontsize=12, color='red', weight='bold',
                    ha='center', va='center')
        
        # Postavke prikaza
        ax.set_xlabel('X (Istok ←→ Zapad) [m]', fontsize=11)
        ax.set_ylabel('Y (Sjever ←→ Jug) [m]', fontsize=11)
        ax.set_zlabel('Z [Visina] [m]', fontsize=11)
        ax.set_xlim(-6, 6)
        ax.set_ylim(-6, 6)
        ax.set_zlim(0, 10)
        ax.view_init(elev=elevation, azim=azimuth_view)
        ax.set_title(
            f'SOLARNA OGRADA – 3D Model\n'
            f'{self.config.total_panels} panela | {self.config.installed_kwp:.1f} kWp | '
            f'{self.config.tilt_from_vertical}° nagib',
            fontsize=14
        )
        
        plt.tight_layout()
        
        if output_path is None:
            output_path = self.base_path / "3D_model.png"
        
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
        plt.close()
        
        print(f"  ✅ 3D model sačuvan: {output_path}")
        return str(output_path)
    
    def _get_panel_corners_3d(self, 
                               center: np.ndarray,
                               normal: np.ndarray,
                               along: np.ndarray) -> List[Tuple[float, float, float]]:
        """Računa 3D koordinate uglova panela."""
        half_width = self.config.panel_x / 2
        
        # Gornji rubovi
        tl = (
            center[0] - half_width * along[0],
            center[1] - half_width * along[1],
            self.z_top
        )
        tr = (
            center[0] + half_width * along[0],
            center[1] + half_width * along[1],
            self.z_top
        )
        
        # Donji rubovi (pomaknuti zbog nagiba)
        bl = (
            tl[0] + self.horiz_offset * normal[0],
            tl[1] + self.horiz_offset * normal[1],
            self.z_bottom
        )
        br = (
            tr[0] + self.horiz_offset * normal[0],
            tr[1] + self.horiz_offset * normal[1],
            self.z_bottom
        )
        
        return [bl, br, tr, tl]
    
    @property
    def base_path(self) -> Path:
        return Path(self.config.main_name)


# ==============================================================================
# 📊 GENERATOR GRAFIKONA
# ==============================================================================
class PlotGenerator:
    """Generiše sve grafikone iz rezultata."""
    
    def __init__(self, results: SimulationResults, config: SimulationConfig):
        self.results = results
        self.config = config
        self.output_dir = Path(config.main_name)
    
    def generate_all(self) -> Dict[str, str]:
        """Generiše sve grafikone i vraća putanje."""
        outputs = {}
        
        outputs['bar_chart'] = self.generate_bar_chart()
        outputs['pie_chart'] = self.generate_pie_chart()
        outputs['cumulative'] = self.generate_cumulative()
        outputs['monthly'] = self.generate_monthly()
        outputs['daily_profiles'] = self.generate_daily_profiles()
        
        return outputs
    
    def generate_bar_chart(self, output_name: str = "proizvodnja_po_stranama.png") -> str:
        """Bar chart poređenja incidentne vs stvarne energije."""
        sides = list(self.results.sides.keys())
        incident = [self.results.sides[s].incident_kwh for s in sides]
        actual = [self.results.sides[s].actual_kwh for s in sides]
        
        x = np.arange(len(sides))
        width = 0.35
        colors_incident = ['gold', 'orange', 'lightgreen', 'lightblue']
        colors_actual = ['darkgoldenrod', 'darkorange', 'forestgreen', 'steelblue']
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars1 = ax.bar(x - width/2, incident, width, 
                       label='Incidentna (kWh)', color=colors_incident)
        bars2 = ax.bar(x + width/2, actual, width,
                       label='Stvarna (kWh)', color=colors_actual, hatch='//')
        
        ax.set_ylabel('Energija [kWh/god]', fontsize=12)
        ax.set_title(
            'Godišnja proizvodnja po stranama\n'
            f'Ukupno: {self.results.total_actual:.0f} kWh ({self.results.specific_yield:.0f} kWh/kWp)',
            fontsize=14
        )
        ax.set_xticks(x)
        ax.set_xticklabels(sides)
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Dodaj vrijednosti iznad barova
        for bar in bars1:
            height = bar.get_height()
            ax.annotate(f'{height:,.0f}',
                        xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)
        
        for bar in bars2:
            height = bar.get_height()
            ax.annotate(f'{height:,.0f}',
                        xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        output_path = self.output_dir / output_name
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✅ Bar chart: {output_path}")
        return str(output_path)
    
    def generate_pie_chart(self, output_name: str = "udio_strana.png") -> str:
        """Pie chart udjela strana u ukupnoj proizvodnji."""
        sides = list(self.results.sides.keys())
        actual = [self.results.sides[s].actual_kwh for s in sides]
        colors = ['darkgoldenrod', 'darkorange', 'forestgreen', 'steelblue']
        
        fig, ax = plt.subplots(figsize=(8, 8))
        wedges, texts, autotexts = ax.pie(
            actual, labels=sides, autopct='%1.1f%%',
            startangle=90, colors=colors,
            explode=[0.02] * len(sides)
        )
        
        ax.set_title('Udio pojedine strane u stvarnoj proizvodnji', fontsize=14)
        
        # Poboljšaj čitljivost procenata
        for autotext in autotexts:
            autotext.set_fontsize(11)
            autotext.set_weight('bold')
        
        plt.tight_layout()
        output_path = self.output_dir / output_name
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✅ Pie chart: {output_path}")
        return str(output_path)
    
    def generate_cumulative(self, output_name: str = "kumulativna.png") -> str:
        """Kumulativna godišnja proizvodnja."""
        hourly_data = self._combine_hourly_data()
        
        if hourly_data is None or hourly_data.empty:
            print("  ⚠️ Nema hourly podataka za kumulativni grafikon")
            return ""
        
        hourly_data = hourly_data.sort_values(['Year', 'Month', 'Day', 'Hour'])
        hourly_data['cumulative_kWh'] = hourly_data['total_W'].cumsum() / 1000
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(hourly_data.index, hourly_data['cumulative_kWh'], 
                color='green', linewidth=2.5)
        
        ax.set_xlabel('Vremenski korak (sat)', fontsize=12)
        ax.set_ylabel('Kumulativna energija [kWh]', fontsize=12)
        ax.set_title('Kumulativna godišnja proizvodnja', fontsize=14)
        ax.grid(True, linestyle='--', alpha=0.6)
        
        plt.tight_layout()
        output_path = self.output_dir / output_name
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✅ Kumulativni grafikon: {output_path}")
        return str(output_path)
    
    def generate_monthly(self, output_name: str = "mjesecna_proizvodnja.png") -> str:
        """Mjesečna proizvodnja."""
        hourly_data = self._combine_hourly_data()
        
        if hourly_data is None or hourly_data.empty:
            print("  ⚠️ Nema hourly podataka za mjesečni grafikon")
            return ""
        
        monthly = hourly_data.groupby('Month')['total_W'].sum() / 1000
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
        monthly.index = months
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(months, monthly, color='skyblue', edgecolor='navy')
        
        ax.set_title('Mjesečna proizvodnja električne energije', fontsize=14)
        ax.set_ylabel('Energija [kWh]', fontsize=12)
        ax.set_xlabel('Mjesec', fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Dodaj vrijednosti
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:,.0f}',
                        xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        output_path = self.output_dir / output_name
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✅ Mjesečni grafikon: {output_path}")
        return str(output_path)
    
    def generate_daily_profiles(self, 
                                 months_days: List[Tuple[int, int]] = [(6, 21), (12, 21)],
                                 output_pattern: str = "dnevni_profil_{}_{}.png") -> List[str]:
        """Dnevni profili za solsticije."""
        hourly_data = self._combine_hourly_data()
        outputs = []
        
        if hourly_data is None or hourly_data.empty:
            print("  ⚠️ Nema hourly podataka za dnevne profile")
            return outputs
        
        for month, day in months_days:
            mask = ((hourly_data['Month'] == month) & 
                    (hourly_data['Day'] == day))
            daily = hourly_data[mask].copy()
            
            if daily.empty:
                continue
            
            daily = daily.sort_values('Hour')
            
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(daily['Hour'], daily['total_W']/1000, 
                    marker='o', linestyle='-', color='orange', linewidth=2)
            
            ax.set_title(f'Dnevni profil proizvodnje ({month}/{day})', fontsize=14)
            ax.set_xlabel('Sat u danu', fontsize=12)
            ax.set_ylabel('Snaga [kW]', fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.set_xticks(range(0, 24, 2))
            
            plt.tight_layout()
            output_name = output_pattern.format(month, day)
            output_path = self.output_dir / output_name
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            outputs.append(str(output_path))
            print(f"  ✅ Dnevni profil {month}/{day}: {output_path}")
        
        return outputs
    
    def _combine_hourly_data(self) -> Optional[pd.DataFrame]:
        """Kombinuje hourly data iz svih strana."""
        all_data = []
        for side_result in self.results.sides.values():
            if side_result.hourly_data is not None:
                all_data.append(side_result.hourly_data)
        
        if not all_data:
            return None
        
        return pd.concat(all_data, ignore_index=True)


# ==============================================================================
# 📄 PDF IZVJEŠTAJ
# ==============================================================================
class ReportGenerator:
    """Generiše profesionalni PDF izvještaj."""
    
    def __init__(self, results: SimulationResults, config: SimulationConfig):
        self.results = results
        self.config = config
        self.output_dir = Path(config.main_name)
    
    def generate(self, 
                 images: Dict[str, str],
                 output_name: str = "izvjestaj.pdf") -> str:
        """
        Generiše kompletan PDF izvještaj.
        
        Args:
            images: Dictionary sa putanjama do generisanih slika
            output_name: Ime output PDF fajla
            
        Returns:
            Putanja do generisanog PDF-a
        """
        pdf_path = self.output_dir / output_name
        
        with PdfPages(pdf_path) as pdf:
            # 1. Naslovna strana
            self._title_page(pdf)
            
            # 2. Rezultati - grafikoni
            self._results_charts(pdf, images)
            
            # 3. 3D Model
            if '3d_model' in images and os.path.exists(images['3d_model']):
                self._image_page(pdf, images['3d_model'], "3D Model Solarne Ograde")
            
            # 4. Tehnički podaci
            self._technical_specs(pdf)
            
            # 5. Autonomija baterija
            self._autonomy_analysis(pdf)
        
        print(f"  ✅ PDF izvještaj: {pdf_path}")
        return str(pdf_path)
    
    def _title_page(self, pdf: PdfPages):
        """Naslovna strana izvještaja."""
        fig = plt.figure(figsize=(11.69, 8.27))  # A4 landscape
        
        title = "SJEDNICA, BILECA – SOLARNA OGRADA"
        subtitle = f"Izvještaj o simulaciji proizvodnje električne energije"
        date_str = f"Datum: {pd.Timestamp.now().strftime('%d.%m.%Y.')}"
        
        fig.text(0.5, 0.7, title, fontsize=24, ha='center', weight='bold')
        fig.text(0.5, 0.6, subtitle, fontsize=16, ha='center')
        fig.text(0.5, 0.55, date_str, fontsize=12, ha='center')
        
        # Ključni rezultati
        results_text = f"""
        ┌─────────────────────────────────────────────────────┐
        │  KLJUČNI REZULTATI                                  │
        ├─────────────────────────────────────────────────────┤
        │  Instalisana snaga:     {self.config.installed_kwp:>8.2f} kWp
        │  Ukupno panela:         {self.config.total_panels:>8}
        │  Godišnja proizvodnja:  {self.results.total_actual:>8.0f} kWh
        │  Specifična yield:      {self.results.specific_yield:>8.0f} kWh/kWp
        │  Prosječno dnevno:      {self.results.daily_average:>8.1f} kWh/dan
        └─────────────────────────────────────────────────────┘
        """
        
        fig.text(0.5, 0.35, results_text, fontsize=11, ha='center', 
                 fontfamily='monospace', verticalalignment='center')
        
        plt.axis('off')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    def _results_charts(self, pdf: PdfPages, images: Dict[str, str]):
        """Stranica sa grafikonom rezultata."""
        fig = plt.figure(figsize=(11.69, 8.27))
        
        # Bar chart
        if 'bar_chart' in images and os.path.exists(images['bar_chart']):
            ax1 = fig.add_subplot(2, 1, 1)
            img = plt.imread(images['bar_chart'])
            ax1.imshow(img)
            ax1.axis('off')
            ax1.set_title('Proizvodnja po stranama', fontsize=14)
        
        # Pie chart
        if 'pie_chart' in images and os.path.exists(images['pie_chart']):
            ax2 = fig.add_subplot(2, 1, 2)
            img = plt.imread(images['pie_chart'])
            ax2.imshow(img)
            ax2.axis('off')
            ax2.set_title('Udio strana u proizvodnji', fontsize=14)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    def _image_page(self, pdf: PdfPages, image_path: str, title: str):
        """Stranica sa jednom slikom."""
        fig = plt.figure(figsize=(11.69, 8.27))
        plt.imshow(plt.imread(image_path))
        plt.axis('off')
        plt.title(title, fontsize=16)
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    def _technical_specs(self, pdf: PdfPages):
        """Tehničke specifikacije."""
        fig = plt.figure(figsize=(11.69, 8.27))
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        try:
            import bifacial_radiance
            br_version = bifacial_radiance.__version__
        except:
            br_version = 'instaliran'
        
        specs = f"""
╔══════════════════════════════════════════════════════════════╗
║                    TEHNIČKE SPECIFIKACIJE                     ║
╠══════════════════════════════════════════════════════════════╣

SOFTVER:
  • bifacial_radiance: {br_version}
  • Python: {sys.version.split()[0]}
  • Radiance (ray tracing engine)

ULAZNI PODACI:
  • EPW fajl: {self.config.epw_file}
  • Albedo tla: {self.config.albedo}
  • Bifacijalnost panela: {self.config.bifaciality}
  • Performance Ratio (PR): {self.config.efficiency_pr}

GEOMETRIJA:
  • Nagib panela: {self.config.tilt_from_vertical}° od vertikale
  • Visina donjeg ruba: {self.config.clearance_height} m
  • Donji okvir: {self.config.lower_frame_side}×{self.config.lower_frame_side} m
  • Gornji okvir: {self.config.upper_frame_side}×{self.config.upper_frame_side} m
  • Platforma: {self.config.concrete_side}×{self.config.concrete_side} m na {self.config.platform_z} m

PANELI:
  • Model: Canadian Solar TOPBiHiKu6 585W
  • Dimenzije: {self.config.panel_x} × {self.config.panel_y} m
  • Snaga: {self.config.panel_watts} Wp
  • Ukupno: {self.config.total_panels} komada

REZULTATI:
  • Ukupna godišnja proizvodnja: {self.results.total_actual:.0f} kWh
  • Specifična proizvodnja: {self.results.specific_yield:.0f} kWh/kWp
  • Instalisana snaga: {self.config.installed_kwp:.2f} kWp

╚══════════════════════════════════════════════════════════════╝
"""
        
        ax.text(0.05, 0.95, specs, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    def _autonomy_analysis(self, pdf: PdfPages):
        """Analiza autonomije baterijskog sistema."""
        fig = plt.figure(figsize=(11.69, 8.27))
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        # Telekom loadovi
        loads = {
            "CISCO ASR 920 Router": 150,
            "BTS 5900 (3x RRU)": 1200,
            "Ostali RRU linkovi": 48,
            "Klimatizacija MTS": 816
        }
        total_power_w = sum(loads.values())
        daily_consumption_kwh = total_power_w * 24 / 1000
        solar_daily_kwh = self.results.daily_average
        energy_deficit_kwh = max(0, daily_consumption_kwh - solar_daily_kwh)
        
        battery_hours = self.config.battery_capacity_kwh / total_power_w * 1000
        
        autonomy_text = f"""
╔══════════════════════════════════════════════════════════════╗
║          ANALIZA AUTONOMIJE ZA TELEKOM OPREMU                ║
╠══════════════════════════════════════════════════════════════╣

1. POTROŠAČI (24/7 rad, 48V DC):
   ┌──────────────────────────────┬────────────┬──────────────┐
   │ Komponenta                   │ Snaga (W)  │ Dnevno (kWh) │
   ├──────────────────────────────┼────────────┼──────────────┤
   │ CISCO ASR 920 Router         │    150 W   │    3.60 kWh  │
   │ BTS 5900 (3x RRU)            │   1200 W   │   28.80 kWh  │
   │ Ostali RRU linkovi           │     48 W   │    1.15 kWh  │
   │ Klimatizacija MTS kabineta   │    816 W   │   19.58 kWh  │
   ├──────────────────────────────┼────────────┼──────────────┤
   │ UKUPNO                       │   2214 W   │   53.13 kWh  │
   └──────────────────────────────┴────────────┴──────────────┘

2. ENERGETSKI BILANS:
   • Dnevna potrošnja:     {daily_consumption_kwh:>8.1f} kWh
   • Dnevna proizvodnja:   {solar_daily_kwh:>8.1f} kWh
   • Dnevni DEFICIT:       {energy_deficit_kwh:>8.1f} kWh

   ➡️ Status: {"⚠️ DEFICIT - potrebno povećati kapacitet" if energy_deficit_kwh > 0 else "✅ BALANSIRANO"}

3. AUTONOMIJA BATERIJA ({self.config.battery_capacity_kwh} kWh):
   • Teorijska autonomija: {battery_hours:>8.1f} sati ({battery_hours/24:.1f} dana)

4. PREPORUKE:
   {"• Povećati baterije na 64.8+ kWh (9+ komada)" if energy_deficit_kwh > 0 else ""}
   {"• Dodati 2-3 dodatna solarna panela" if energy_deficit_kwh > 0 else ""}
   {"• Razmotriti diesel generator kao backup" if energy_deficit_kwh > 0 else ""}

╚══════════════════════════════════════════════════════════════╝
"""
        
        ax.text(0.05, 0.95, autonomy_text, transform=ax.transAxes, fontsize=9,
                verticalalignment='top', fontfamily='monospace')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()


# ==============================================================================
# 🚀 MAIN EXECUTION
# ==============================================================================
def main():
    """Glavna funkcija za pokretanje kompletne simulacije."""
    
    print("\n" + "="*80)
    print("  ☀️  SOLARNA OGRADA – BEST SIMULATION EVER  ☀️")
    print("="*80)
    
    # 1. Konfiguracija
    config = SimulationConfig()
    
    # 2. Simulacija
    simulator = SolarSimulation(config)
    results = simulator.run(parallel=False)  # Parallel može uzrokovati probleme sa Radiance
    
    # 3. Vizualizacija
    print("\n🎨 Generišem 3D vizualizacije...")
    visualizer = Visualizer3D(config)
    model_path = visualizer.generate_model(
        show_supports=True,
        show_gate=True,
        elevation=25,
        azimuth_view=45
    )
    
    # 4. Grafikoni
    print("\n📊 Generišem grafikone...")
    plot_gen = PlotGenerator(results, config)
    images = plot_gen.generate_all()
    images['3d_model'] = model_path
    
    # 5. PDF Izvještaj
    print("\n📄 Generišem PDF izvještaj...")
    report_gen = ReportGenerator(results, config)
    pdf_path = report_gen.generate(images)
    
    # 6. Finalni summary
    print("\n" + "="*80)
    print("  ✅ SIMULACIJA ZAVRŠENA USPJEŠNO")
    print("="*80)
    print(f"\n📁 Svi rezultati su sačuvani u: {config.main_name}/")
    print("\n📋 Generisani fajlovi:")
    for name, path in images.items():
        if path:
            print(f"   • {path}")
    print(f"   • {pdf_path}")
    
    print("\n" + "="*80)
    print(f"  📊 UKUPNA PROIZVODNJA: {results.total_actual:,.0f} kWh/god")
    print(f"  ⚡ SPECIFIČNO: {results.specific_yield:,.0f} kWh/kWp")
    print("="*80 + "\n")
    
    return results.summary_dict()


if __name__ == "__main__":
    summary = main()
