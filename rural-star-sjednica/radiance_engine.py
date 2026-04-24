import os
import numpy as np
import pandas as pd
import bifacial_radiance as br
import pvlib
# POPRAVKA 4: Dodan log_success u import
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
        log_info("Pokrećem bifacial Radiance simulaciju (Optimized)...")
        
        try:
            demo = br.RadianceObj(name='ruralstar_opt', path=self.rad_path)
            
            # POPRAVKA 1: setGround koristi groundDict ili samo albedo float (ovisno o verziji)
            # Najsigurniji način za novije verzije je groundDict
            try:
                demo.setGround(groundDict={'material': 'groundplane', 'albedo': self.albedo})
            except TypeError:
                # Fallback za starije verzije koje primaju samo float
                demo.setGround(self.albedo)
            
            epw_file = self._create_temp_epw_fast(weather_df)
            demo.readWeatherFile(weatherFile=epw_file)
            
            panel_specs = self.equipment['panels']['Huawei_IPV540-M1A']
            width = float(panel_specs['dimensions_mm'][1]) / 1000.0
            height = float(panel_specs['dimensions_mm'][0]) / 1000.0
            
            # Bifaciality factor kao integer (0-100) za makeModule
            bifi_val = int(self.bifaciality * 100)
            
            module = demo.makeModule(
                name='Huawei_540W_Bi',
                x=width,
                y=height,
                bifi=bifi_val,
                numpanels=1
            )
            
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
                'nRows': 1
            }
            
            scene = demo.makeScene(module=module, sceneDict=sceneDict)
            demo.genCumSky()
            oct_file = demo.makeOct(demo.getfilelist())
            
            analysis = br.AnalysisObj(oct_file, demo.basename)
            frontscan, backscan = analysis.moduleAnalysis(scene)
            
            # POPRAVKA 3: Uklonjen parametar 'parallel' koji ne postoji u ovoj verziji
            results = analysis.analysis(oct_file, demo.basename, frontscan, backscan)
            
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
            
            poa_front_array = np.asarray(df_res[col_front])
            poa_back_array = np.asarray(df_res[col_back])
            
            final_df['poa_front'] = pd.Series(poa_front_array[:len_data], index=final_df.index[:len_data])
            final_df['poa_back'] = pd.Series(poa_back_array[:len_data], index=final_df.index[:len_data])
            
            if len_data < len(final_df):
                final_df['poa_front'] = final_df['poa_front'].fillna(0)
                final_df['poa_back'] = final_df['poa_back'].fillna(0)
            
            log_success(f"Radiance uspjedan! Prosijek Front: {final_df['poa_front'].mean():.1f} W/m2")
            return final_df
            
        except Exception as e:
            log_error(f"Greška u Radiance: {e}")
            return self._fallback_pvlib(weather_df)

    def _create_temp_epw_fast(self, df):
        """Vektorizovana verzija kreiranja EPW-a."""
        epw_path = os.path.join(self.rad_path, 'temp_weather_fast.epw')
        lat = 42.94483338639821
        lon = 18.323625614573174
        
        header = (
            f"LOCATION,Bileca,,BIH,TMY,{lat:.4f},{lon:.4f},1,1076\n"
            "DESIGN CONDITIONS,0\nTYPICAL/EXTREME PERIODS,0\nGROUND TEMPERATURES,0\n"
            "HOLIDAYS/DAYLIGHT SAVING,No,0,0,0\nCOMMENTS 1,RuralStar Fast Sim\nCOMMENTS 2,\n"
            "DATA PERIODS,1,1,Data,Sunday, 1/ 1,12/31\n"
        )
        
        # Vektorizacija za brzinu
        years = df.index.year.astype(str)
        months = df.index.month.astype(str).str.zfill(2)
        days = df.index.day.astype(str).str.zfill(2)
        hours = (df.index.hour + 1).astype(str).str.zfill(2)
        
        dni = np.maximum(0, df['dni'].fillna(0)).astype(int).astype(str)
        dhi = np.maximum(0, df['dhi'].fillna(0)).astype(int).astype(str)
        ghi = np.maximum(0, df['ghi'].fillna(0)).astype(int).astype(str)
        
        static_part = ",60,1,9999,9999,9999,9999,9999,9999,9999,9999,9999,9999,9999,9999,9999,9999,9999,9999,9999,9999,9999,9999,9999,"
        
        lines = years + "," + months + "," + days + "," + hours + static_part + dni + "," + dhi + "," + ghi
        lines_str = "\n".join(lines)
        
        with open(epw_path, 'w', encoding='utf-8') as f:
            f.write(header + lines_str)
            
        return epw_path

    def _fallback_pvlib(self, df):
        log_warning("Koristim PVLib fallback.")
        from energy_simulator import calculate_poa_irradiance_simple
        
        poa_front = []
        tilt = float(self.config.get('tilt_angle', 45.0))
        azimuth = float(self.config.get('azimuth_angle', 180.0))
        
        # POPRAVKA 2: Funkcija calculate_poa_irradiance_simple sada interno rješava deltat
        # Ovdje samo iteriramo
        for index, row in df.iterrows():
            poa = calculate_poa_irradiance_simple(row, tilt, azimuth)
            poa_front.append(poa)
        
        result_df = pd.DataFrame(index=df.index)
        result_df['poa_front'] = poa_front
        result_df['poa_back'] = [x * 0.15 for x in poa_front]
        return result_df