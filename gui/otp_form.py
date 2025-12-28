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
        
        self._enable_mousewheel_scroll()
        self._create_response_and_verify_section()
    
    def _enable_mousewheel_scroll(self):
        import platform
        
        def on_mousewheel(event):
            try:
                if hasattr(self, '_parent_canvas') and self._parent_canvas:
                    if platform.system() == "Darwin":
                        self._parent_canvas.yview_scroll(int(-1 * (event.delta)), "units")
                    else:
                        self._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except:
                pass
        
        def on_linux_scroll_up(event):
            try:
                if hasattr(self, '_parent_canvas') and self._parent_canvas:
                    self._parent_canvas.yview_scroll(-1, "units")
            except:
                pass
        
        def on_linux_scroll_down(event):
            try:
                if hasattr(self, '_parent_canvas') and self._parent_canvas:
                    self._parent_canvas.yview_scroll(1, "units")
            except:
                pass
        
        def bind_to_mousewheel(event):
            root = self.winfo_toplevel()
            root.bind_all("<MouseWheel>", on_mousewheel)
            if platform.system() == "Linux":
                root.bind_all("<Button-4>", on_linux_scroll_up)
                root.bind_all("<Button-5>", on_linux_scroll_down)
        
        def unbind_from_mousewheel(event):
            root = self.winfo_toplevel()
            root.unbind_all("<MouseWheel>")
            if platform.system() == "Linux":
                root.unbind_all("<Button-4>")
                root.unbind_all("<Button-5>")
        
        self.bind("<Enter>", bind_to_mousewheel)
        self.bind("<Leave>", unbind_from_mousewheel)
    
    def _create_response_and_verify_section(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, columnspan=2, padx=15, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        response_container = ctk.CTkFrame(main_frame, corner_radius=10)
        response_container.grid(row=0, column=0, padx=(0, 8), pady=0, sticky="nsew")
        response_container.grid_columnconfigure(0, weight=1)
        response_container.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            response_container,
            text="OTP Generation Response",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=12, pady=(10, 8), sticky="w")
        
        self.response_textbox = ctk.CTkTextbox(
            response_container,
            height=200,
            wrap="word",
            font=ctk.CTkFont(size=11),
            state="disabled",
            fg_color=("#f8f8f8", "#2a2a2a"),
            corner_radius=8
        )
        self.response_textbox.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        
        verify_container = ctk.CTkFrame(main_frame, corner_radius=10)
        verify_container.grid(row=0, column=1, padx=(8, 0), pady=0, sticky="nsew")
        verify_container.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            verify_container,
            text="Enter OTP",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=12, pady=(10, 12), sticky="w")
        
        ctk.CTkLabel(
            verify_container,
            text="OTP Code:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).grid(row=1, column=0, padx=12, pady=(0, 6), sticky="w")
        
        self.otp_entry = ctk.CTkEntry(
            verify_container,
            placeholder_text="Enter 6-digit OTP",
            font=ctk.CTkFont(size=12),
            height=32,
            corner_radius=8
        )
        self.otp_entry.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="ew")
        self.otp_entry.configure(state="disabled")
    
    def get_otp_value(self) -> str:
        return self.otp_entry.get().strip()
    
    def reset(self):
        self.txn_id = None
        self.masked_email = None
        self.masked_mobile = None
        self.generation_response = None
        self.otp_entry.delete(0, "end")
        self.otp_entry.configure(state="disabled")
        self.response_textbox.configure(state="normal")
        self.response_textbox.delete("1.0", "end")
        self.response_textbox.configure(state="disabled")
    
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
