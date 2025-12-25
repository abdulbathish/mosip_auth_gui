"""Main application window."""
import customtkinter as ctk
import threading
from typing import Optional, Callable
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config_loader import GUIConfig
from .kyc_form import KYCForm
from .auth_form import AuthForm
from .otp_form import OTPForm
from .profile_view import ProfileView


class MainWindow(ctk.CTk):
    """Main application window."""
    
    def __init__(self, auth_handler, **kwargs):
        super().__init__(**kwargs)
        
        self.auth_handler = auth_handler
        self.current_form: Optional[ctk.CTkFrame] = None
        self.profile_view: Optional[ProfileView] = None
        self.gui_config = GUIConfig()
        
        self.title("MOSIP Authentication")
        self.geometry("1000x700")
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_header()
        self._create_main_content()
        self._create_status_bar()
    
    def _create_header(self):
        """Create header with auth type selection and UIN/VID input."""
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Auth type selection
        auth_type_label = ctk.CTkLabel(header_frame, text="Auth Type:", anchor="w")
        auth_type_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.auth_type_var = ctk.StringVar(value="kyc")
        auth_type_frame = ctk.CTkFrame(header_frame)
        auth_type_frame.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        kyc_radio = ctk.CTkRadioButton(
            auth_type_frame,
            text="KYC Auth",
            variable=self.auth_type_var,
            value="kyc",
            command=self._on_auth_type_changed
        )
        kyc_radio.grid(row=0, column=0, padx=10)
        
        demo_radio = ctk.CTkRadioButton(
            auth_type_frame,
            text="Demographic Auth",
            variable=self.auth_type_var,
            value="demo",
            command=self._on_auth_type_changed
        )
        demo_radio.grid(row=0, column=1, padx=10)
        
        otp_radio = ctk.CTkRadioButton(
            auth_type_frame,
            text="OTP Auth",
            variable=self.auth_type_var,
            value="otp",
            command=self._on_auth_type_changed
        )
        otp_radio.grid(row=0, column=2, padx=10)
        
        # UIN/VID input
        id_frame = ctk.CTkFrame(header_frame)
        id_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        id_frame.grid_columnconfigure(1, weight=1)
        
        id_type_label = ctk.CTkLabel(id_frame, text="ID Type:", anchor="w")
        id_type_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        id_types = self.gui_config.id_types
        default_id_type = self.gui_config.default_id_type
        self.id_type_var = ctk.StringVar(value=default_id_type)
        id_type_combo = ctk.CTkComboBox(
            id_frame,
            values=id_types,
            variable=self.id_type_var,
            width=100
        )
        id_type_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        id_label = ctk.CTkLabel(id_frame, text="ID:", anchor="w")
        id_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        self.id_entry = ctk.CTkEntry(id_frame, placeholder_text="Enter UIN or VID")
        self.id_entry.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        
        # Submit button
        self.submit_btn = ctk.CTkButton(
            header_frame,
            text="Submit",
            command=self._on_submit,
            width=100
        )
        self.submit_btn.grid(row=1, column=2, padx=10, pady=10)
    
    def _create_main_content(self):
        """Create main content area with form and profile view."""
        # Create notebook for form and results
        self.notebook = ctk.CTkTabview(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # Form tab
        self.form_tab = self.notebook.add("Form")
        self.form_tab.grid_columnconfigure(0, weight=1)
        self.form_tab.grid_rowconfigure(0, weight=1)
        
        # Results tab
        self.results_tab = self.notebook.add("Results")
        self.results_tab.grid_columnconfigure(0, weight=1)
        self.results_tab.grid_rowconfigure(0, weight=1)
        
        # Create profile view
        self.profile_view = ProfileView(self.results_tab)
        self.profile_view.grid(row=0, column=0, sticky="nsew")
        
        # Load initial form after tabs are created
        self._on_auth_type_changed()
    
    def _create_status_bar(self):
        """Create status bar at bottom."""
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            anchor="w"
        )
        self.status_label.grid(row=2, column=0, sticky="ew", padx=20, pady=5)
    
    def _on_auth_type_changed(self):
        """Handle auth type selection change."""
        # Remove current form
        if self.current_form:
            self.current_form.destroy()
        
        # Create new form based on selection
        auth_type = self.auth_type_var.get()
        
        if auth_type == "kyc":
            self.current_form = KYCForm(self.form_tab)
            self.submit_btn.configure(state="normal")
        elif auth_type == "demo":
            self.current_form = AuthForm(self.form_tab)
            self.submit_btn.configure(state="disabled")
        elif auth_type == "otp":
            self.current_form = OTPForm(self.form_tab)
            self.submit_btn.configure(state="disabled")
        
        if self.current_form:
            self.current_form.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    def _on_submit(self):
        """Handle form submission."""
        # Validate ID
        individual_id = self.id_entry.get().strip()
        if not individual_id:
            self._update_status("Error: Please enter UIN or VID", "error")
            return
        
        id_type = self.id_type_var.get()
        auth_type = self.auth_type_var.get()
        
        # Only KYC is implemented
        if auth_type != "kyc":
            self._update_status("This authentication type is not yet implemented", "error")
            return
        
        # Validate form
        if not hasattr(self.current_form, 'validate'):
            self._update_status("Form validation not available", "error")
            return
        
        is_valid, error_msg = self.current_form.validate()
        if not is_valid:
            self._update_status(f"Validation error: {error_msg}", "error")
            return
        
        # Get form data
        demographics_data = self.current_form.get_data()
        if not demographics_data:
            self._update_status("Error: Could not create demographics data", "error")
            return
        
        # Disable submit button and show loading
        self.submit_btn.configure(state="disabled")
        self._update_status("Processing authentication request...", "info")
        
        # Run authentication in separate thread to avoid blocking UI
        thread = threading.Thread(
            target=self._perform_authentication,
            args=(individual_id, id_type, demographics_data)
        )
        thread.daemon = True
        thread.start()
    
    def _perform_authentication(self, individual_id: str, id_type: str, demographics_data):
        """Perform authentication in background thread."""
        try:
            result = self.auth_handler.perform_kyc(
                individual_id=individual_id,
                id_type=id_type,
                demographics_data=demographics_data,
                consent=True
            )
            
            # Update UI in main thread
            self.after(0, self._handle_authentication_result, result)
            
        except Exception as e:
            self.after(0, self._handle_authentication_result, {
                'success': False,
                'error': f"Exception: {str(e)}",
                'data': None
            })
    
    def _handle_authentication_result(self, result: dict):
        """Handle authentication result in main thread."""
        # Re-enable submit button
        self.submit_btn.configure(state="normal")
        
        if result['success']:
            # Switch to results tab
            self.notebook.set("Results")
            
            # Display response
            self.profile_view.display_response(result['data'])
            self._update_status("Authentication successful!", "success")
        else:
            # Display error
            self.notebook.set("Results")
            self.profile_view.display_error(result['error'])
            self._update_status(f"Error: {result['error']}", "error")
    
    def _update_status(self, message: str, status_type: str = "info"):
        """Update status bar message."""
        color_map = {
            "info": "gray",
            "success": "green",
            "error": "red"
        }
        color = color_map.get(status_type, "gray")
        self.status_label.configure(text=message, text_color=color)

