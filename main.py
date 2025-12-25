"""Main entry point for MOSIP Authentication GUI application."""
import customtkinter as ctk
import sys
from pathlib import Path
from utils.auth_handler import AuthHandler
from gui.main_window import MainWindow


def main():
    """Main function to start the application."""
    # Set appearance mode and color theme
    ctk.set_appearance_mode("dark")  # Options: "light", "dark", "system"
    ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"
    
    try:
        # Initialize auth handler
        print("Initializing authentication handler...")
        auth_handler = AuthHandler()
        print("Authentication handler initialized successfully.")
        
        # Create and run main window
        app = MainWindow(auth_handler)
        app.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

