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
        self.bifaciality = float(self.sys_params.get('bifaciality_factor', 0.80))
        
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.rad_path = os.path.join(self.base_path, 'radiance_results')
        os.makedirs(self.rad_path, exist_ok=True)

    def run_simulation(self, weather_df):
        log_info("Pokrećem bifacial Radiance simulaciju (Professional Mode)...")
        
        try:
            demo = br.RadianceObj(name='ruralstar_pro', path=self.rad_path)
            demo.setGround(self.albedo)
            
            # --- KLJUČNA PROMJENA: Korišćenje stvarnog EPW fajla ---
            epw_file = os.path.join(self.rad_path, 'bileca_cemerno.epw')
            if not os.path.exists(epw_file):
                raise FileNotFoundError(f"EPW fajl nije pronađen: {epw_file}")
            
            log_info(f"Koristim validirani EPW: {os.path.basename(epw_file)}")
            demo.readWeatherFile(weatherFile=epw_file)
            
            # Provjera metapodataka
            meta = getattr(demo, 'metadata', {})
            log_info(f"Lokacija: Lat={meta.get('latitude')}, Lon={meta.get('longitude')}, Alt={meta.get('altitude')}m")

            # Definisanje modula
            panel_specs = self.equipment['panels']['Huawei_IPV540-M1A']
            width = float(panel_specs['dimensions_mm'][1]) / 1000.0
            height = float(panel_specs['dimensions_mm'][0]) / 1000.0
            bifi_val = int(self.bifaciality * 100)

            module = demo.makeModule(
                name='Huawei_540W_Bi',
                x=width,
                y=height,
                bifi=bifi_val,
                numpanels=1
            )

            # Parametri scene
            tilt = float(self.sys_params.get('tilt_angle', 45.0))
            azimuth = float(self.sys_params.get('azimuth_angle', 180.0))
            clearance = float(self.sys_params.get('module_clearance_height', 0.5))
            pitch = 3.0
            
            sceneDict = {
                'tilt': tilt,
                'azimuth': azimuth,
                'clearance_height': clearance,
                'pitch': pitch,
                'nMods': 12,
                'nRows': 1 # ili 2 ako želiš dva reda
            }

            scene = demo.makeScene(module=module, sceneDict=sceneDict)
            demo.genCumSky()
            oct_file = demo.makeOct(demo.getfilelist())

            # Analiza
            analysis = br.AnalysisObj(oct_file, demo.basename)
            frontscan, backscan = analysis.moduleAnalysis(scene)
            results = analysis.analysis(oct_file, demo.basename, frontscan, backscan)

            # Obrada rezultata
            results_dir = os.path.join(self.rad_path, 'results')
            if not os.path.exists(results_dir):
                raise FileNotFoundError(f"Folder {results_dir} ne postoji.")
                
            csv_files = [f for f in os.listdir(results_dir) if f.endswith('.csv')]
            if not csv_files:
                return self._fallback_pvlib(weather_df)
            
            df_res = pd.read_csv(os.path.join(results_dir, csv_files[0]))
            col_front = next((c for c in df_res.columns if 'Front' in c), None)
            col_back = next((c for c in df_res.columns if 'Back' in c), None)
            
            if not col_front or not col_back:
                return self._fallback_pvlib(weather_df)
            
            final_df = pd.DataFrame(index=weather_df.index)
            len_data = min(len(df_res), len(final_df))
            
            poa_front = np.asarray(df_res[col_front])
            poa_back = np.asarray(df_res[col_back])
            
            final_df['poa_front'] = pd.Series(poa_front[:len_data], index=final_df.index[:len_data])
            final_df['poa_back'] = pd.Series(poa_back[:len_data], index=final_df.index[:len_data])
            
            if len_data < len(final_df):
                final_df['poa_front'] = final_df['poa_front'].fillna(0)
                final_df['poa_back'] = final_df['poa_back'].fillna(0)
            
            log_success(f"Radiance uspješan! Front: {final_df['poa_front'].mean():.1f} W/m2")
            return final_df

        except Exception as e:
            log_error(f"Greška u Radiance: {e}")
            import traceback
            log_error(traceback.format_exc())
            return self._fallback_pvlib(weather_df)

    def _fallback_pvlib(self, df):
        log_warning("Koristim PVLib fallback.")
        from energy_simulator import calculate_poa_irradiance_simple
        poa_front = []
        tilt = float(self.config.get('tilt_angle', 45.0))
        azimuth = float(self.config.get('azimuth_angle', 180.0))
        lat = float(self.config.get('latitude', 42.9448))
        lon = float(self.config.get('longitude', 18.3236))
        for index, row in df.iterrows():
            poa_front.append(calculate_poa_irradiance_simple(row, tilt, azimuth, lat, lon))
        result_df = pd.DataFrame(index=df.index)
        result_df['poa_front'] = poa_front
        result_df['poa_back'] = [x * 0.15 for x in poa_front]
        return result_df