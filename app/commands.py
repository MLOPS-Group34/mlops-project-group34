#!/usr/bin/env python
"""
Quick reference script - Shows all commands to run the Streamlit dashboard.
Run: python commands.py
"""

import sys
from pathlib import Path


def print_banner():
    """Print welcome banner."""
    banner = """
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║    🔥 FOREST FIRE DETECTION - STREAMLIT DASHBOARD 🔥          ║
    ║                                                                ║
    ║           Quick Command Reference Guide                       ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_section(title):
    """Print a section header."""
    print(f"\n{'═' * 70}")
    print(f"  {title}")
    print(f"{'═' * 70}\n")


def print_command(cmd, description, details=""):
    """Print a command with description."""
    print(f"📌 {description}")
    print(f"   $ {cmd}")
    if details:
        print(f"   💡 {details}")
    print()


def main():
    """Display command reference."""
    
    print_banner()
    
    # Setup Commands
    print_section("1️⃣  SETUP & INSTALLATION")
    print_command(
        "uv sync",
        "Install all project dependencies",
        "Only needed first time or after pyproject.toml changes"
    )
    print_command(
        "python verify_setup.py",
        "Verify the setup is correct",
        "Checks all files, config, and dependencies"
    )
    print_command(
        "python test_imports.py",
        "Test if all Python imports work",
        "Useful for debugging dependency issues"
    )
    
    # Running Commands
    print_section("2️⃣  RUNNING THE DASHBOARD")
    print_command(
        "streamlit run app/streamlit_app.py",
        "Start the dashboard (MAIN COMMAND)",
        "Opens browser at http://localhost:8501"
    )
    print_command(
        "python run_dashboard.py",
        "Alternative launcher script",
        "Does the same as the streamlit command above"
    )
    print_command(
        "streamlit run app/streamlit_app.py --logger.level=debug",
        "Run dashboard with debug logging",
        "Useful for troubleshooting"
    )
    print_command(
        "streamlit run app/streamlit_app.py --server.port 8502",
        "Run on different port (if 8501 is busy)",
        "Change 8502 to any available port"
    )
    
    # Pipeline Commands
    print_section("3️⃣  GENERATING PREDICTIONS (CLI)")
    print_command(
        "python main.py --pipeline visualize",
        "Generate prediction grids via command line",
        "Same as clicking 'Generate' in dashboard"
    )
    print_command(
        "python main.py --pipeline all",
        "Run full pipeline: train, evaluate, visualize",
        "Requires training data and sufficient compute"
    )
    print_command(
        "python main.py --pipeline visualize --config configs/config.yaml",
        "Generate with specific config file",
        "Default is configs/config.yaml"
    )
    
    # Utility Commands
    print_section("4️⃣  UTILITIES & HELPERS")
    print_command(
        "python setup_dashboard.py",
        "Interactive setup wizard",
        "Guides you through installation step-by-step"
    )
    print_command(
        "streamlit cache clear",
        "Clear Streamlit's internal cache",
        "Try this if having stale data issues"
    )
    print_command(
        "ls reports/figures/",
        "List generated prediction grids",
        "Check what grids are available locally"
    )
    
    # Debugging Commands
    print_section("5️⃣  DEBUGGING & TROUBLESHOOTING")
    print_command(
        "python -c \"import streamlit; print(streamlit.__version__)\"",
        "Check installed Streamlit version",
        "Verify correct version is installed"
    )
    print_command(
        "python --version",
        "Check Python version",
        "Should be 3.11 or higher"
    )
    print_command(
        "uv pip list",
        "List all installed packages with versions",
        "Verify all dependencies are present"
    )
    print_command(
        "pip install --upgrade streamlit",
        "Upgrade Streamlit to latest version",
        "Use if experiencing bugs"
    )
    
    # Information Section
    print_section("📖 KEY INFORMATION")
    
    print("""
📍 DASHBOARD URL
   http://localhost:8501

📁 KEY FILES
   - Main app:           app/streamlit_app.py
   - Configuration:      configs/config.yaml
   - Streamlit config:   .streamlit/config.toml
   - Generated grids:    reports/figures/predictions_grid_*.png

📚 DOCUMENTATION
   - Quick start:        STREAMLIT_QUICKSTART.md
   - Full guide:         DASHBOARD_SETUP.md
   - App docs:           app/README.md
   - Setup info:         SETUP_COMPLETE.md

⚙️  DEFAULT SETTINGS
   - Port:               8501
   - Config:             configs/config.yaml
   - Reports dir:        reports/figures/
   - Theme:              Fire red (🔥)

🔧 CONFIGURATION
   Edit .streamlit/config.toml to customize:
   - Theme colors
   - Server port
   - Layout size
   - Logging level
""")
    
    # Quick Start
    print_section("🚀 QUICK START (3 COMMANDS)")
    
    print("1. Install dependencies:")
    print("   $ uv sync\n")
    
    print("2. Start dashboard:")
    print("   $ streamlit run app/streamlit_app.py\n")
    
    print("3. Browser opens automatically at:")
    print("   http://localhost:8501\n")
    
    # Common Issues
    print_section("⚠️  COMMON ISSUES & SOLUTIONS")
    
    issues = [
        (
            "Port 8501 already in use",
            "streamlit run app/streamlit_app.py --server.port 8502"
        ),
        (
            "ImportError: No module named 'streamlit'",
            "uv sync"
        ),
        (
            "No prediction grids found",
            "Click 'Generate New Samples' in dashboard"
        ),
        (
            "Model not found error",
            "Check configs/config.yaml for correct model path"
        ),
        (
            "Generation is slow",
            "Normal: YOLOv8n takes 2-10 min for 50 test images"
        ),
    ]
    
    for issue, solution in issues:
        print(f"❌ {issue}")
        print(f"   ✅ Solution: {solution}\n")
    
    # Tips
    print_section("💡 PRO TIPS")
    
    tips = [
        "Press Ctrl+C in terminal to stop the dashboard",
        "Dashboard auto-reloads on file changes",
        "Use --logger.level=debug for verbose output",
        "Session state persists during your session",
        "Click 'Generate New Samples' to update predictions",
        "Use keyboard shortcuts: R to rerun, C to clear cache",
        "Check console (terminal) for detailed error messages",
        "Reports are saved as PNG files for easy sharing",
    ]
    
    for i, tip in enumerate(tips, 1):
        print(f"{i}. {tip}")
    
    # Footer
    print(f"\n{'═' * 70}")
    print("  Ready to go! Start with:")
    print("  $ streamlit run app/streamlit_app.py")
    print(f"{'═' * 70}\n")
    
    print("Happy analyzing! 🔥📊\n")


if __name__ == "__main__":
    main()
