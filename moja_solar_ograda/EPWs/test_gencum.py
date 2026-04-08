import os
from bifacial_radiance import RadianceObj

# Dodaj putanju do Radiance bin (ako već nije u PATH)
os.environ["PATH"] = r"E:\Radiance_build\bin" + os.pathsep + os.environ.get("PATH", "")

demo = RadianceObj("test", path="./test_cum")
demo.setGround(0.4)
demo.makeModule(name='m', x=1.134, y=2.2, bifi=0.75)
demo.readWeatherFile(r"SRB_Podgorica.134620_IWEC.epw", coerce_year=2023)
demo.genCumSky()
print("genCumSky uspješno pozvan!")