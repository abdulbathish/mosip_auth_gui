"""Profile view component for displaying authentication results."""
import json
import customtkinter as ctk
from PIL import Image, ImageTk
from typing import Dict, Any, Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.photo_handler import decode_photo


class ProfileView(ctk.CTkScrollableFrame):
    """Profile view for displaying decrypted authentication response."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.photo_image = None
        self.photo_label = None
        self.current_row = 0
        
    def display_auth_response(self, response_data: Dict[str, Any], auth_status: bool = None, auth_token: str = None, error: str = None):
        """
        Display authentication response with status and token.
        
        Args:
            response_data: Dictionary containing response data
            auth_status: Boolean indicating authentication status
            auth_token: Authentication token string
            error: Error message if any
        """
        # Clear existing content
        for widget in self.winfo_children():
            widget.destroy()
        
        self.current_row = 0
        
        # Authentication Status Section (always shown first)
        self._create_section_header("Authentication Result")
        
        # Display auth status with color
        if auth_status is not None:
            status_frame = ctk.CTkFrame(self)
            status_frame.grid(row=self.current_row, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
            status_frame.grid_columnconfigure(1, weight=1)
            
            status_label = ctk.CTkLabel(
                status_frame,
                text="Status:",
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w",
                width=100
            )
            status_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
            
            status_text = "PASSED" if auth_status else "FAILED"
            status_color = "#2ecc71" if auth_status else "#8B0000"  # Green for pass, dark red for fail
            
            status_value = ctk.CTkLabel(
                status_frame,
                text=status_text,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=status_color
            )
            status_value.grid(row=0, column=1, padx=10, pady=10, sticky="w")
            
            self.current_row += 1
        
        # Display auth token if available
        if auth_token:
            token_frame = ctk.CTkFrame(self)
            token_frame.grid(row=self.current_row, column=0, columnspan=2, pady=5, padx=20, sticky="ew")
            token_frame.grid_columnconfigure(1, weight=1)
            
            token_label = ctk.CTkLabel(
                token_frame,
                text="Auth Token:",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w",
                width=100
            )
            token_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            token_value = ctk.CTkLabel(
                token_frame,
                text=auth_token,
                font=ctk.CTkFont(size=12, family="Courier"),
                anchor="w",
                wraplength=500
            )
            token_value.grid(row=0, column=1, padx=10, pady=5, sticky="w")
            
            self.current_row += 1
        
        # Display error if any
        if error:
            error_frame = ctk.CTkFrame(self)
            error_frame.grid(row=self.current_row, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
            
            error_label = ctk.CTkLabel(
                error_frame,
                text="Error:",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#8B0000",
                anchor="w"
            )
            error_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            error_text = ctk.CTkTextbox(
                error_frame,
                height=80,
                wrap="word",
                font=ctk.CTkFont(size=12),
                fg_color="#fff5f5",
                text_color="#8B0000"
            )
            error_text.insert("1.0", error)
            error_text.configure(state="disabled")
            error_text.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
            error_frame.grid_columnconfigure(0, weight=1)
            
            self.current_row += 1
        
        # Display response data if available
        if response_data:
            self._create_section_header("Response Details")
            
            # Extract response section if it exists
            response_section = response_data.get("response", {})
            if response_section:
                response_fields = {}
                for key, value in sorted(response_section.items()):
                    if key not in ["authStatus", "authToken"] and value is not None:
                        formatted_key = self._format_field_name(key)
                        response_fields[formatted_key] = str(value)
                
                if response_fields:
                    self._display_key_value_pairs(response_fields)
            
            # Display other top-level fields
            other_fields = {}
            for key, value in sorted(response_data.items()):
                if key not in ["response", "errors"] and value is not None and str(value).strip():
                    formatted_key = self._format_field_name(key)
                    other_fields[formatted_key] = str(value)
            
            if other_fields:
                self._display_key_value_pairs(other_fields)
        
        # Raw Response Section (Collapsible)
        self._create_raw_response_section(response_data)
    
    def display_response(self, response_data: Dict[str, Any]):
        """
        Display the decrypted response data in a profile format.
        For KYC responses with photo and profile data.
        
        Args:
            response_data: Dictionary containing decrypted response data
        """
        # Clear existing content
        for widget in self.winfo_children():
            widget.destroy()
        
        self.current_row = 0
        
        # Photo Section (always displayed - placeholder if no photo)
        photo_base64 = response_data.get('photo', '')
        if photo_base64:
            self._display_photo(photo_base64)
        else:
            self._display_photo_placeholder()
        
        # Dynamically display all other fields from response
        self._create_section_header("Profile Information")
        
        # Get all fields except photo, sorted alphabetically for consistency
        profile_fields = {}
        for key, value in sorted(response_data.items()):
            if key != 'photo' and value is not None and str(value).strip():  # Exclude photo and empty values
                # Format key name nicely
                formatted_key = self._format_field_name(key)
                profile_fields[formatted_key] = str(value)
        
        if profile_fields:
            self._display_key_value_pairs(profile_fields)
        else:
            no_data_label = ctk.CTkLabel(
                self,
                text="No additional data available",
                text_color="gray"
            )
            no_data_label.grid(row=self.current_row, column=0, columnspan=2, pady=20, padx=20)
            self.current_row += 1
        
        # Raw Response Section (Collapsible)
        self._create_raw_response_section(response_data)
    
    def _format_field_name(self, key: str) -> str:
        """Format field name from JSON key to readable format."""
        # Remove language suffixes
        key_clean = key.replace('_eng', '').replace('_ara', '').replace('_fra', '').strip()
        
        # Replace underscores with spaces
        formatted = key_clean.replace('_', ' ')
        
        # Split by camelCase if present
        import re
        formatted = re.sub(r'(?<!^)(?=[A-Z])', ' ', formatted)
        
        # Title case each word
        words = formatted.split()
        formatted = ' '.join(word.capitalize() for word in words)
        
        # Handle common patterns
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
    
    def _display_photo(self, base64_string: str):
        """Display the photo from base64 string."""
        try:
            photo = decode_photo(base64_string)
            if photo:
                # Resize photo to fit (max 200x200)
                photo.thumbnail((200, 200), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                self.photo_image = ImageTk.PhotoImage(photo)
                
                # Create label for photo
                self.photo_label = ctk.CTkLabel(
                    self,
                    image=self.photo_image,
                    text=""
                )
                self.photo_label.grid(row=self.current_row, column=0, columnspan=2, pady=20, padx=20)
                self.current_row += 1
            else:
                self._display_photo_placeholder()
        except Exception as e:
            print(f"Error displaying photo: {e}")
            self._display_photo_placeholder()
    
    def _display_photo_placeholder(self):
        """Display a placeholder when photo cannot be displayed."""
        placeholder_frame = ctk.CTkFrame(self, width=200, height=200)
        placeholder_frame.grid(row=self.current_row, column=0, columnspan=2, pady=20, padx=20)
        placeholder_frame.grid_propagate(False)
        
        placeholder_label = ctk.CTkLabel(
            placeholder_frame,
            text="Photo\nNot Available",
            font=ctk.CTkFont(size=14),
            text_color="gray",
            width=200,
            height=200
        )
        placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
        
        self.current_row += 1
    
    def _create_section_header(self, title: str):
        """Create a section header."""
        header = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header.grid(row=self.current_row, column=0, columnspan=2, pady=(20, 10), padx=20, sticky="w")
        self.current_row += 1
    
    def _display_key_value_pairs(self, data: Dict[str, str]):
        """Display key-value pairs in a formatted way."""
        for key, value in data.items():
            # Create a frame for each row to prevent overlapping
            row_frame = ctk.CTkFrame(self)
            row_frame.grid(row=self.current_row, column=0, columnspan=2, pady=5, padx=20, sticky="ew")
            row_frame.grid_columnconfigure(1, weight=1)
            
            # Key label
            key_label = ctk.CTkLabel(
                row_frame,
                text=f"{key}:",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w",
                width=150
            )
            key_label.grid(row=0, column=0, pady=5, padx=(10, 10), sticky="w")
            
            # Value label (wrap long values)
            value_text = str(value)
            if len(value_text) > 80:
                # For long values, use a textbox
                text_height = min(120, max(40, (len(value_text) // 80) * 20))
                value_textbox = ctk.CTkTextbox(
                    row_frame,
                    height=text_height,
                    wrap="word",
                    font=ctk.CTkFont(size=12)
                )
                value_textbox.insert("1.0", value_text)
                value_textbox.configure(state="disabled")
                value_textbox.grid(row=0, column=1, pady=5, padx=(10, 10), sticky="ew")
            else:
                value_label = ctk.CTkLabel(
                    row_frame,
                    text=value_text,
                    font=ctk.CTkFont(size=12),
                    anchor="w",
                    wraplength=400
                )
                value_label.grid(row=0, column=1, pady=5, padx=(10, 10), sticky="w")
            
            self.current_row += 1
    
    def _create_raw_response_section(self, data: Dict[str, Any]):
        """Create collapsible raw response section."""
        # Toggle button
        toggle_var = ctk.BooleanVar(value=False)
        raw_text = None
        
        def toggle_raw_response():
            nonlocal raw_text
            if toggle_var.get():
                if raw_text is None:
                    # Create textbox only when needed
                    raw_text = ctk.CTkTextbox(
                        self,
                        height=300,  # Larger height
                        font=ctk.CTkFont(family="Courier", size=11),
                        wrap="none"  # No wrapping for better performance
                    )
                    raw_text.grid(row=self.current_row + 1, column=0, columnspan=2, pady=10, padx=40, sticky="nsew")
                
                # Clear and insert content
                raw_text.delete("1.0", "end")
                # Insert in chunks for better performance
                json_str = json.dumps(data, indent=2)
                raw_text.insert("1.0", json_str)
                raw_text.configure(state="disabled")
            else:
                if raw_text:
                    raw_text.grid_remove()
        
        def update_button_text():
            toggle_btn.configure(text="Hide Raw Response" if toggle_var.get() else "Show Raw Response")
        
        toggle_btn = ctk.CTkButton(
            self,
            text="Show Raw Response",
            command=lambda: [toggle_var.set(not toggle_var.get()), toggle_raw_response(), update_button_text()],
            width=150
        )
        toggle_btn.grid(row=self.current_row, column=0, pady=10, padx=20, sticky="w")
        self.current_row += 1
    
    def display_otp_generation_response(self, response_data: Dict[str, Any], masked_email: str = None, masked_mobile: str = None):
        """
        Display OTP generation response.
        
        Args:
            response_data: Dictionary containing response data
            masked_email: Masked email address
            masked_mobile: Masked mobile number
        """
        # Clear existing content
        for widget in self.winfo_children():
            widget.destroy()
        
        self.current_row = 0
        
        # Success message
        self._create_section_header("OTP Generation Result")
        
        success_frame = ctk.CTkFrame(self)
        success_frame.grid(row=self.current_row, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
        
        success_label = ctk.CTkLabel(
            success_frame,
            text="OTP sent successfully!",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#2ecc71"
        )
        success_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.current_row += 1
        
        # Display masked email and mobile
        if masked_email or masked_mobile:
            contact_frame = ctk.CTkFrame(self)
            contact_frame.grid(row=self.current_row, column=0, columnspan=2, pady=5, padx=20, sticky="ew")
            contact_frame.grid_columnconfigure(1, weight=1)
            
            if masked_email:
                email_label = ctk.CTkLabel(
                    contact_frame,
                    text="Email:",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    anchor="w",
                    width=100
                )
                email_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
                
                email_value = ctk.CTkLabel(
                    contact_frame,
                    text=masked_email,
                    font=ctk.CTkFont(size=12),
                    anchor="w"
                )
                email_value.grid(row=0, column=1, padx=10, pady=5, sticky="w")
            
            if masked_mobile:
                mobile_label = ctk.CTkLabel(
                    contact_frame,
                    text="Mobile:",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    anchor="w",
                    width=100
                )
                mobile_label.grid(row=1 if masked_email else 0, column=0, padx=10, pady=5, sticky="w")
                
                mobile_value = ctk.CTkLabel(
                    contact_frame,
                    text=masked_mobile,
                    font=ctk.CTkFont(size=12),
                    anchor="w"
                )
                mobile_value.grid(row=1 if masked_email else 0, column=1, padx=10, pady=5, sticky="w")
            
            self.current_row += 1
        
        # Display other response fields
        if response_data:
            self._create_section_header("Response Details")
            
            response_fields = {}
            for key, value in sorted(response_data.items()):
                if key not in ["response", "errors"] and value is not None and str(value).strip():
                    formatted_key = self._format_field_name(key)
                    response_fields[formatted_key] = str(value)
            
            # Also include response section fields
            response_section = response_data.get("response", {})
            if response_section:
                for key, value in sorted(response_section.items()):
                    if key not in ["maskedEmail", "maskedMobile"] and value is not None and str(value).strip():
                        formatted_key = self._format_field_name(key)
                        response_fields[formatted_key] = str(value)
            
            if response_fields:
                self._display_key_value_pairs(response_fields)
        
        # Raw Response Section
        self._create_raw_response_section(response_data)
    
    def display_error(self, error_message: str):
        """Display an error message."""
        # Clear existing content
        for widget in self.winfo_children():
            widget.destroy()
        
        self.current_row = 0
        
        error_label = ctk.CTkLabel(
            self,
            text="Error",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#8B0000"
        )
        error_label.grid(row=self.current_row, column=0, columnspan=2, pady=20, padx=20)
        self.current_row += 1
        
        error_text = ctk.CTkTextbox(
            self,
            height=150,
            wrap="word",
            font=ctk.CTkFont(size=12),
            fg_color="#fff5f5",
            text_color="#8B0000"
        )
        error_text.insert("1.0", error_message)
        error_text.configure(state="disabled")
        error_text.grid(row=self.current_row, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
        self.current_row += 1
