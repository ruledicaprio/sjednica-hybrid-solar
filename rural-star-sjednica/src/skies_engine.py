import os
import subprocess
from typing import Dict, Any, cast
import pandas as pd
from datetime import datetime # Dodajemo za type hinting
from logger import log_info, log_success, log_error

def generate_sky(row: pd.Series, scene_path: str) -> str:
    """
    Generiše Radiance .sky fajl. 
    Fix: Eksplicitno pretvaramo row.name u datetime/timestamp tip.
    """
    # Pylance fix: Cast-ujemo row.name u datetime da bi prepoznao month, day, hour...
    dt = cast(datetime, row.name)
    
    if dt is None:
        log_error("Red podataka nema validan vremenski pečat.")
        return ""

    month = dt.month
    day = dt.day
    hour = dt.hour + dt.minute / 60.0
    
    # Sigurno izvlačenje zračenja (ako Pylance pravi problem oko Unknown tipa)
    dni = float(row.get('dni', 0))
    dhi = float(row.get('dhi', 0))
    
    # strftime sada radi jer Pylance zna da je dt tipa datetime
    sky_filename = f"sky_{dt.strftime('%m%d_%H%M')}.rad"
    sky_path = os.path.join(scene_path, sky_filename)
    
    # Gendaylit komanda
    command = [
        "gendaylit", 
        str(month), str(day), f"{hour:.2f}",
        "-W", str(dni), str(dhi),
        "-g", "0.2"
    ]
    
    try:
        # Kod produkcionih sistema, provjeravamo da li gensky postoji
        sky_content = subprocess.check_output(command, stderr=subprocess.STDOUT).decode('utf-8')
        
        full_content = (
            f"# Sky for {dt}\n"
            f"{sky_content}"
            "\nskyfunc glow ground_glow\n0\n0\n4 1 1 1 0\n"
            "\nground_glow source ground\n0\n0\n4 0 0 -1 180\n"
        )
        
        with open(sky_path, "w") as f:
            f.write(full_content)
            
        return sky_path
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        log_error(f"Gendaylit nije dostupan ili je greška: {e}")
        return ""

def prepare_sky_simulation(weather_df: pd.DataFrame, config: Dict[str, Any]):
    """
    Priprema simulaciju neba.
    """
    log_info("☁️  Pokretanje Skies Engine-a...")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    scene_path = os.path.join(base_path, 'radiance_scene', 'skies')
    os.makedirs(scene_path, exist_ok=True)
    
    # Osiguravamo da su nazivi kolona ispravni (lowercase)
    weather_df.columns = [c.lower() for c in weather_df.columns]
    
    # Filtriramo sate sa suncem
    daylight = weather_df[weather_df['dni'] > 0]
    
    if daylight.empty:
        log_error("Nema sunčanih sati u učitanim podacima!")
        return scene_path

    # Uzimamo prvi red za test
    test_row = daylight.iloc[0]
    sky_file = generate_sky(test_row, scene_path)
    
    if sky_file:
        log_success(f"Nebo generisano: {os.path.basename(sky_file)}")
        
    return scene_path

def read_epw_data(file_path):
    """Učitava EPW fajl i priprema podatke za simulaciju."""
    # Čitamo zaglavlje za visinu
    with open(file_path, 'r') as f:
        first_line = f.readline()
        altitude = float(first_line.split(',')[-1].strip())

    # Čitamo podatke (preskačemo 8 linija zaglavlja)
    df_raw = pd.read_csv(file_path, skiprows=8, header=None)
    
    df = pd.DataFrame()
    df['month'] = df_raw[1]
    df['day'] = df_raw[2]
    df['hour'] = df_raw[3] - 1  # Korekcija za Radiance (0-23)
    df['dni'] = df_raw[14]
    df['dhi'] = df_raw[15]
    df['temp'] = df_raw[6]
    
    # Vremenska osa
    df['datetime'] = pd.to_datetime({
        'year': 2024, 'month': df['month'], 'day': df['day'], 'hour': df['hour']
    })
    df.set_index('datetime', inplace=True)
    
    return df, altitude