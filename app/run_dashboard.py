"""
Helper script to launch the Streamlit app.
Can be run from anywhere in the project.
"""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    app_path = project_root / "app" / "streamlit_app.py"

    if not app_path.exists():
        print(f"Error: Streamlit app not found at {app_path}")
        sys.exit(1)

    print(f"Starting Streamlit app from {app_path}")
    print("Dashboard will open at http://localhost:8501")

    # Run streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])
