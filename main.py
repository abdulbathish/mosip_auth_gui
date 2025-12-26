import customtkinter as ctk
import sys
from pathlib import Path
from utils.auth_handler import AuthHandler
from gui.main_window import MainWindow


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    try:
        print("Initializing authentication handler...")
        auth_handler = AuthHandler()
        print("Authentication handler initialized successfully.")
        
        app = MainWindow(auth_handler)
        app.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
