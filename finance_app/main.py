# main.py

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

def main():
    # Enable High DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # Create the application
    app = QApplication(sys.argv)
    
    # Add the parent directory to sys.path to make the package importable
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
        
    # Set application icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'logo.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Import the main application class which handles login and dashboards
    from finance_app.gui.main_app import MainApp
    
    # Create and show the main window
    main_window = MainApp()
    main_window.show()
    
    # Start the event loop
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())


