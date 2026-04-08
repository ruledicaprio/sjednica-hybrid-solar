import os
from bifacial_radiance import RadianceObj

simulation_name = "moja_solar_ograda"
test_folder = os.path.abspath(rf".\{simulation_name}")
os.makedirs(test_folder, exist_ok=True)

demo = RadianceObj(simulation_name, path=test_folder)
demo.setGround(0.4)

myModule = demo.makeModule(name='TOPBiHiKu6', x=1.134, y=2.2)

scene = {
    'tilt': 60,
    'azimuth': 135,
    'nMods': 2,
    'nRows': 1,
    'clearance_height': 0.5,
    'pitch': 10.0
}
print("Scene dictionary:", scene)  # Dodajmo provjeru
demo.makeScene(module=myModule, sceneDict=scene)

oct_file = demo.makeOct(demo.getfilelist())
print(f"✅ .oct fajl uspješno kreiran: {oct_file}")