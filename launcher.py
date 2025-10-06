import subprocess

# Ejecutar las dos apps en paralelo
subprocess.Popen(["python", "main_UV.py"])
subprocess.Popen(["python", "main_fluo.py"])
