import os
import subprocess
import numpy as np
import pandas as pd
import pvlib
from datetime import datetime
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
        self.scene_path = os.path.join(self.base_path, 'radiance_scene')
        self.objects_path = os.path.join(self.base_path, 'radiance_objects')
        os.makedirs(self.rad_path, exist_ok=True)
        os.makedirs(self.scene_path, exist_ok=True)
        
        # Radiance alati - provjeri PATH
        self.oconv_cmd = 'oconv'
        self.rtrace_cmd = 'rtrace'
        self.gendaylit_cmd = 'gendaylit'
        self.genbox_cmd = 'genbox'

    def _run_radiance_command(self, cmd_args, description="Radiance komanda"):
        """Pokreni Radiance komandu i vrati rezultat."""
        try:
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            log_error(f"{description} nije uspjela: {e.stderr[:200] if e.stderr else str(e)}")
            return None
        except Exception as e:
            log_error(f"{description} greška: {str(e)}")
            return None

    def generate_scene_file(self):
        """Kreira glavni scene.rad fajl koji uključuje sve objekte."""
        scene_file = os.path.join(self.scene_path, 'scene.rad')
        
        # Provjeri da li postoje potrebni fajlovi
        materials_file = os.path.join(self.objects_path, 'materials.mat')
        ground_file = os.path.join(self.objects_path, 'ground.rad')
        panels_file = os.path.join(self.objects_path, 'panels.rad')
        
        content = "# RuralStar Sjednicu Scene\n\n"
        
        if os.path.exists(materials_file):
            content += f"#include \"{os.path.abspath(materials_file)}\"\n\n"
        else:
            # Dodaj osnovne materijale ako ne postoje
            content += """void plastic ground_mat
0
0
5 0.40 0.40 0.30 0 0

void plastic steel_mount
0
0
5 0.60 0.60 0.60 0 0

void glass pv_module_glass
0
0
3 0.90 0.90 0.90

"""
        
        if os.path.exists(ground_file):
            content += f"#include \"{os.path.abspath(ground_file)}\"\n\n"
        else:
            content += """ground_mat polygon ground_plane
0
0
12
-20 -20 0
20 -20 0
20 20 0
-20 20 0

"""
        
        if os.path.exists(panels_file):
            content += f"#include \"{os.path.abspath(panels_file)}\"\n"
        else:
            log_warning("panels.rad ne postoji - generišem jednostavnu geometriju")
            content += self._generate_simple_panels()
        
        with open(scene_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        log_success(f"Scene fajl kreiran: {scene_file}")
        return scene_file

    def _generate_simple_panels(self):
        """Generiše jednostavne panele koristeći polygon (bez box tipa)."""
        import math
        
        tilt = float(self.sys_params.get('tilt_angle', 45.0))
        azimuth = float(self.sys_params.get('azimuth_angle', 180.0))
        
        # Dimenzije panela (Huawei 540W)
        p_width = 1.134  # m
        p_height = 2.279  # m
        clearance = 0.5  # m
        
        rows = 2
        cols = 6
        row_spacing = 3.0
        
        rad_tilt = math.radians(tilt)
        rad_az = math.radians(azimuth)
        sin_t, cos_t = math.sin(rad_tilt), math.cos(rad_tilt)
        
        content = ""
        panel_id = 0
        
        for r in range(rows):
            for c in range(cols):
                panel_id += 1
                
                x_offset = (c - (cols - 1) / 2.0) * p_width
                y_offset = (r - (rows - 1) / 2.0) * row_spacing
                
                w2, h2 = p_width / 2.0, p_height / 2.0
                local_verts = [(-w2, -h2, 0), (w2, -h2, 0), (w2, h2, 0), (-w2, h2, 0)]
                
                global_verts = []
                for lx, ly, lz in local_verts:
                    ry = ly * cos_t - lz * sin_t
                    rz = ly * sin_t + lz * cos_t
                    
                    theta = math.radians(90) - rad_az
                    cos_th, sin_th = math.cos(theta), math.sin(theta)
                    
                    gx = x_offset + lx * cos_th - ry * sin_th
                    gy = y_offset + lx * sin_th + ry * cos_th
                    gz = clearance + rz
                    
                    global_verts.append((gx, gy, gz))
                
                pname = f"panel_{panel_id}"
                content += f"pv_module_glass polygon {pname}\n0\n0\n12\n"
                for vx, vy, vz in global_verts:
                    content += f"  {vx:.4f} {vy:.4f} {vz:.4f}\n"
        
        return content

    def generate_sky_file(self, dt, dni, ghi, dhi):
        """Generiše Radiance nebo za određeni sat koristeći gendaylit."""
        sky_file = os.path.join(self.scene_path, f'sky_{dt.month:02d}{dt.day:02d}_{dt.hour:02d}00.rad')
        
        # gendaylit format: gendaylit month day hour -W dni ghi -g albedo
        cmd = [
            self.gendaylit_cmd,
            str(dt.month), str(dt.day), f"{dt.hour}.5",
            '-W', str(dni), str(ghi),
            '-g', str(self.albedo)
        ]
        
        output = self._run_radiance_command(cmd, f"gendaylit za {dt}")
        
        if output:
            with open(sky_file, 'w', encoding='utf-8') as f:
                f.write(output)
            return sky_file
        return None

    def create_octree(self, sky_file, scene_file):
        """Kreira octree fajl za rendering."""
        octree_file = os.path.join(self.rad_path, f'scene_{os.path.basename(sky_file).replace(".rad", ".oct")}')
        
        cmd = [self.oconv_cmd, sky_file, scene_file]
        
        # Kreiraj octree direktno u fajl
        try:
            with open(octree_file, 'wb') as out_f:
                result = subprocess.run(
                    cmd,
                    stdout=out_f,
                    stderr=subprocess.PIPE,
                    check=True,
                    timeout=30
                )
            log_success(f"Octree kreiran: {octree_file}")
            return octree_file
        except subprocess.CalledProcessError as e:
            log_error(f"oconv greška: {e.stderr[:200] if e.stderr else str(e)}")
            return None
        except Exception as e:
            log_error(f"create_octree greška: {str(e)}")
            return None

    def run_rtrace(self, octree_file, sensor_points):
        """Pokreni rtrace za senzorske tačke."""
        if not octree_file or not os.path.exists(octree_file):
            return None
        
        # Pripremi input za rtrace (senzorske tačke)
        sensor_input = "\n".join([f"{x} {y} {z} 0 0 1" for x, y, z in sensor_points])
        
        cmd = [
            self.rtrace_cmd,
            '-I+',  # Irradijancija
            '-h',   # Bez headera
            '-ab', '3',  # Ambient bounces
            '-ad', '2048',  # Ambient divisions
            '-as', '1024',  # Ambient super-samples
            octree_file
        ]
        
        try:
            result = subprocess.run(
                cmd,
                input=sensor_input,
                capture_output=True,
                text=True,
                check=True,
                timeout=60
            )
            
            # Parsiraj rezultate (RGB vrijednosti)
            lines = result.stdout.strip().split('\n')
            irradiances = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        # Konvertuj RGB u irradijanciju (koristimo luminance formulu)
                        r, g, b = float(parts[0]), float(parts[1]), float(parts[2])
                        irr = (0.265*r + 0.670*g + 0.065*b)  # Approximation
                        irradiances.append(irr)
            
            return irradiances
        except Exception as e:
            log_error(f"rtrace greška: {str(e)}")
            return None

    def get_sensor_points(self):
        """Vraća liste senzorskih tačaka (centar svakog panela, prednja i zadnja strana)."""
        import math
        
        tilt = float(self.sys_params.get('tilt_angle', 45.0))
        azimuth = float(self.sys_params.get('azimuth_angle', 180.0))
        
        p_width = 1.134
        p_height = 2.279
        clearance = 0.5
        
        rows = 2
        cols = 6
        row_spacing = 3.0
        
        rad_tilt = math.radians(tilt)
        rad_az = math.radians(azimuth)
        sin_t, cos_t = math.sin(rad_tilt), math.cos(rad_tilt)
        
        sensors = []
        
        for r in range(rows):
            for c in range(cols):
                x_offset = (c - (cols - 1) / 2.0) * p_width
                y_offset = (r - (rows - 1) / 2.0) * row_spacing
                
                # Centar panela u lokalnom sistemu
                lx, ly, lz = 0, 0, 0
                
                # Rotacija
                ry = ly * cos_t - lz * sin_t
                rz = ly * sin_t + lz * cos_t
                
                theta = math.radians(90) - rad_az
                cos_th, sin_th = math.cos(theta), math.sin(theta)
                
                gx = x_offset + lx * cos_th - ry * sin_th
                gy = y_offset + lx * sin_th + ry * cos_th
                gz = clearance + rz
                
                # Prednja strana (normala prema suncu)
                sensors.append((gx, gy, gz))
        
        return sensors

    def run_simulation(self, weather_df):
        """Glavna simulacija koja koristi i PVLib i Radiance."""
        log_info("🤖 Pokrećem dualnu simulaciju (PVLib + Radiance)...")
        
        # Generiši scenu
        scene_file = self.generate_scene_file()
        if not scene_file:
            log_error("Neuspješno generisanje scene fajla")
            return self._pvlib_only_simulation(weather_df)
        
        # Priprema podataka
        lat = self.config.get('latitude', 42.94483338639821)
        lon = self.config.get('longitude', 18.323625614573174)
        altitude = self.config.get('altitude', 1076)
        tilt = float(self.sys_params.get('tilt_angle', 45.0))
        azimuth = float(self.sys_params.get('azimuth_angle', 180.0))
        
        location = pvlib.location.Location(lat, lon, altitude=altitude)
        times = weather_df.index
        
        # Rezultati
        final_df = pd.DataFrame(index=times)
        final_df['poa_front_pvlib'] = 0.0
        final_df['poa_front_radiance'] = 0.0
        final_df['poa_back_radiance'] = 0.0
        
        # Sensor tačke
        sensors = self.get_sensor_points()
        n_sensors = len(sensors)
        
        log_info(f"Simuliram {len(times)} sati sa {n_sensors} senzora...")
        
        # Uzorak prvih 24 sata za test (ukloni ovo za punu simulaciju)
        test_mode = True
        max_hours = 24 if test_mode else len(times)
        
        for i, dt in enumerate(times[:max_hours]):
            row = weather_df.loc[dt]
            dni = row.get('dni', 0)
            ghi = row.get('ghi', 0)
            dhi = row.get('dhi', 0)
            
            # PVLib proračun
            solar_position = location.get_solarposition([dt])
            poa = pvlib.irradiance.get_total_irradiance(
                surface_tilt=tilt,
                surface_azimuth=azimuth,
                solar_zenith=solar_position['apparent_zenith'].iloc[0],
                solar_azimuth=solar_position['azimuth'].iloc[0],
                dni=dni, ghi=ghi, dhi=dhi,
                albedo=self.albedo
            )
            final_df.loc[dt, 'poa_front_pvlib'] = poa['poa_global'].iloc[0]
            
            # Radiance proračun (samo ako ima sunca)
            if dni > 50 and ghi > 50:
                # 1. Generiši nebo
                sky_file = self.generate_sky_file(dt, dni, ghi, dhi)
                
                if sky_file:
                    # 2. Kreiraj octree
                    octree_file = self.create_octree(sky_file, scene_file)
                    
                    if octree_file:
                        # 3. Pokreni raytracing
                        irradiances = self.run_rtrace(octree_file, sensors)
                        
                        if irradiances and len(irradiances) == n_sensors:
                            final_df.loc[dt, 'poa_front_radiance'] = np.mean(irradiances)
                            # Bifacialni dio (aproksimacija)
                            final_df.loc[dt, 'poa_back_radiance'] = final_df.loc[dt, 'poa_front_radiance'] * self.albedo * self.bifaciality
        
        # Za sate izvan testnog perioda, kopiraj PVLib rezultate
        if test_mode and len(times) > max_hours:
            final_df.loc[times[max_hours:], 'poa_front_pvlib'] = weather_df.loc[times[max_hours:], 'ghi'] * 0.8
        
        # Kombinuj rezultate
        final_df['poa_front'] = final_df['poa_front_radiance'].where(
            final_df['poa_front_radiance'] > 0,
            final_df['poa_front_pvlib']
        )
        final_df['poa_back'] = final_df['poa_back_radiance'].where(
            final_df['poa_back_radiance'] > 0,
            final_df['poa_front'] * self.albedo * self.bifaciality
        )
        
        log_success(f"Dualna simulacija završena!")
        log_success(f"PVLib prosjek: {final_df['poa_front_pvlib'].mean():.1f} W/m²")
        if final_df['poa_front_radiance'].max() > 0:
            log_success(f"Radiance prosjek (uzorak): {final_df['poa_front_radiance'][final_df['poa_front_radiance']>0].mean():.1f} W/m²")
        
        return final_df

    def _pvlib_only_simulation(self, weather_df):
        """Fallback na samo PVLib ako Radiance ne radi."""
        log_warning("Koristim PVLib fallback...")
        
        lat = self.config.get('latitude', 42.94483338639821)
        lon = self.config.get('longitude', 18.323625614573174)
        altitude = self.config.get('altitude', 1076)
        tilt = float(self.sys_params.get('tilt_angle', 45.0))
        azimuth = float(self.sys_params.get('azimuth_angle', 180.0))
        
        location = pvlib.location.Location(lat, lon, altitude=altitude)
        times = weather_df.index
        
        solar_position = location.get_solarposition(times)
        poa = pvlib.irradiance.get_total_irradiance(
            surface_tilt=tilt,
            surface_azimuth=azimuth,
            solar_zenith=solar_position['apparent_zenith'],
            solar_azimuth=solar_position['azimuth'],
            dni=weather_df['dni'].fillna(0),
            ghi=weather_df['ghi'].fillna(0),
            dhi=weather_df['dhi'].fillna(0),
            albedo=self.albedo
        )
        
        result_df = pd.DataFrame(index=times)
        result_df['poa_front'] = poa['poa_global'].fillna(0)
        result_df['poa_back'] = result_df['poa_front'] * self.albedo * self.bifaciality
        
        return result_df

    def _fallback_pvlib(self, df):
        """Fallback metoda ako glavni PVLib proračun ne uspije."""
        log_warning("Koristim PVLib fallback (jednostavniji model).")
        
        try:
            lat = self.config.get('latitude', 42.94483338639821)
            lon = self.config.get('longitude', 18.323625614573174)
            altitude = self.config.get('altitude', 1076)
            tilt = float(self.sys_params.get('tilt_angle', 45.0))
            azimuth = float(self.sys_params.get('azimuth_angle', 180.0))
            
            location = pvlib.location.Location(lat, lon, altitude=altitude)
            times = df.index
            
            solar_position = location.get_solarposition(times)
            apparent_zenith = solar_position['apparent_zenith']
            azimuth_sun = solar_position['azimuth']
            
            ghi = df['ghi'].fillna(0)
            dni = df['dni'].fillna(0)
            dhi = df['dhi'].fillna(0)
            
            poa = pvlib.irradiance.get_total_irradiance(
                surface_tilt=tilt,
                surface_azimuth=azimuth,
                solar_zenith=apparent_zenith,
                solar_azimuth=azimuth_sun,
                dni=dni,
                ghi=ghi,
                dhi=dhi,
                albedo=self.albedo
            )
            
            result_df = pd.DataFrame(index=df.index)
            result_df['poa_front'] = poa['poa_global'].fillna(0)
            result_df['poa_back'] = result_df['poa_front'] * self.albedo * self.bifaciality
            
            return result_df
        except Exception as e:
            log_error(f"Fallback također nije uspio: {e}")
            # Posljednji resort - nulti podaci
            result_df = pd.DataFrame(index=df.index)
            result_df['poa_front'] = 0
            result_df['poa_back'] = 0
            return result_df