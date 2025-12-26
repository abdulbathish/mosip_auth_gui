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
        
        # OTP mode selection (only shown for OTP auth type) - moved after ID Type
        self.otp_mode_frame = ctk.CTkFrame(id_frame)
        self.otp_mode_frame.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.otp_mode_frame.grid_remove()  # Hidden by default
        
        otp_mode_label = ctk.CTkLabel(self.otp_mode_frame, text="Mode:", anchor="w")
        otp_mode_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.email_var = ctk.BooleanVar(value=False)
        self.phone_var = ctk.BooleanVar(value=False)
        
        email_checkbox = ctk.CTkCheckBox(
            self.otp_mode_frame,
            text="Email",
            variable=self.email_var,
            width=80
        )
        email_checkbox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        phone_checkbox = ctk.CTkCheckBox(
            self.otp_mode_frame,
            text="Phone",
            variable=self.phone_var,
            width=80
        )
        phone_checkbox.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        id_label = ctk.CTkLabel(id_frame, text="ID:", anchor="w")
        id_label.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        self.id_entry = ctk.CTkEntry(id_frame, placeholder_text="Enter UIN or VID")
        self.id_entry.grid(row=0, column=4, padx=10, pady=10, sticky="ew")
        
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
        
        # Create OTP submit button container (will be placed in form tab below OTP form)
        self.otp_submit_container = ctk.CTkFrame(self.form_tab)
        self.otp_submit_container.grid_columnconfigure(0, weight=1)
        
        self.otp_submit_btn = ctk.CTkButton(
            self.otp_submit_container,
            text="Submit OTP",
            command=self._on_verify_otp,
            width=150,
            state="disabled"
        )
        self.otp_submit_btn.grid(row=0, column=0, padx=20, pady=10)
        self.otp_submit_container.grid_remove()  # Hidden initially
        
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
            self.submit_btn.configure(text="Submit", state="normal", command=self._on_submit)
            self.otp_mode_frame.grid_remove()
            self.otp_submit_container.grid_remove()
        elif auth_type == "demo":
            self.current_form = AuthForm(self.form_tab)
            self.submit_btn.configure(text="Submit", state="normal", command=self._on_submit)
            self.otp_mode_frame.grid_remove()
            self.otp_submit_container.grid_remove()
        elif auth_type == "otp":
            self.current_form = OTPForm(self.form_tab)
            # Show OTP mode selection in header
            self.otp_mode_frame.grid()
            # Change submit button text for OTP generation
            self.submit_btn.configure(text="Generate OTP", state="normal", command=self._on_generate_otp)
            # Show OTP submit container (button disabled until OTP is generated)
            self.otp_submit_container.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
            self.otp_submit_btn.configure(state="disabled")
        
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
        
        # Check if auth type is implemented
        if auth_type not in ["kyc", "demo"]:
            self._update_status("This authentication type is not yet implemented", "error")
            return
        
        # Validate form
        if not hasattr(self.current_form, 'validate'):
            self._update_status("Form validation not available", "error")
            return
        
        if auth_type == "kyc":
            is_valid, error_msg = self.current_form.validate()
        else:  # demo
            is_valid = self.current_form.validate()
            error_msg = "Validation failed" if not is_valid else None
        
        if not is_valid:
            self._update_status(f"Validation error: {error_msg}", "error")
            return
        
        # Get form data
        if auth_type == "kyc":
            demographics_data = self.current_form.get_data()
        else:  # demo
            demographics_data = self.current_form.get_demographic_data()
        
        if not demographics_data:
            self._update_status("Error: Could not create demographics data", "error")
            return
        
        # Disable submit button and show loading
        self.submit_btn.configure(state="disabled")
        self._update_status("Processing authentication request...", "info")
        
        # Run authentication in separate thread to avoid blocking UI
        thread = threading.Thread(
            target=self._perform_authentication,
            args=(individual_id, id_type, demographics_data, auth_type)
        )
        thread.daemon = True
        thread.start()
    
    def _perform_authentication(self, individual_id: str, id_type: str, demographics_data, auth_type: str):
        """Perform authentication in background thread."""
        try:
            if auth_type == "kyc":
                result = self.auth_handler.perform_kyc(
                    individual_id=individual_id,
                    id_type=id_type,
                    demographics_data=demographics_data,
                    consent=True
                )
            else:  # demo
                result = self.auth_handler.perform_auth(
                    individual_id=individual_id,
                    id_type=id_type,
                    demographics_data=demographics_data,
                    consent=True
                )
            
            # Update UI in main thread
            self.after(0, self._handle_authentication_result, result, auth_type)
            
        except Exception as e:
            self.after(0, self._handle_authentication_result, {
                'success': False,
                'error': f"Exception: {str(e)}",
                'data': None,
                'authStatus': False,
                'authToken': None
            }, auth_type)
    
    def _handle_authentication_result(self, result: dict, auth_type: str = "kyc"):
        """Handle authentication result in main thread."""
        # Re-enable submit button
        self.submit_btn.configure(state="normal")
        
        # Switch to results tab
        self.notebook.set("Results")
        
        if result['success']:
            if auth_type == "demo":
                # Display auth response with status and token
                self.profile_view.display_auth_response(
                    response_data=result.get('data', {}),
                    auth_status=result.get('authStatus', False),
                    auth_token=result.get('authToken'),
                    error=result.get('error')
                )
                if result.get('authStatus'):
                    self._update_status("Authentication successful!", "success")
                else:
                    self._update_status("Authentication failed", "error")
            else:
                # Display KYC response with profile data
                self.profile_view.display_response(result['data'])
                self._update_status("Authentication successful!", "success")
        else:
            # Display error
            if auth_type == "demo":
                self.profile_view.display_auth_response(
                    response_data=result.get('data', {}),
                    auth_status=result.get('authStatus', False),
                    auth_token=result.get('authToken'),
                    error=result.get('error')
                )
            else:
                self.profile_view.display_error(result['error'])
            self._update_status(f"Error: {result['error']}", "error")
    
    def _on_generate_otp(self):
        """Handle OTP generation."""
        # Validate ID
        individual_id = self.id_entry.get().strip()
        if not individual_id:
            self._update_status("Error: Please enter UIN or VID", "error")
            if hasattr(self.current_form, 'set_generation_result'):
                self.current_form.set_generation_result(False, error="Please enter UIN or VID")
            return
        
        id_type = self.id_type_var.get()
        
        # Get email/phone selection from header checkboxes
        email = self.email_var.get()
        phone = self.phone_var.get()
        
        if not email and not phone:
            self._update_status("Error: Please select at least one delivery method", "error")
            if hasattr(self.current_form, 'set_generation_result'):
                self.current_form.set_generation_result(False, error="Please select at least one delivery method")
            return
        
        # Reset form for new generation
        self._reset_otp_form()
        
        # Disable generate button and show loading
        self.submit_btn.configure(state="disabled")
        self._update_status("Generating OTP...", "info")
        
        # Run OTP generation in separate thread
        thread = threading.Thread(
            target=self._perform_otp_generation,
            args=(individual_id, id_type, email, phone)
        )
        thread.daemon = True
        thread.start()
    
    def _perform_otp_generation(self, individual_id: str, id_type: str, email: bool, phone: bool):
        """Perform OTP generation in background thread."""
        try:
            result = self.auth_handler.generate_otp(
                individual_id=individual_id,
                id_type=id_type,
                email=email,
                phone=phone
            )
            
            # Update UI in main thread
            self.after(0, self._handle_otp_generation_result, result)
            
        except Exception as e:
            self.after(0, self._handle_otp_generation_result, {
                'success': False,
                'error': f"Exception: {str(e)}",
                'data': None,
                'txn_id': None,
                'masked_email': None,
                'masked_mobile': None
            })
    
    def _handle_otp_generation_result(self, result: dict):
        """Handle OTP generation result in main thread."""
        # Always re-enable generate button so user can generate again
        self.submit_btn.configure(state="normal")
        
        if result['success']:
            # Update form with result (shows in Form tab)
            self.current_form.set_generation_result(
                success=True,
                response_data=result.get('data', {})
            )
            
            # Enable OTP submit button below OTP input
            self.otp_submit_btn.configure(state="normal")
            
            self._update_status("OTP generated successfully! Enter OTP and click Submit OTP to verify.", "success")
        else:
            # Show error in form
            self.current_form.set_generation_result(
                success=False,
                response_data=result.get('data', {}),
                error=result.get('error', 'Unknown error')
            )
            # Disable submit button if generation failed
            self.otp_submit_btn.configure(state="disabled")
            self._update_status(f"Error: {result['error']}", "error")
    
    def _on_verify_otp(self):
        """Handle OTP verification."""
        # Validate ID
        individual_id = self.id_entry.get().strip()
        if not individual_id:
            self._update_status("Error: Please enter UIN or VID", "error")
            return
        
        id_type = self.id_type_var.get()
        
        # Validate form
        if not hasattr(self.current_form, 'validate'):
            self._update_status("Form validation not available", "error")
            return
        
        is_valid, error_msg = self.current_form.validate()
        if not is_valid:
            self._update_status(f"Validation error: {error_msg}", "error")
            return
        
        # Get OTP value and transaction ID
        otp_value = self.current_form.get_otp_value()
        txn_id = self.current_form.get_txn_id()
        
        # Disable submit button and show loading
        self.submit_btn.configure(state="disabled")
        self._update_status("Verifying OTP...", "info")
        
        # Run OTP verification in separate thread
        thread = threading.Thread(
            target=self._perform_otp_verification,
            args=(individual_id, id_type, otp_value, txn_id)
        )
        thread.daemon = True
        thread.start()
    
    def _perform_otp_verification(self, individual_id: str, id_type: str, otp_value: str, txn_id: str):
        """Perform OTP verification in background thread."""
        try:
            result = self.auth_handler.verify_otp(
                individual_id=individual_id,
                id_type=id_type,
                otp_value=otp_value,
                txn_id=txn_id,
                consent=True
            )
            
            # Update UI in main thread
            self.after(0, self._handle_otp_verification_result, result)
            
        except Exception as e:
            self.after(0, self._handle_otp_verification_result, {
                'success': False,
                'error': f"Exception: {str(e)}",
                'data': None
            })
    
    def _handle_otp_verification_result(self, result: dict):
        """Handle OTP verification result in main thread."""
        # Re-enable OTP submit button
        self.otp_submit_btn.configure(state="normal")
        
        # Re-enable Generate OTP button so user can generate again
        self.submit_btn.configure(state="normal")
        
        # Switch to results tab
        self.notebook.set("Results")
        
        if result['success']:
            # Display KYC response (OTP verification returns KYC data, same as KYC auth)
            self.profile_view.display_response(result['data'])
            self._update_status("OTP verified successfully! You can generate a new OTP if needed.", "success")
        else:
            # Display error
            self.profile_view.display_error(result['error'])
            self._update_status(f"Error: {result['error']}", "error")
    
    def _reset_otp_form(self):
        """Reset OTP form to allow new generation."""
        if hasattr(self.current_form, 'otp_entry'):
            self.current_form.otp_entry.delete(0, "end")
            self.current_form.otp_entry.configure(state="disabled")
        if hasattr(self.current_form, 'response_textbox'):
            self.current_form.response_textbox.configure(state="normal")
            self.current_form.response_textbox.delete("1.0", "end")
            self.current_form.response_textbox.configure(state="disabled")
        if hasattr(self.current_form, 'txn_id'):
            self.current_form.txn_id = None
        # Disable OTP submit button
        self.otp_submit_btn.configure(state="disabled")
    
    def _update_status(self, message: str, status_type: str = "info"):
        """Update status bar message."""
        color_map = {
            "info": "gray",
            "success": "green",
            "error": "red"
        }
        color = color_map.get(status_type, "gray")
        self.status_label.configure(text=message, text_color=color)

