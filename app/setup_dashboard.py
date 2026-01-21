"""
Installation and setup helper for the Streamlit dashboard.
This script helps install dependencies and configure the dashboard.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and report the result."""
    print(f"\n{'=' * 60}")
    print(f"📦 {description}")
    print(f"{'=' * 60}")
    print(f"Running: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            return True
        else:
            print(f"❌ {description} failed with exit code {result.returncode}")
            return False
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False


def main():
    """Main setup function."""

    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "   🔥 Forest Fire Detection - Streamlit Dashboard Setup 🔥".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")

    project_root = Path(__file__).parent.parent

    # Step 1: Sync dependencies
    print("\n\n📋 STEP 1: Installing Dependencies")
    print("-" * 60)
    print("This will install all required Python packages.")
    print("It may take several minutes...\n")

    response = input("Continue with dependency installation? (y/n): ").strip().lower()
    if response != "y":
        print("Skipping dependency installation.")
    else:
        if not run_command([sys.executable, "-m", "pip", "install", "uv"], "Installing uv"):
            print("⚠️  uv installation failed. Trying with pip...")

        if not run_command(["uv", "sync"], "Installing project dependencies with uv"):
            print("❌ Dependency installation failed.")
            print("Please run manually: uv sync")
            return 1

    # Step 2: Verify setup
    print("\n\n🔍 STEP 2: Verifying Setup")
    print("-" * 60)

    verify_script = project_root / "verify_setup.py"
    if verify_script.exists():
        if not run_command([sys.executable, str(verify_script)], "Running verification"):
            return 1
    else:
        print("⚠️  Verification script not found")

    # Step 3: Information
    print("\n\n✅ STEP 3: Setup Complete!")
    print("=" * 60)
    print(f"Project location: {project_root}")
    print("=" * 60)

    print("\n📚 Quick Start:")
    print("\n1️⃣  Start the dashboard:")
    print("   streamlit run app/streamlit_app.py")

    print("\n2️⃣  Dashboard will open at:")
    print("   http://localhost:8501")

    print("\n3️⃣  In the dashboard:")
    print("   - Go to '⚙️ Generate New Samples' tab")
    print("   - Click the button to run inference")
    print("   - View results in '📸 Prediction Gallery' tab")

    print("\n📖 Documentation:")
    print(f"   - Quick Start: {project_root / 'STREAMLIT_QUICKSTART.md'}")
    print(f"   - Dashboard Guide: {project_root / 'app' / 'README.md'}")
    print(f"   - Config File: {project_root / 'configs' / 'config.yaml'}")

    print("\n💡 Useful Commands:")
    print("   streamlit run app/streamlit_app.py           # Run dashboard")
    print("   python main.py --pipeline visualize          # Generate grids via CLI")
    print("   python verify_setup.py                       # Verify setup")
    print("   streamlit run app/streamlit_app.py --logger.level=debug  # Debug mode")

    print("\n" + "=" * 60)
    print("🎉 Ready to use! Start with:")
    print("   streamlit run app/streamlit_app.py")
    print("=" * 60 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
