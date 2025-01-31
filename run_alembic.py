"""
Helper script to run Alembic with the correct Python path.
"""
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from alembic.config import main

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        args = ['--help']
    main(argv=args)
