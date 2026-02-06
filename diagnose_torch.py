import sys
print(f"Python: {sys.version}")
try:
    import torch
    print(f"Torch version: {torch.__version__}")
    print("Torch imported successfully!")
except ImportError as e:
    print(f"ImportError: {e}")
except OSError as e:
    print(f"OSError: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
