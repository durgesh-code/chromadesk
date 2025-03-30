print("DEBUG: main.py top-level execution starting...")
#!/usr/bin/env python3
# chromadesk/main.py
"""
ChromaDesk - Daily Bing/Custom Wallpaper Changer for GNOME

This is the main entry point for the ChromaDesk application.
It handles both GUI and command-line modes.
"""

import sys
import argparse
import logging
import os
from pathlib import Path

# Configure logging
log_format = '%(asctime)s - %(levelname)s - %(message)s'
log_file_path = Path.home() / ".config" / "chromadesk" / "chromadesk.log"
try:
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )
except Exception as e:
    # Fallback basic logging if file handler fails
    logging.basicConfig(level=logging.WARNING, format=log_format)
    logging.critical(f"Failed to configure file logging: {e}")

logger = logging.getLogger(__name__)

# Suppress Mesa Intel warning
os.environ["MESA_DEBUG"] = "silent"

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="ChromaDesk - Daily Wallpaper Changer")
    
    # Add subparsers for different modes
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # GUI mode (default)
    gui_parser = subparsers.add_parser("gui", help="Launch the GUI application (default)")
    
    # Update mode
    update_parser = subparsers.add_parser("update", help="Update wallpaper without launching GUI")
    update_parser.add_argument("--notify", action="store_true", help="Show desktop notification after update")
    
    # Version info
    parser.add_argument("--version", action="store_true", help="Show version information")
    
    # If no arguments are provided, default to GUI mode
    if len(sys.argv) == 1:
        sys.argv.append("gui")
        
    return parser.parse_args()

def main():
    """Main entry point for ChromaDesk."""
    args = parse_args()
    
    # Show version info if requested
    if args.version:
        from importlib.metadata import version
        try:
            ver = version("chromadesk")
            print(f"ChromaDesk version {ver}")
        except:
            print("ChromaDesk (version unknown)")
        return 0
    
    # Handle different commands
    if args.command == "update":
        logger.info("Running in update mode")
        from chromadesk.headless import run_daily_update
        success = run_daily_update()
        return 0 if success else 1
    else:  # gui mode
        print("DEBUG: Entering GUI mode...")
        logger.info("Starting GUI application")
        try:
            print("DEBUG: Attempting to import PySide6.QtWidgets...")
            from PySide6.QtWidgets import QApplication
            print("DEBUG: PySide6.QtWidgets imported successfully.")
            print("DEBUG: Attempting to import chromadesk.ui.main_window...")
            from chromadesk.ui.main_window import MainWindow
            print("DEBUG: chromadesk.ui.main_window imported successfully.")
        except ImportError as e:
            print(f"FATAL: Failed to import GUI components: {e}")
            logger.critical(f"Failed to import GUI components: {e}")
            return 1

        try:
            logger.info("Initializing QApplication...")
            print("DEBUG: Initializing QApplication...")
            app = QApplication(sys.argv)
            print("DEBUG: QApplication initialized.")
            logger.info("QApplication initialized.")
            app.setApplicationName("ChromaDesk")
            app.setOrganizationName("chromadesk")

            logger.info("Initializing MainWindow...")
            print("DEBUG: Initializing MainWindow...")
            window = MainWindow()
            print("DEBUG: MainWindow initialized.")
            logger.info("MainWindow initialized.")

            logger.info("Showing MainWindow...")
            print("DEBUG: Showing MainWindow...")
            window.show()
            print("DEBUG: MainWindow shown.")
            logger.info("MainWindow shown.")

            logger.info("Starting application event loop...")
            print("DEBUG: Starting application event loop...")
            result = app.exec()
            print(f"DEBUG: Application event loop finished with result: {result}")
            return result
        except Exception as e:
            print(f"FATAL: An error occurred during GUI execution: {e}")
            logger.critical(f"An error occurred during GUI execution: {e}", exc_info=True)
            return 1

if __name__ == "__main__":
    print("DEBUG: Script starting in __main__...")
    result = main()
    print(f"DEBUG: main() finished with exit code: {result}")
    sys.exit(result)
