import json
import customtkinter as ctk
from PIL import Image, ImageTk
from typing import Dict, Any, Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.photo_handler import decode_photo
import platform


class ProfileView(ctk.CTkScrollableFrame):
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.photo_image = None
        self.photo_label = None
        self.current_row = 0
        
        self._enable_mousewheel_scroll()
    
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
        
    def display_auth_response(self, response_data: Dict[str, Any], auth_status: bool = None, auth_token: str = None, error: str = None):
        for widget in self.winfo_children():
            widget.destroy()
        
        self.current_row = 0
        
        self._create_section_header("Authentication Result")
        
        if auth_status is not None:
            status_card = ctk.CTkFrame(self, corner_radius=12, fg_color=("#f0f0f0", "#1a1a1a"))
            status_card.grid(row=self.current_row, column=0, pady=15, padx=20, sticky="ew")
            status_card.grid_columnconfigure(1, weight=1)
            
            status_text = "✓ PASSED" if auth_status else "✗ FAILED"
            status_color = "#2ecc71" if auth_status else "#e74c3c"
            
            status_label = ctk.CTkLabel(
                status_card,
                text=status_text,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=status_color
            )
            status_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
            self.current_row += 1
        
        if auth_token:
            token_card = ctk.CTkFrame(self, corner_radius=12)
            token_card.grid(row=self.current_row, column=0, pady=10, padx=20, sticky="ew")
            token_card.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(
                token_card,
                text="Auth Token",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            ).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
            
            token_text = ctk.CTkTextbox(
                token_card,
                height=60,
                wrap="word",
                font=ctk.CTkFont(size=11, family="Courier"),
                fg_color=("#f8f8f8", "#2a2a2a")
            )
            token_text.insert("1.0", auth_token)
            token_text.configure(state="disabled")
            token_text.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
            self.current_row += 1
        
        if error:
            error_card = ctk.CTkFrame(self, corner_radius=12, fg_color=("#ffe6e6", "#3a1a1a"))
            error_card.grid(row=self.current_row, column=0, pady=10, padx=20, sticky="ew")
            error_card.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(
                error_card,
                text="Error",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#e74c3c",
                anchor="w"
            ).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
            
            error_text = ctk.CTkTextbox(
                error_card,
                height=100,
                wrap="word",
                font=ctk.CTkFont(size=12),
                fg_color=("#fff5f5", "#4a2a2a"),
                text_color="#8B0000"
            )
            error_text.insert("1.0", error)
            error_text.configure(state="disabled")
            error_text.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
            self.current_row += 1
        
        if response_data:
            self._create_section_header("Response Details")
            response_section = response_data.get("response", {})
            if response_section:
                response_fields = {}
                for key, value in sorted(response_section.items()):
                    if key not in ["authStatus", "authToken"] and value is not None:
                        formatted_key = self._format_field_name(key)
                        response_fields[formatted_key] = str(value)
                
                if response_fields:
                    self._display_key_value_pairs(response_fields)
            
            other_fields = {}
            for key, value in sorted(response_data.items()):
                if key not in ["response", "errors"] and value is not None and str(value).strip():
                    formatted_key = self._format_field_name(key)
                    other_fields[formatted_key] = str(value)
            
            if other_fields:
                self._display_key_value_pairs(other_fields)
        
        self._create_raw_response_section(response_data)
    
    def display_response(self, response_data: Dict[str, Any]):
        for widget in self.winfo_children():
            widget.destroy()
        
        self.current_row = 0
        
        photo_base64 = response_data.get('photo', '')
        
        profile_card = ctk.CTkFrame(self, corner_radius=15)
        profile_card.grid(row=self.current_row, column=0, pady=20, padx=20, sticky="ew")
        profile_card.grid_columnconfigure(1, weight=1)
        
        photo_frame = ctk.CTkFrame(profile_card, corner_radius=12, width=220, height=220)
        photo_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nw")
        photo_frame.grid_propagate(False)
        
        if photo_base64:
            try:
                photo = decode_photo(photo_base64)
                if photo:
                    photo.thumbnail((200, 200), Image.Resampling.LANCZOS)
                    self.photo_image = ImageTk.PhotoImage(photo)
                    
                    photo_label = ctk.CTkLabel(
                        photo_frame,
                        image=self.photo_image,
                        text=""
                    )
                    photo_label.place(relx=0.5, rely=0.5, anchor="center")
                else:
                    self._display_photo_placeholder_in_frame(photo_frame)
            except Exception as e:
                print(f"Error displaying photo: {e}")
                self._display_photo_placeholder_in_frame(photo_frame)
        else:
            self._display_photo_placeholder_in_frame(photo_frame)
        
        info_frame = ctk.CTkFrame(profile_card, fg_color="transparent")
        info_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        info_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            info_frame,
            text="Profile Information",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, pady=(0, 15), sticky="w")
        
        profile_fields = {}
        for key, value in sorted(response_data.items()):
            if key != 'photo' and value is not None and str(value).strip():
                formatted_key = self._format_field_name(key)
                profile_fields[formatted_key] = str(value)
        
        if profile_fields:
            row = 1
            for key, value in list(profile_fields.items())[:8]:
                field_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
                field_frame.grid(row=row, column=0, pady=8, sticky="ew")
                field_frame.grid_columnconfigure(1, weight=1)
                
                ctk.CTkLabel(
                    field_frame,
                    text=f"{key}:",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    anchor="w",
                    width=140
                ).grid(row=0, column=0, padx=(0, 10), sticky="w")
                
                value_text = str(value)
                if len(value_text) > 50:
                    value_label = ctk.CTkLabel(
                        field_frame,
                        text=value_text[:50] + "...",
                        font=ctk.CTkFont(size=12),
                        anchor="w",
                        wraplength=400
                    )
                else:
                    value_label = ctk.CTkLabel(
                        field_frame,
                        text=value_text,
                        font=ctk.CTkFont(size=12),
                        anchor="w"
                    )
                value_label.grid(row=0, column=1, sticky="w")
                row += 1
            
            if len(profile_fields) > 8:
                more_label = ctk.CTkLabel(
                    info_frame,
                    text=f"+ {len(profile_fields) - 8} more fields...",
                    font=ctk.CTkFont(size=11),
                    text_color="gray"
                )
                more_label.grid(row=row, column=0, pady=(10, 0), sticky="w")
        else:
            ctk.CTkLabel(
                info_frame,
                text="No additional data available",
                text_color="gray",
                font=ctk.CTkFont(size=12)
            ).grid(row=1, column=0, pady=10, sticky="w")
        
        self.current_row += 1
        
        if profile_fields and len(profile_fields) > 8:
            self._create_section_header("All Profile Fields")
            self._display_key_value_pairs(profile_fields)
        
        self._create_raw_response_section(response_data)
    
    def _display_photo_placeholder_in_frame(self, parent_frame):
        placeholder_label = ctk.CTkLabel(
            parent_frame,
            text="Photo\nNot Available",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def _format_field_name(self, key: str) -> str:
        import re
        key_clean = re.sub(r'_[a-z]{2,3}$', '', key)
        formatted = key_clean.replace('_', ' ')
        formatted = re.sub(r'(?<!^)(?=[A-Z])', ' ', formatted)
        words = formatted.split()
        formatted = ' '.join(word.capitalize() for word in words)
        
        replacements = {
            'First Name': 'First Name',
            'Last Name': 'Last Name',
            'Middle Name': 'Middle Name',
            'Full Name': 'Full Name',
            'Postal Code': 'Postal Code',
            'Date Of Birth': 'Date of Birth',
            'Date Of': 'Date of',
            'Email Id': 'Email',
            'Phone Number': 'Phone',
        }
        
        for old, new in replacements.items():
            formatted = formatted.replace(old, new)
        
        return formatted
    
    def _create_section_header(self, title: str):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=self.current_row, column=0, pady=(25, 15), padx=20, sticky="ew")
        
        ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        
        separator = ctk.CTkFrame(header_frame, height=2, fg_color=("#e0e0e0", "#404040"))
        separator.grid(row=1, column=0, pady=(8, 0), sticky="ew")
        separator.grid_columnconfigure(0, weight=1)
        
        self.current_row += 1
    
    def _display_key_value_pairs(self, data: Dict[str, str]):
        for key, value in data.items():
            field_card = ctk.CTkFrame(self, corner_radius=10)
            field_card.grid(row=self.current_row, column=0, pady=6, padx=20, sticky="ew")
            field_card.grid_columnconfigure(1, weight=1)
            
            key_label = ctk.CTkLabel(
                field_card,
                text=f"{key}:",
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
                width=180
            )
            key_label.grid(row=0, column=0, pady=12, padx=(15, 10), sticky="w")
            
            value_text = str(value)
            if len(value_text) > 100:
                value_textbox = ctk.CTkTextbox(
                    field_card,
                    height=min(100, max(40, (len(value_text) // 100) * 25)),
                    wrap="word",
                    font=ctk.CTkFont(size=12),
                    fg_color=("#f8f8f8", "#2a2a2a")
                )
                value_textbox.insert("1.0", value_text)
                value_textbox.configure(state="disabled")
                value_textbox.grid(row=0, column=1, pady=12, padx=(0, 15), sticky="ew")
            else:
                value_label = ctk.CTkLabel(
                    field_card,
                    text=value_text,
                    font=ctk.CTkFont(size=12),
                    anchor="w",
                    wraplength=500
                )
                value_label.grid(row=0, column=1, pady=12, padx=(0, 15), sticky="w")
            
            self.current_row += 1
    
    def _create_raw_response_section(self, data: Dict[str, Any]):
        toggle_var = ctk.BooleanVar(value=False)
        raw_text = None
        
        def toggle_raw_response():
            nonlocal raw_text
            if toggle_var.get():
                if raw_text is None:
                    raw_text = ctk.CTkTextbox(
                        self,
                        height=300,
                        font=ctk.CTkFont(family="Courier", size=11),
                        wrap="none"
                    )
                    raw_text.grid(row=self.current_row + 1, column=0, pady=10, padx=40, sticky="nsew")
                
                raw_text.delete("1.0", "end")
                json_str = json.dumps(data, indent=2)
                raw_text.insert("1.0", json_str)
                raw_text.configure(state="disabled")
            else:
                if raw_text:
                    raw_text.grid_remove()
        
        def update_button_text():
            toggle_btn.configure(text="▼ Hide Raw Response" if toggle_var.get() else "▶ Show Raw Response")
        
        toggle_btn = ctk.CTkButton(
            self,
            text="▶ Show Raw Response",
            command=lambda: [toggle_var.set(not toggle_var.get()), toggle_raw_response(), update_button_text()],
            width=180,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        toggle_btn.grid(row=self.current_row, column=0, pady=20, padx=20, sticky="w")
        self.current_row += 1
    
    def display_otp_generation_response(self, response_data: Dict[str, Any], masked_email: str = None, masked_mobile: str = None):
        for widget in self.winfo_children():
            widget.destroy()
        
        self.current_row = 0
        
        self._create_section_header("OTP Generation Result")
        
        success_card = ctk.CTkFrame(self, corner_radius=12, fg_color=("#e8f5e9", "#1a3a1a"))
        success_card.grid(row=self.current_row, column=0, pady=15, padx=20, sticky="ew")
        
        ctk.CTkLabel(
            success_card,
            text="✓ OTP sent successfully!",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#2ecc71"
        ).grid(row=0, column=0, padx=20, pady=15, sticky="w")
        self.current_row += 1
        
        if masked_email or masked_mobile:
            contact_card = ctk.CTkFrame(self, corner_radius=12)
            contact_card.grid(row=self.current_row, column=0, pady=10, padx=20, sticky="ew")
            contact_card.grid_columnconfigure(1, weight=1)
            
            row = 0
            if masked_email:
                ctk.CTkLabel(
                    contact_card,
                    text="Email:",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    anchor="w",
                    width=100
                ).grid(row=row, column=0, padx=15, pady=12, sticky="w")
                
                ctk.CTkLabel(
                    contact_card,
                    text=masked_email,
                    font=ctk.CTkFont(size=13),
                    anchor="w"
                ).grid(row=row, column=1, padx=(0, 15), pady=12, sticky="w")
                row += 1
            
            if masked_mobile:
                ctk.CTkLabel(
                    contact_card,
                    text="Mobile:",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    anchor="w",
                    width=100
                ).grid(row=row, column=0, padx=15, pady=12, sticky="w")
                
                ctk.CTkLabel(
                    contact_card,
                    text=masked_mobile,
                    font=ctk.CTkFont(size=13),
                    anchor="w"
                ).grid(row=row, column=1, padx=(0, 15), pady=12, sticky="w")
            
            self.current_row += 1
        
        if response_data:
            self._create_section_header("Response Details")
            response_fields = {}
            for key, value in sorted(response_data.items()):
                if key not in ["response", "errors"] and value is not None and str(value).strip():
                    formatted_key = self._format_field_name(key)
                    response_fields[formatted_key] = str(value)
            
            response_section = response_data.get("response", {})
            if response_section:
                for key, value in sorted(response_section.items()):
                    if key not in ["maskedEmail", "maskedMobile"] and value is not None and str(value).strip():
                        formatted_key = self._format_field_name(key)
                        response_fields[formatted_key] = str(value)
            
            if response_fields:
                self._display_key_value_pairs(response_fields)
        
        self._create_raw_response_section(response_data)
    
    def display_error(self, error_message: str):
        for widget in self.winfo_children():
            widget.destroy()
        
        self.current_row = 0
        
        error_card = ctk.CTkFrame(self, corner_radius=15, fg_color=("#ffe6e6", "#3a1a1a"))
        error_card.grid(row=self.current_row, column=0, pady=30, padx=20, sticky="ew")
        error_card.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            error_card,
            text="✗ Error",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#e74c3c"
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        error_text = ctk.CTkTextbox(
            error_card,
            height=150,
            wrap="word",
            font=ctk.CTkFont(size=12),
            fg_color=("#fff5f5", "#4a2a2a"),
            text_color="#8B0000"
        )
        error_text.insert("1.0", error_message)
        error_text.configure(state="disabled")
        error_text.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.current_row += 1
