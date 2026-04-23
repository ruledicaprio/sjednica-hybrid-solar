#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AUTOMATSKI POKRETAČ SIMULACIJE
Preskače interaktivni unos i pokreće ruralstar_hybrid_final.py sa fiksnim parametrima.
"""
import sys
import os

# Dodajemo trenutni direktorij u path da bismo mogli importovati glavni script
# Ali pošto je glavni script dizajniran da se izvršava direktno (if __name__ == "__main__"),
# najbolje je da ga modifikujemo da prihvati argumente ili da ga pokrenemo kao subprocess.
# Ovdje ćemo koristiti trik: postaviti sys.argv da simulira unos.

if __name__ == "__main__":
    # Fiksni parametri za Bileću
    LAT = "42.9448"
    LON = "18.3236"
    USE_TMY = "d"  # Da, koristi TMY
    
    # Priprema inputa za simulaciju
    # Glavna skripta traži: lat, lon, use_tmy, (godine ako nije TMY)
    # Moramo "pretvariti" da su ovo uneseni podaci. 
    # Najsigurniji način je modifikacija source koda na letu ili korištenje subprocess sa stdin.
    
    import subprocess
    
    script_path = "ruralstar_hybrid_final.py"
    
    if not os.path.exists(script_path):
        print(f"❌ Greška: {script_path} nije pronađen!")
        sys.exit(1)

    print("🚀 Pokrećem automatsku simulaciju za Bileću...")
    print(f"   📍 GPS: {LAT}, {LON}")
    print(f"   📅 Podaci: PVGIS TMY")
    
    # Kreiramo input string za subprocess
    input_data = f"{LAT}\n{LON}\n{USE_TMY}\n"
    
    try:
        # Pokrećemo skriptu i prosleđujemo inpute
        result = subprocess.run(
            [sys.executable, script_path],
            input=input_data,
            text=True,
            capture_output=False, # Prikazuj output u realnom vremenu
            check=True
        )
        print("\n✅ Simulacija uspješno završena!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Simulacija je prekinuta sa greškom: {e}")
        print("Provjeri da li su Radiance alati (gendaymtx, oconv, rtrace) u PATH-u.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"\n❌ Python skripta {script_path} nije pronađena.")
        sys.exit(1)

    print("\n📊 Sada generišem detaljan PDF izvještaj...")
    # Pokrećemo generator izvještaja
    os.system(f"{sys.executable} generate_report.py")
