"""
Entry point for PyInstaller packaging.
This file provides an absolute import entry point since PyInstaller 
cannot handle relative imports in `src.main` when run as `python -m src.main`.
"""
from src.main import main

if __name__ == "__main__":
    main()
