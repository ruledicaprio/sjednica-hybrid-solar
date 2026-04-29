import os
import subprocess
import glob
from logger import log_info, log_success, log_error, log_warning

def generate_false_color_images():
    """Generiše False Color slike iz Radiance rezultata."""
    log_info("🎨 Generisanje False Color slika...")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    rad_path = os.path.join(base_path, 'radiance_results')
    images_path = os.path.join(rad_path, 'images')
    materials_path = os.path.join(rad_path, 'materials')
    objects_path = os.path.join(rad_path, 'objects')
    
    os.makedirs(images_path, exist_ok=True)
    os.makedirs(materials_path, exist_ok=True)
    
    # 1. OSIGURAJ MATERIJALE (Kreiraj ground.rad ako ne postoji)
    ground_rad_file = os.path.join(materials_path, 'ground.rad')
    if not os.path.exists(ground_rad_file):
        log_info("Kreiram missing 'ground.rad' materijal...")
        with open(ground_rad_file, 'w') as f:
            f.write("# Ground material for Radiance\n")
            f.write("void plastic ground_mat\n")
            f.write("0\n0\n5 0.4 0.4 0.4 0.0 0.0\n") # Albedo 0.4
            f.write("\nground_mat polygon ground_plane\n")
            f.write("0\n0\n12 -50 -50 0 50 -50 0 50 50 0 -50 50 0\n")
        log_success("ground.rad kreiran.")

    # 2. Pronađi Octree
    oct_files = glob.glob(os.path.join(rad_path, '*.oct'))
    if not oct_files:
        log_error("Nema .oct fajla. Pokrenite prvo run_simulation.py")
        return
    
    oct_file = oct_files[0]
    log_info(f"Koristim Octree: {os.path.basename(oct_file)}")
    
    # 3. Definicija Pogleda (View)
    # Kamera je na JUGU (negativni Y), gleda prema SJEVERU (+Y).
    # Paneli su na Y=0 do Y=~5. Kontejner je IZA (Sjevernije, npr. Y=6+).
    # Dakle, kamera mora biti na Y = -10 da vidi sve.
    # -vp x y z : Pozicija kamere
    # -vd x y z : Smjer gledanja (0 1 0 = Sjever)
    view_cmd = "-vtv -vp 0 -15 2 -vd 0 1 0 -vu 0 0 1"
    
    hdr_file = os.path.join(images_path, 'view_solar_radiance.hdr')
    fc_file = os.path.join(images_path, 'falsecolor_solar_radiance.png')
    
    # 4. Renderovanje (rpict)
    # Napomena: Pokrećemo iz rad_path da bi relativne putanje u .oct fajlu radile
    cmd_rpict = f"rpict {view_cmd} -ab 2 -ad 1000 -as 500 -ar 300 -aa 0.1 {os.path.basename(oct_file)}"
    
    try:
        log_info("Renderovanje HDR slike (ovo može potrajati 1-2 min)...")
        with open(hdr_file, 'w') as out_f:
            # Pokrećemo subprocess unutar rad_path direktorija
            result = subprocess.run(
                cmd_rpict, 
                shell=True, 
                cwd=rad_path, # KLJUČNO: Radi iz foldera gdje je .oct i podfolderi
                stdout=out_f, 
                stderr=subprocess.PIPE, 
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(result.stderr)
                
        log_success(f"HDR slika kreirana: {hdr_file}")
        
        # 5. False Color Konverzija
        log_info("Generisanje False Color mape...")
        cmd_fc = f"falsecolor -ip {hdr_file} -o {fc_file} -cl -cb -log"
        subprocess.run(cmd_fc, shell=True, check=True)
        
        log_success(f"✅ False Color slika uspješno kreirana: {fc_file}")
        
    except Exception as e:
        log_error(f"Greška pri renderovanju: {e}")
        log_error("Provjerite da li su svi .rad fajlovi (paneli, kontejner) prisutni u folderima 'objects' i 'materials'.")

if __name__ == "__main__":
    generate_false_color_images()