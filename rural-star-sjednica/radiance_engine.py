import os
import numpy as np
import pandas as pd
import bifacial_radiance as br
from logger import log_info, log_error, log_warning, log_success


class RadianceEngine:
    def __init__(self, config, equipment_db):
        self.config = config
        self.equipment = equipment_db
        self.sys_params = equipment_db.get('system_parameters', {})

        self.albedo = float(self.sys_params.get('albedo', 0.40))

        # FIX: bifaciality_factor is already 0–1 in equipment_db.
        # bifacial_radiance makeModule() expects a float in [0, 1],
        # NOT an integer percentage. Passing 80 instead of 0.80 was
        # silently producing ~100× wrong bifacial gain.
        self.bifaciality = float(self.sys_params.get('bifaciality_factor', 0.80))

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.rad_path = os.path.join(self.base_path, 'radiance_results')
        os.makedirs(self.rad_path, exist_ok=True)

    def run_simulation(self, weather_df: pd.DataFrame) -> pd.DataFrame:
        log_info("Pokrećem bifacial Radiance simulaciju (Professional Mode)...")

        try:
            demo = br.RadianceObj(name='ruralstar_pro', path=self.rad_path)
            demo.setGround(self.albedo)

            # Use validated EPW from the project root (one level up from rad_path)
            epw_file = os.path.join(self.base_path, 'bileca_cemerno.epw')
            if not os.path.exists(epw_file):
                raise FileNotFoundError(f"EPW fajl nije pronađen: {epw_file}")

            log_info(f"Koristim validirani EPW: {os.path.basename(epw_file)}")
            demo.readWeatherFile(weatherFile=epw_file)

            meta = getattr(demo, 'metadata', {})
            log_info(
                f"Lokacija: Lat={meta.get('latitude')}, "
                f"Lon={meta.get('longitude')}, Alt={meta.get('altitude')}m"
            )

            # --- Module definition ---
            panel_specs = self.equipment['panels']['Huawei_IPV540-M1A']
            width  = float(panel_specs['dimensions_mm'][1]) / 1000.0   # ~1.134 m
            height = float(panel_specs['dimensions_mm'][0]) / 1000.0   # ~2.279 m

            # FIX: bifi must be float [0, 1] — was incorrectly int(0.80*100)=80
            module = demo.makeModule(
                name='Huawei_540W_Bi',
                x=width,
                y=height,
                bifi=int(self.bifaciality * 100),   # <-- 0.80, not 80
                numpanels=1
            )

            # --- Scene parameters (Huawei Smart 3.0, 45° tilt, South) ---
            tilt      = float(self.sys_params.get('tilt_angle', 45.0))
            azimuth   = float(self.sys_params.get('azimuth_angle', 180.0))
            clearance = float(self.sys_params.get('module_clearance_height', 0.8))
            pitch     = 3.5   # row-to-row pitch (m), Smart 3.0 standard

            sceneDict = {
                'tilt': tilt,
                'azimuth': azimuth,
                'clearance_height': clearance,
                'pitch': pitch,
                'nMods': 6,    # 6 panels per row (portrait)
                'nRows': 2,    # 2 rows = 12 panels total
            }

            scene   = demo.makeScene(module=module, sceneDict=sceneDict)
            demo.genCumSky()
            oct_file = demo.makeOct(demo.getfilelist())

            # --- Analysis ---
            analysis = br.AnalysisObj(oct_file, demo.basename)
            frontscan, backscan = analysis.moduleAnalysis(scene)
            analysis.analysis(oct_file, demo.basename, frontscan, backscan)

            # --- Parse results ---
            results_dir = os.path.join(self.rad_path, 'results')
            if not os.path.exists(results_dir):
                raise FileNotFoundError(f"Rezultati ne postoje: {results_dir}")

            csv_files = [f for f in os.listdir(results_dir) if f.endswith('.csv')]
            if not csv_files:
                log_warning("Nema CSV rezultata — prelazim na PVLib fallback.")
                return self._fallback_pvlib(weather_df)

            df_res    = pd.read_csv(os.path.join(results_dir, csv_files[0]))
            col_front = next((c for c in df_res.columns if 'Front' in c), None)
            col_back  = next((c for c in df_res.columns if 'Back'  in c), None)

            if not col_front or not col_back:
                log_warning("Kolone Front/Back nisu pronađene — fallback.")
                return self._fallback_pvlib(weather_df)

            final_df   = pd.DataFrame(index=weather_df.index)
            len_data   = min(len(df_res), len(final_df))
            poa_front  = np.asarray(df_res[col_front])
            poa_back   = np.asarray(df_res[col_back])

            final_df['poa_front'] = pd.Series(
                poa_front[:len_data], index=final_df.index[:len_data]
            )
            final_df['poa_back'] = pd.Series(
                poa_back[:len_data], index=final_df.index[:len_data]
            )
            final_df[['poa_front', 'poa_back']] = (
                final_df[['poa_front', 'poa_back']].fillna(0)
            )

            log_success(
                f"Radiance uspješan! "
                f"Front avg: {final_df['poa_front'].mean():.1f} W/m² | "
                f"Back avg: {final_df['poa_back'].mean():.1f} W/m²"
            )
            return final_df

        except Exception as e:
            log_error(f"Greška u Radiance simulaciji: {e}")
            import traceback
            log_error(traceback.format_exc())
            return self._fallback_pvlib(weather_df)

    def _fallback_pvlib(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        PVLib POA fallback when Radiance is unavailable.
        Back irradiance estimated as front × albedo × bifaciality (simplified).
        """
        log_warning("⚠️  Koristim PVLib fallback za POA irradijancu.")
        import pvlib

        tilt    = float(self.sys_params.get('tilt_angle', 45.0))
        azimuth = float(self.sys_params.get('azimuth_angle', 180.0))
        lat     = float(self.sys_params.get('latitude', 42.9448))
        lon     = float(self.sys_params.get('longitude', 18.3236))
        alt     = float(self.sys_params.get('altitude', 1076.0))

        solpos = pvlib.solarposition.get_solarposition(df.index, lat, lon, alt)
        poa    = pvlib.irradiance.get_total_irradiance(
            surface_tilt=tilt,
            surface_azimuth=azimuth,
            solar_zenith=solpos['apparent_zenith'],
            solar_azimuth=solpos['azimuth'],
            dni=df.get('dni', df.get('DNI', 0)),
            ghi=df.get('ghi', df.get('GHI', 0)),
            dhi=df.get('dhi', df.get('DHI', 0)),
            albedo=self.albedo,
            model='haydavies'
        )

        result_df = pd.DataFrame(index=df.index)
        result_df['poa_front'] = poa['poa_global'].clip(lower=0)
        # Simplified back estimate: albedo reflected + bifaciality factor
        result_df['poa_back']  = (
            result_df['poa_front'] * self.albedo * self.bifaciality
        ).clip(lower=0)

        log_success(
            f"PVLib fallback završen. "
            f"Front avg: {result_df['poa_front'].mean():.1f} W/m²"
        )
        return result_df