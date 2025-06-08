# main.py

import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# Define error dialog function first, as it's used in init_app
def show_error_dialog(error_msg):
    """Show error dialog with detailed message"""
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("Application Error")
    msg.setInformativeText(str(error_msg))
    msg.setWindowTitle("Error")
    msg.exec_()

# Initialize environment paths first
def init_app():
    """Initialize application environment"""
    try:
        # Add parent directory to Python path
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
            
        # Enable High DPI support
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
    except Exception as e:
        show_error_dialog(f"Error initializing application: {str(e)}")
        sys.exit(1)

# Call init_app before importing from the package
init_app()

# Now we can import from finance_app
from finance_app.utils.logging_config import setup_logging

# Set up logging
logger = setup_logging()

def main():
    # Initialize environment
    init_app()
    
    try:
        # Import after path setup
        from finance_app.gui.main_app import MainApp
        
        logger.info("Starting Finance App")
        
        # Create QApplication instance
        app = QApplication(sys.argv)
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        
        # Create and show main window
        main_window = MainApp()
        main_window.show()
        
        # Start event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        error_msg = f"Application error: {str(e)}\n\n{traceback.format_exc()}"
        logger.error(error_msg)
        show_error_dialog(error_msg)
        sys.exit(1)

if __name__ == '__main__':
    main()


