"""KYC authentication form with checkbox-based field selection."""
import customtkinter as ctk
from typing import Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config_loader import GUIConfig
from mosip_auth_sdk.models import DemographicsModel, IdentityInfo


class KYCForm(ctk.CTkScrollableFrame):
    """Form for KYC authentication with checkbox-based field selection."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=0)  # Checkbox column
        self.grid_columnconfigure(1, weight=0)  # Label column
        self.grid_columnconfigure(2, weight=1)  # Value column (expandable)
        self.grid_columnconfigure(3, weight=0)  # Language column
        
        # Load GUI configuration
        self.gui_config = GUIConfig()
        self.languages = self.gui_config.languages
        self.gender_options = self.gui_config.gender_options
        
        # Form fields storage
        self.fields = {}
        self._create_form_fields()
    
    def _create_field_row(self, row, field_name, label_text, field_type="text", is_list=False):
        """Create a row with checkbox, label, input field, and language selector if needed."""
        # Checkbox
        checkbox_var = ctk.BooleanVar(value=False)
        checkbox = ctk.CTkCheckBox(
            self,
            text="",
            variable=checkbox_var,
            width=30
        )
        checkbox.grid(row=row, column=0, pady=10, padx=(20, 5), sticky="w")
        
        # Label
        label = ctk.CTkLabel(self, text=label_text, anchor="w", width=180)
        label.grid(row=row, column=1, pady=10, padx=5, sticky="w")
        
        # Value input
        if field_type == "text":
            value_entry = ctk.CTkEntry(self, placeholder_text=f"Enter {label_text.lower()}")
        elif field_type == "combo":
            value_entry = ctk.CTkComboBox(
                self,
                values=self.gender_options,
                width=150
            )
            value_entry.set(self.gui_config.default_gender)
        else:
            value_entry = ctk.CTkEntry(self, placeholder_text=f"Enter {label_text.lower()}")
        
        value_entry.grid(row=row, column=2, pady=10, padx=5, sticky="ew")
        
        # Language selector (for list fields)
        lang_combo = None
        if is_list:
            lang_combo = ctk.CTkComboBox(
                self,
                values=self.languages,
                width=80
            )
            lang_combo.set("eng")
            lang_combo.grid(row=row, column=3, pady=10, padx=5, sticky="w")
        
        # Store field info
        self.fields[field_name] = {
            'checkbox': checkbox_var,
            'value': value_entry,
            'lang': lang_combo,
            'is_list': is_list,
            'field_type': field_type
        }
        
        # Disable value and lang initially
        value_entry.configure(state="disabled")
        if lang_combo:
            lang_combo.configure(state="disabled")
        
        # Enable/disable based on checkbox
        def toggle_field():
            if checkbox_var.get():
                value_entry.configure(state="normal")
                if lang_combo:
                    lang_combo.configure(state="normal")
            else:
                value_entry.configure(state="disabled")
                if lang_combo:
                    lang_combo.configure(state="disabled")
                # Clear value when disabled
                if hasattr(value_entry, 'delete'):
                    value_entry.delete(0, 'end')
        
        checkbox.configure(command=toggle_field)
    
    def _create_form_fields(self):
        """Create form fields with checkboxes."""
        row = 0
        
        # Header
        header = ctk.CTkLabel(
            self,
            text="Select fields to include in authentication:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        header.grid(row=row, column=0, columnspan=4, pady=(10, 20), padx=20, sticky="w")
        row += 1
        
        # DOB
        self._create_field_row(row, "dob", "Date of Birth (YYYY/MM/DD)", "text", False)
        row += 1
        
        # Gender
        self._create_field_row(row, "gender", "Gender", "combo", True)
        row += 1
        
        # Name
        self._create_field_row(row, "name", "Name", "text", True)
        row += 1
        
        # Age
        self._create_field_row(row, "age", "Age", "text", False)
        row += 1
        
        # Address (using fullAddress field)
        self._create_field_row(row, "full_address", "Address", "text", True)
        row += 1
        
        # Consent checkbox (always required)
        self.consent_var = ctk.BooleanVar(value=True)
        consent_checkbox = ctk.CTkCheckBox(
            self,
            text="I consent to the authentication process",
            variable=self.consent_var,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        consent_checkbox.grid(row=row, column=0, columnspan=4, pady=20, padx=20, sticky="w")
    
    def get_data(self) -> Optional[DemographicsModel]:
        """Get form data as DemographicsModel, including only checked fields."""
        try:
            demographics_data = {}
            
            # Process each field
            for field_name, field_info in self.fields.items():
                if not field_info['checkbox'].get():
                    continue  # Skip unchecked fields
                
                value_widget = field_info['value']
                value = value_widget.get().strip() if hasattr(value_widget, 'get') else ""
                
                if not value:
                    continue  # Skip empty values
                
                if field_info['is_list']:
                    # List fields need IdentityInfo
                    lang = field_info['lang'].get() if field_info['lang'] else "eng"
                    demographics_data[field_name] = [
                        IdentityInfo(language=lang, value=value)
                    ]
                else:
                    # Simple string fields
                    demographics_data[field_name] = value
            
            # Create DemographicsModel
            return DemographicsModel(**demographics_data)
            
        except Exception as e:
            print(f"Error creating DemographicsModel: {e}")
            return None
    
    def validate(self):
        """
        Validate form data.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if at least one field is selected
        has_selected_field = any(
            field_info['checkbox'].get() 
            for field_info in self.fields.values()
        )
        
        if not has_selected_field:
            return False, "Please select at least one field to authenticate"
        
        # Check if selected fields have values
        for field_name, field_info in self.fields.items():
            if field_info['checkbox'].get():
                value = field_info['value'].get().strip() if hasattr(field_info['value'], 'get') else ""
                if not value:
                    return False, f"Field '{field_name}' is selected but has no value"
        
        # Validate DOB format if selected
        if self.fields['dob']['checkbox'].get():
            dob = self.fields['dob']['value'].get().strip()
            try:
                parts = dob.split('/')
                if len(parts) != 3:
                    return False, "Date of Birth must be in format YYYY/MM/DD"
                year, month, day = map(int, parts)
                if not (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31):
                    return False, "Invalid date values"
            except ValueError:
                return False, "Date of Birth must be in format YYYY/MM/DD"
        
        # Consent is required
        if not self.consent_var.get():
            return False, "Consent is required"
        
        return True, None
