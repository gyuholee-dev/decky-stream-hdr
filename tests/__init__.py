import os
import sys

# Make the backend modules importable without the Decky loader.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "py_modules"))
