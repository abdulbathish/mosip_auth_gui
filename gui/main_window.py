import customtkinter as ctk
import threading
from typing import Optional, Callable
import sys
import platform
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config_loader import GUIConfig
from .kyc_form import KYCForm
from .auth_form import AuthForm
from .otp_form import OTPForm
from .profile_view import ProfileView


class MainWindow(ctk.CTk):
    
    def __init__(self, auth_handler, **kwargs):
        super().__init__(**kwargs)
        
        self.auth_handler = auth_handler
        self.current_form: Optional[ctk.CTkFrame] = None
        self.profile_view: Optional[ProfileView] = None
        self.gui_config = GUIConfig()
        
        self.title("MOSIP IDA Authentication Testing Tool")
        self.geometry("1200x800")
        
        self._set_window_icon()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self._create_header()
        self._create_main_content()
        self._create_status_bar()
    
    def _set_window_icon(self):
        logo_path = Path(__file__).parent.parent / "logo.png"
        if not logo_path.exists():
            return
        
        try:
            if platform.system() == "Windows":
                try:
                    import ctypes
                    myappid = 'com.mosip.auth.gui.1.0'
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                except:
                    pass
                
                ico_path = Path(__file__).parent.parent / "logo.ico"
                if ico_path.exists():
                    self.iconbitmap(str(ico_path))
                else:
                    try:
                        from PIL import Image
                        img = Image.open(logo_path)
                        ico_path = Path(__file__).parent.parent / "logo.ico"
                        img.save(ico_path, format='ICO')
                        self.iconbitmap(str(ico_path))
                    except:
                        pass
            else:
                try:
                    from PIL import Image, ImageTk
                    import tkinter as tk
                    img = Image.open(logo_path)
                    photo = ImageTk.PhotoImage(img)
                    self.iconphoto(False, photo)
                    self._icon_photo = photo
                except:
                    pass
        except Exception:
            pass
    
    def _create_header(self):
        header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("#f0f0f0", "#1a1a1a"))
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(1, weight=1)
        
        logo_path = Path(__file__).parent.parent / "logo.png"
        logo_exists = False
        if logo_path.exists():
            try:
                from PIL import Image
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((40, 40), Image.Resampling.LANCZOS)
                logo_ctk = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(40, 40))
                logo_label = ctk.CTkLabel(header_frame, image=logo_ctk, text="")
                logo_label.grid(row=0, column=0, padx=(25, 10), pady=15, sticky="w")
                logo_exists = True
            except Exception:
                pass
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="MOSIP IDA Authentication Testing Tool",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=(25 if not logo_exists else 80, 0), pady=15, sticky="w")
        
        self.auth_type_var = ctk.StringVar(value="kyc")
        auth_type_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        auth_type_frame.grid(row=0, column=1, padx=20, pady=15, sticky="e")
        
        kyc_radio = ctk.CTkRadioButton(
            auth_type_frame,
            text="Demo KYC",
            variable=self.auth_type_var,
            value="kyc",
            command=self._on_auth_type_changed,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        kyc_radio.grid(row=0, column=0, padx=8)
        
        demo_radio = ctk.CTkRadioButton(
            auth_type_frame,
            text="Demo Auth",
            variable=self.auth_type_var,
            value="demo",
            command=self._on_auth_type_changed,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        demo_radio.grid(row=0, column=1, padx=8)
        
        otp_radio = ctk.CTkRadioButton(
            auth_type_frame,
            text="OTP KYC",
            variable=self.auth_type_var,
            value="otp",
            command=self._on_auth_type_changed,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        otp_radio.grid(row=0, column=2, padx=8)
        
        input_card = ctk.CTkFrame(self, corner_radius=12)
        input_card.grid(row=1, column=0, sticky="ew", padx=20, pady=(15, 20))
        input_card.grid_columnconfigure(4, weight=1)
        
        ctk.CTkLabel(
            input_card,
            text="ID Type:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).grid(row=0, column=0, padx=(15, 8), pady=15, sticky="w")
        
        id_types = self.gui_config.id_types
        default_id_type = self.gui_config.default_id_type
        self.id_type_var = ctk.StringVar(value=default_id_type)
        id_type_combo = ctk.CTkComboBox(
            input_card,
            values=id_types,
            variable=self.id_type_var,
            width=110,
            font=ctk.CTkFont(size=12)
        )
        id_type_combo.grid(row=0, column=1, padx=8, pady=15, sticky="w")
        
        self.otp_mode_frame = ctk.CTkFrame(input_card, fg_color="transparent")
        self.otp_mode_frame.grid(row=0, column=2, padx=8, pady=15, sticky="w")
        self.otp_mode_frame.grid_remove()
        
        ctk.CTkLabel(
            self.otp_mode_frame,
            text="Mode:",
            font=ctk.CTkFont(size=12),
            anchor="w"
        ).grid(row=0, column=0, padx=(0, 5), sticky="w")
        
        self.email_var = ctk.BooleanVar(value=False)
        self.phone_var = ctk.BooleanVar(value=False)
        
        email_checkbox = ctk.CTkCheckBox(
            self.otp_mode_frame,
            text="Email",
            variable=self.email_var,
            width=70,
            font=ctk.CTkFont(size=11)
        )
        email_checkbox.grid(row=0, column=1, padx=5, sticky="w")
        
        phone_checkbox = ctk.CTkCheckBox(
            self.otp_mode_frame,
            text="Phone",
            variable=self.phone_var,
            width=70,
            font=ctk.CTkFont(size=11)
        )
        phone_checkbox.grid(row=0, column=2, padx=5, sticky="w")
        
        ctk.CTkLabel(
            input_card,
            text="ID:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).grid(row=0, column=3, padx=(15, 8), pady=15, sticky="w")
        
        self.id_entry = ctk.CTkEntry(
            input_card,
            placeholder_text="Enter UIN or VID",
            font=ctk.CTkFont(size=13),
            height=35
        )
        self.id_entry.grid(row=0, column=4, padx=(0, 15), pady=15, sticky="ew")
        
        self.submit_btn = ctk.CTkButton(
            input_card,
            text="Submit",
            command=self._on_submit,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8
        )
        self.submit_btn.grid(row=0, column=5, padx=(10, 15), pady=15, sticky="e")
    
    def _create_main_content(self):
        self.notebook = ctk.CTkTabview(self, corner_radius=12)
        self.notebook.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        
        self.form_tab = self.notebook.add("Form")
        self.form_tab.grid_columnconfigure(0, weight=1)
        self.form_tab.grid_rowconfigure(0, weight=1)
        
        self.results_tab = self.notebook.add("Results")
        self.results_tab.grid_columnconfigure(0, weight=1)
        self.results_tab.grid_rowconfigure(0, weight=1)
        
        self.profile_view = ProfileView(self.results_tab)
        self.profile_view.grid(row=0, column=0, sticky="nsew")
        
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
        self.otp_submit_container.grid_remove()
        
        self._on_auth_type_changed()
    
    def _create_status_bar(self):
        status_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("#e8e8e8", "#2a2a2a"), height=35)
        status_frame.grid(row=3, column=0, sticky="ew", padx=0, pady=0)
        status_frame.grid_propagate(False)
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            anchor="w",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.grid(row=0, column=0, sticky="ew", padx=20, pady=8)
    
    def _on_auth_type_changed(self):
        if self.current_form:
            self.current_form.destroy()
            self.current_form = None
        
        for widget in self.profile_view.winfo_children():
            widget.destroy()
        self.profile_view.current_row = 0
        self.profile_view.photo_image = None
        self.profile_view.photo_label = None
        
        self.notebook.set("Form")
        
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
            self.otp_mode_frame.grid()
            self.submit_btn.configure(text="Generate OTP", state="normal", command=self._on_generate_otp)
            self.otp_submit_container.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
            self.otp_submit_btn.configure(state="disabled")
            if hasattr(self.current_form, 'reset'):
                self.current_form.reset()
        
        if self.current_form:
            self.current_form.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            self.current_form.update()
        
        self.id_entry.delete(0, "end")
        self.email_var.set(False)
        self.phone_var.set(False)
        self._update_status("Ready", "info")
    
    def _on_submit(self):
        individual_id = self.id_entry.get().strip()
        individual_id = self.id_entry.get().strip()
        if not individual_id:
            self._update_status("Error: Please enter UIN or VID", "error")
            return
        
        id_type = self.id_type_var.get()
        auth_type = self.auth_type_var.get()
        
        if auth_type not in ["kyc", "demo"]:
            self._update_status("This authentication type is not yet implemented", "error")
            return
        
        if not hasattr(self.current_form, 'validate'):
            self._update_status("Form validation not available", "error")
            return
        
        if auth_type == "kyc":
            is_valid, error_msg = self.current_form.validate()
        else:
            is_valid = self.current_form.validate()
            error_msg = "Validation failed" if not is_valid else None
        
        if not is_valid:
            self._update_status(f"Validation error: {error_msg}", "error")
            return
        
        if auth_type == "kyc":
            demographics_data = self.current_form.get_data()
        else:
            demographics_data = self.current_form.get_demographic_data()
        
        if not demographics_data:
            self._update_status("Error: Could not create demographics data", "error")
            return
        
        self.submit_btn.configure(state="disabled")
        self._update_status("Processing authentication request...", "info")
        
        thread = threading.Thread(
            target=self._perform_authentication,
            args=(individual_id, id_type, demographics_data, auth_type)
        )
        thread.daemon = True
        thread.start()
    
    def _perform_authentication(self, individual_id: str, id_type: str, demographics_data, auth_type: str):
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
        self.submit_btn.configure(state="normal")
        self.notebook.set("Results")
        
        if result['success']:
            if auth_type == "demo":
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
                self.profile_view.display_response(result['data'])
                self._update_status("Authentication successful!", "success")
        else:
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
        individual_id = self.id_entry.get().strip()
        if not individual_id:
            self._update_status("Error: Please enter UIN or VID", "error")
            if hasattr(self.current_form, 'set_generation_result'):
                self.current_form.set_generation_result(False, error="Please enter UIN or VID")
            return
        
        id_type = self.id_type_var.get()
        email = self.email_var.get()
        phone = self.phone_var.get()
        
        if not email and not phone:
            self._update_status("Error: Please select at least one delivery method", "error")
            if hasattr(self.current_form, 'set_generation_result'):
                self.current_form.set_generation_result(False, error="Please select at least one delivery method")
            return
        
        self._reset_otp_form()
        self.submit_btn.configure(state="disabled")
        self._update_status("Generating OTP...", "info")
        
        thread = threading.Thread(
            target=self._perform_otp_generation,
            args=(individual_id, id_type, email, phone)
        )
        thread.daemon = True
        thread.start()
    
    def _perform_otp_generation(self, individual_id: str, id_type: str, email: bool, phone: bool):
        try:
            result = self.auth_handler.generate_otp(
                individual_id=individual_id,
                id_type=id_type,
                email=email,
                phone=phone
            )
            
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
        self.submit_btn.configure(state="normal")
        
        if result['success']:
            self.current_form.set_generation_result(
                success=True,
                response_data=result.get('data', {})
            )
            self.otp_submit_btn.configure(state="normal")
            self._update_status("OTP generated successfully! Enter OTP and click Submit OTP to verify.", "success")
        else:
            self.current_form.set_generation_result(
                success=False,
                response_data=result.get('data', {}),
                error=result.get('error', 'Unknown error')
            )
            self.otp_submit_btn.configure(state="disabled")
            self._update_status(f"Error: {result['error']}", "error")
    
    def _on_verify_otp(self):
        individual_id = self.id_entry.get().strip()
        if not individual_id:
            self._update_status("Error: Please enter UIN or VID", "error")
            return
        
        id_type = self.id_type_var.get()
        
        if not hasattr(self.current_form, 'validate'):
            self._update_status("Form validation not available", "error")
            return
        
        is_valid, error_msg = self.current_form.validate()
        if not is_valid:
            self._update_status(f"Validation error: {error_msg}", "error")
            return
        
        otp_value = self.current_form.get_otp_value()
        txn_id = self.current_form.get_txn_id()
        
        self.submit_btn.configure(state="disabled")
        self._update_status("Verifying OTP...", "info")
        
        thread = threading.Thread(
            target=self._perform_otp_verification,
            args=(individual_id, id_type, otp_value, txn_id)
        )
        thread.daemon = True
        thread.start()
    
    def _perform_otp_verification(self, individual_id: str, id_type: str, otp_value: str, txn_id: str):
        try:
            result = self.auth_handler.verify_otp(
                individual_id=individual_id,
                id_type=id_type,
                otp_value=otp_value,
                txn_id=txn_id,
                consent=True
            )
            
            self.after(0, self._handle_otp_verification_result, result)
            
        except Exception as e:
            self.after(0, self._handle_otp_verification_result, {
                'success': False,
                'error': f"Exception: {str(e)}",
                'data': None
            })
    
    def _handle_otp_verification_result(self, result: dict):
        self.otp_submit_btn.configure(state="normal")
        self.submit_btn.configure(state="normal")
        self.notebook.set("Results")
        
        if result['success']:
            self.profile_view.display_response(result['data'])
            self._update_status("OTP verified successfully! You can generate a new OTP if needed.", "success")
        else:
            self.profile_view.display_error(result['error'])
            self._update_status(f"Error: {result['error']}", "error")
    
    def _reset_otp_form(self):
        if hasattr(self.current_form, 'otp_entry'):
            self.current_form.otp_entry.delete(0, "end")
            self.current_form.otp_entry.configure(state="disabled")
        if hasattr(self.current_form, 'response_textbox'):
            self.current_form.response_textbox.configure(state="normal")
            self.current_form.response_textbox.delete("1.0", "end")
            self.current_form.response_textbox.configure(state="disabled")
        if hasattr(self.current_form, 'txn_id'):
            self.current_form.txn_id = None
        self.otp_submit_btn.configure(state="disabled")
    
    def _update_status(self, message: str, status_type: str = "info"):
        if not hasattr(self, 'status_label') or self.status_label is None:
            return
        color_map = {
            "info": "gray",
            "success": "green",
            "error": "red"
        }
        color = color_map.get(status_type, "gray")
        self.status_label.configure(text=message, text_color=color)

