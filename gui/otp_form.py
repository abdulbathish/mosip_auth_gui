"""OTP authentication form (placeholder)."""
import customtkinter as ctk


class OTPForm(ctk.CTkFrame):
    """Placeholder form for OTP authentication."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        
        # Placeholder label
        label = ctk.CTkLabel(
            self,
            text="OTP Authentication",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        label.grid(row=0, column=0, pady=50, padx=20)
        
        coming_soon = ctk.CTkLabel(
            self,
            text="Coming Soon",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        coming_soon.grid(row=1, column=0, pady=10, padx=20)
    
    def get_data(self):
        """Return None as this is a placeholder."""
        return None
    
    def validate(self):
        """Always returns False for placeholder."""
        return False

