"""Demographic authentication form with checkbox-based field selection."""
import customtkinter as ctk
from typing import Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config_loader import GUIConfig
from mosip_auth_sdk.models import DemographicsModel, IdentityInfo


class AuthForm(ctk.CTkScrollableFrame):
    """Form for demographic authentication with checkbox-based field selection."""
    
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
        self.field_widgets = {}
        self._create_form_fields()
    
    def _create_form_fields(self):
        """Create all form fields with checkboxes."""
        # Consent checkbox (always required)
        consent_frame = ctk.CTkFrame(self)
        consent_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="ew")
        
        self.consent_var = ctk.BooleanVar(value=True)
        consent_checkbox = ctk.CTkCheckBox(
            consent_frame,
            text="I consent to share my demographic information for authentication",
            variable=self.consent_var,
            font=ctk.CTkFont(weight="bold")
        )
        consent_checkbox.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # DOB
        self._create_field_with_checkbox("dob", "Date of Birth (YYYY/MM/DD)", ctk.CTkEntry, placeholder_text="YYYY/MM/DD")
        
        # Gender
        self._create_field_with_checkbox("gender", "Gender", ctk.CTkComboBox, values=self.gender_options, has_language=True)
        
        # Name
        self._create_field_with_checkbox("name", "Name", ctk.CTkEntry, placeholder_text="Enter Name", has_language=True)
        
        # Age
        self._create_field_with_checkbox("age", "Age", ctk.CTkEntry, placeholder_text="Enter Age")
        
        # Address
        self._create_field_with_checkbox("fullAddress", "Address", ctk.CTkEntry, placeholder_text="Enter Full Address", has_language=True)
    
    def _create_field_with_checkbox(self, field_name: str, label_text: str, widget_class, has_language: bool = False, **kwargs):
        """Create a field row with checkbox, input widget, and optional language selector."""
        row = len(self.field_widgets) + 1
        
        frame = ctk.CTkFrame(self)
        frame.grid(row=row, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)
        
        checkbox_var = ctk.BooleanVar(value=False)
        checkbox = ctk.CTkCheckBox(frame, text="", variable=checkbox_var, width=30)
        checkbox.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        label = ctk.CTkLabel(frame, text=label_text, anchor="w", width=180)
        label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        if widget_class == ctk.CTkComboBox:
            entry_widget = widget_class(frame, **kwargs)
            entry_widget.set(kwargs.get("values", [""])[0] if kwargs.get("values") else "")
        else:
            entry_widget = widget_class(frame, **kwargs)
        
        entry_widget.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        entry_widget.configure(state="disabled")
        
        lang_combo = None
        lang_var = None
        if has_language:
            lang_var = ctk.StringVar(value=self.gui_config.default_language)
            lang_combo = ctk.CTkComboBox(frame, values=self.languages, variable=lang_var, width=80)
            lang_combo.grid(row=0, column=3, padx=5, pady=5, sticky="e")
            lang_combo.configure(state="disabled")
        
        self.field_widgets[field_name] = {
            "checkbox_var": checkbox_var,
            "entry_widget": entry_widget,
            "lang_var": lang_var,
            "lang_combo": lang_combo,
        }
        
        checkbox.configure(command=lambda: self._toggle_field_state(field_name))
    
    def _toggle_field_state(self, field_name: str):
        """Enable/disable field based on checkbox state."""
        widgets = self.field_widgets[field_name]
        is_checked = widgets["checkbox_var"].get()
        state = "normal" if is_checked else "disabled"
        widgets["entry_widget"].configure(state=state)
        if widgets["lang_combo"]:
            widgets["lang_combo"].configure(state=state)
    
    def get_demographic_data(self) -> Optional[DemographicsModel]:
        """Get demographic data from form, only including checked fields."""
        if not self.consent_var.get():
            return None
        
        demographics_data = DemographicsModel()
        
        for field_name, widgets in self.field_widgets.items():
            if widgets["checkbox_var"].get():
                value = widgets["entry_widget"].get()
                if value:
                    if widgets["lang_var"]:
                        lang = widgets["lang_var"].get()
                        setattr(demographics_data, field_name, [IdentityInfo(language=lang, value=value)])
                    else:
                        setattr(demographics_data, field_name, value)
        
        return demographics_data
    
    def validate(self) -> bool:
        """Validate form data."""
        if not self.consent_var.get():
            return False
        
        # At least one field must be checked and filled
        for widgets in self.field_widgets.values():
            if widgets["checkbox_var"].get():
                value = widgets["entry_widget"].get()
                if value:
                    return True
        
        return False
