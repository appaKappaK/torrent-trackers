import tkinter as tk
import logging
import os
import sys

# ===== PATH CONFIGURATION =====

# Add the current directory to Python path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ===== LOGGING CONFIGURATION =====

def setup_logging():
    """Configure application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('tracker_manager.log'),
            logging.StreamHandler()
        ]
    )

# ===== APPLICATION INITIALIZATION =====

def initialize_application():
    """Initialize and start the main application"""
    try:
        # Create root window
        root = tk.Tk()
        root.title("Tracker Manager")
        
        # Initialize MVC components
        controller = MainController()
        view = MainView(root, controller)
        
        # Set up controller-view relationship
        controller.set_view(view)
        
        # Start application
        root.mainloop()
        
    except Exception as e:
        logging.critical(f"Application failed to start: {e}")
        raise

# ===== IMPORTS (After path configuration) =====

# Import locally after path configuration
from controllers.main_controller import MainController
from views.main_view import MainView

# ===== MAIN ENTRY POINT =====

def main():
    """Main application entry point"""
    # Setup logging first
    setup_logging()
    
    # Log application start
    logging.info("Starting Tracker Manager application")
    
    # Initialize and run application
    initialize_application()
    
    # Log application shutdown
    logging.info("Tracker Manager application shutdown complete")

if __name__ == "__main__":
    main()