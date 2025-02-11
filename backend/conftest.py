import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Add FreeCAD paths
CONDA_PREFIX = os.getenv('CONDA_PREFIX')
if CONDA_PREFIX:
    freecad_lib = Path(CONDA_PREFIX) / 'lib'
    if freecad_lib.exists():
        sys.path.append(str(freecad_lib))
        os.environ['FREECAD_LIB'] = str(freecad_lib / 'FreeCAD.so')

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eurotempl.settings')

# Initialize Django
import django
django.setup()