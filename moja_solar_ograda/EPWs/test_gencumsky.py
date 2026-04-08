import os
from bifacial_radiance import RadianceObj, AnalysisObj

EPW_FILE = r"E:\Radiance_build\moja_solar_ograda\EPWs\SRB_Podgorica.134620_IWEC.epw"

demo = RadianceObj("test_gencum", path="./test_gencum")
demo.setGround(0.4)
module = demo.makeModule(name='panel', x=1.134, y=2.2, bifi=0.75)
demo.readWeatherFile(EPW_FILE, coerce_year=2023)
demo.genCumSky()   # bez argumenata

scene_dict = {'tilt': 60, 'azimuth': 135, 'nMods': 4, 'nRows': 1, 'clearance_height': 0.5, 'pitch': 10}
scene = demo.makeScene(module=module, sceneDict=scene_dict)
oct_file = demo.makeOct(demo.getfilelist())

analysis = AnalysisObj(oct_file, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(scene)
analysis.analysis(oct_file, demo.basename, frontscan, backscan)

print("CSV fajlovi kreirani u results folderu.")