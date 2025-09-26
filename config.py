import os
import pathlib

def setup_qtwebengine_profile(profile_name):
    """Setup QtWebEngine profile for a specific viewer type."""
    BASE = pathlib.Path(__file__).resolve().parent
    PROFILE_DIR = BASE / ".qtwebengine" / profile_name
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    
    os.environ["QTWEBENGINE_PROFILE_STORAGE"] = str(PROFILE_DIR)
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu-shader-disk-cache"
    
    return PROFILE_DIR

DEFAULT_WINDOW_SIZE = (1200, 750)
DEFAULT_PLOT_SIZE = (600, 400)