import tkinter as tk
import logging
import os
import sys
#from views.theme_manager import ThemeManager

# Add the current directory to Python path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tracker_manager.log'),
        logging.StreamHandler()
    ]
)

# Now import locally
from controllers.main_controller import MainController
from views.main_view import MainView

def main():
    """Main application entry point"""
    try:
        root = tk.Tk()
        controller = MainController()
        app = MainView(root, controller)
        root.mainloop()
    except Exception as e:
        logging.critical(f"Application failed to start: {e}")
        raise

if __name__ == "__main__":
    main()