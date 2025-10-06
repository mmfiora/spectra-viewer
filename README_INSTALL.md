# Spectra Viewer Installation

## Create virtual environment (recommended)

### Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Linux/Mac/WSL:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Alternative with conda:
```bash
conda env create -f environment.yml
conda activate spectra-viewer
```

## Run the application

### On Windows (from WSL with venv activated):
```bash
/mnt/c/Users/mfiora/Documents/Repositories/spectra-viewer/venv/bin/python launcher.py
```

### With venv activated:
```bash
# Launcher (select UV or Fluorescence):
python launcher.py

# UV viewer directly:
python main_UV.py

# Fluorescence viewer directly:
python main_fluo.py
```

## Verify installation
```bash
python check_versions.py
```
