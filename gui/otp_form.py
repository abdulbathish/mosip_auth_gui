import customtkinter as ctk
from typing import Optional, Dict, Any, Tuple


class OTPForm(ctk.CTkScrollableFrame):
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.txn_id = None
        self.masked_email = None
        self.masked_mobile = None
        self.generation_response = None
        
        self._create_response_and_verify_section()
    
    def _create_response_and_verify_section(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        response_container = ctk.CTkFrame(main_frame)
        response_container.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        response_container.grid_columnconfigure(0, weight=1)
        response_container.grid_rowconfigure(1, weight=1)
        
        response_header = ctk.CTkLabel(
            response_container,
            text="OTP Generation Response",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        response_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.response_textbox = ctk.CTkTextbox(
            response_container,
            height=200,
            wrap="word",
            font=ctk.CTkFont(size=11),
            state="disabled"
        )
        self.response_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        verify_container = ctk.CTkFrame(main_frame)
        verify_container.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        verify_container.grid_columnconfigure(0, weight=1)
        
        verify_header = ctk.CTkLabel(
            verify_container,
            text="Enter OTP",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        verify_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        otp_label = ctk.CTkLabel(
            verify_container,
            text="OTP:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        otp_label.grid(row=1, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.otp_entry = ctk.CTkEntry(
            verify_container,
            placeholder_text="Enter OTP",
            width=200,
            font=ctk.CTkFont(size=14)
        )
        self.otp_entry.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.otp_entry.configure(state="disabled")
    
    def get_otp_value(self) -> str:
        return self.otp_entry.get().strip()
    
    def set_generation_result(self, success: bool, response_data: Dict[str, Any] = None, error: str = None):
        self.response_textbox.configure(state="normal")
        self.response_textbox.delete("1.0", "end")
        
        if success and response_data:
            self.generation_response = response_data
            self.txn_id = response_data.get("transactionID")
            response_section = response_data.get("response", {})
            self.masked_email = response_section.get("maskedEmail")
            self.masked_mobile = response_section.get("maskedMobile")
            
            self.otp_entry.configure(state="normal")
            
            response_text = "OTP sent successfully!\n\n"
            if self.masked_email:
                response_text += f"Email: {self.masked_email}\n"
            if self.masked_mobile:
                response_text += f"Mobile: {self.masked_mobile}\n"
            
            if response_data:
                response_text += "\n--- Response Details ---\n\n"
                for key, value in sorted(response_data.items()):
                    if key not in ["response", "errors"] and value is not None:
                        formatted_key = key.replace("_", " ").title()
                        response_text += f"{formatted_key}: {value}\n"
                
                response_section = response_data.get("response", {})
                for key, value in sorted(response_section.items()):
                    if key not in ["maskedEmail", "maskedMobile"] and value is not None:
                        formatted_key = key.replace("_", " ").title()
                        response_text += f"{formatted_key}: {value}\n"
            
            self.response_textbox.insert("1.0", response_text)
            self.response_textbox.configure(state="disabled")
        else:
            error_text = f"Error: {error or 'Unknown error'}\n\n"
            if response_data:
                error_text += "--- Response Details ---\n\n"
                for key, value in sorted(response_data.items()):
                    if value is not None:
                        formatted_key = key.replace("_", " ").title()
                        error_text += f"{formatted_key}: {value}\n"
            
            self.response_textbox.insert("1.0", error_text)
            self.response_textbox.configure(state="disabled")
    
    def get_txn_id(self) -> Optional[str]:
        return self.txn_id
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        if not self.txn_id:
            return False, "Please generate OTP first"
        
        otp_value = self.get_otp_value()
        if not otp_value:
            return False, "Please enter OTP value"
        
        if len(otp_value) < 4:
            return False, "OTP must be at least 4 digits"
        
        return True, None
