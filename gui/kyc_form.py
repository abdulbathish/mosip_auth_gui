import customtkinter as ctk
from typing import Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config_loader import GUIConfig
from mosip_auth_sdk.models import DemographicsModel, IdentityInfo


class KYCForm(ctk.CTkScrollableFrame):
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=0)
        
        self.gui_config = GUIConfig()
        self.languages = self.gui_config.languages
        self.gender_options = self.gui_config.gender_options
        
        self.fields = {}
        self._enable_mousewheel_scroll()
        self._create_form_fields()
    
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
    
    def _create_field_row(self, row, field_name, label_text, field_type="text", is_list=False):
        field_card = ctk.CTkFrame(self, corner_radius=8)
        field_card.grid(row=row, column=0, columnspan=4, pady=4, padx=15, sticky="ew")
        field_card.grid_columnconfigure(2, weight=1)
        
        checkbox_var = ctk.BooleanVar(value=False)
        checkbox = ctk.CTkCheckBox(
            field_card,
            text="",
            variable=checkbox_var,
            width=20
        )
        checkbox.grid(row=0, column=0, pady=6, padx=(10, 6), sticky="w")
        
        label = ctk.CTkLabel(
            field_card,
            text=label_text,
            anchor="w",
            width=180,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        label.grid(row=0, column=1, pady=6, padx=6, sticky="w")
        
        if field_type == "text":
            value_entry = ctk.CTkEntry(
                field_card,
                placeholder_text=f"Enter {label_text.lower()}",
                font=ctk.CTkFont(size=11),
                height=28
            )
        elif field_type == "combo":
            value_entry = ctk.CTkComboBox(
                field_card,
                values=self.gender_options,
                width=140,
                font=ctk.CTkFont(size=11),
                height=28
            )
            value_entry.set(self.gui_config.default_gender)
        else:
            value_entry = ctk.CTkEntry(
                field_card,
                placeholder_text=f"Enter {label_text.lower()}",
                font=ctk.CTkFont(size=11),
                height=28
            )
        
        value_entry.grid(row=0, column=2, pady=6, padx=6, sticky="ew")
        
        lang_combo = None
        if is_list:
            lang_combo = ctk.CTkComboBox(
                field_card,
                values=self.languages,
                width=80,
                font=ctk.CTkFont(size=10),
                height=28
            )
            lang_combo.set("eng")
            lang_combo.grid(row=0, column=3, pady=6, padx=(0, 10), sticky="w")
        
        self.fields[field_name] = {
            'checkbox': checkbox_var,
            'value': value_entry,
            'lang': lang_combo,
            'is_list': is_list,
            'field_type': field_type
        }
        
        value_entry.configure(state="disabled")
        if lang_combo:
            lang_combo.configure(state="disabled")
        
        def toggle_field():
            if checkbox_var.get():
                value_entry.configure(state="normal")
                if lang_combo:
                    lang_combo.configure(state="normal")
            else:
                value_entry.configure(state="disabled")
                if lang_combo:
                    lang_combo.configure(state="disabled")
                if hasattr(value_entry, 'delete'):
                    value_entry.delete(0, 'end')
        
        checkbox.configure(command=toggle_field)
    
    def _create_form_fields(self):
        row = 0
        
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=row, column=0, columnspan=4, pady=(10, 12), padx=15, sticky="ew")
        
        ctk.CTkLabel(
            header_frame,
            text="Select fields to include in authentication",
            font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        
        separator = ctk.CTkFrame(header_frame, height=2, fg_color=("#e0e0e0", "#404040"))
        separator.grid(row=1, column=0, pady=(6, 0), sticky="ew")
        separator.grid_columnconfigure(0, weight=1)
        
        row += 1
        
        self._create_field_row(row, "dob", "Date of Birth (YYYY/MM/DD)", "text", False)
        row += 1
        
        self._create_field_row(row, "gender", "Gender", "combo", True)
        row += 1
        
        self._create_field_row(row, "name", "Name", "text", True)
        row += 1
        
        self._create_field_row(row, "age", "Age", "text", False)
        row += 1
        
        self._create_field_row(row, "full_address", "Address", "text", True)
        row += 1
        
        consent_frame = ctk.CTkFrame(self, corner_radius=8, fg_color=("#e8f5e9", "#1a3a1a"))
        consent_frame.grid(row=row, column=0, columnspan=4, pady=12, padx=15, sticky="ew")
        
        self.consent_var = ctk.BooleanVar(value=True)
        consent_checkbox = ctk.CTkCheckBox(
            consent_frame,
            text="I consent to the authentication process",
            variable=self.consent_var,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        consent_checkbox.grid(row=0, column=0, pady=8, padx=12, sticky="w")
    
    def get_data(self) -> Optional[DemographicsModel]:
        try:
            demographics_data = {}
            
            for field_name, field_info in self.fields.items():
                if not field_info['checkbox'].get():
                    continue
                
                value_widget = field_info['value']
                value = value_widget.get().strip() if hasattr(value_widget, 'get') else ""
                
                if not value:
                    continue
                
                if field_info['is_list']:
                    lang = field_info['lang'].get() if field_info['lang'] else "eng"
                    demographics_data[field_name] = [
                        IdentityInfo(language=lang, value=value)
                    ]
                else:
                    demographics_data[field_name] = value
            
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
        has_selected_field = any(
            field_info['checkbox'].get() 
            for field_info in self.fields.values()
        )
        
        if not has_selected_field:
            return False, "Please select at least one field to authenticate"
        
        for field_name, field_info in self.fields.items():
            if field_info['checkbox'].get():
                value = field_info['value'].get().strip() if hasattr(field_info['value'], 'get') else ""
                if not value:
                    return False, f"Field '{field_name}' is selected but has no value"
        
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
        
        if not self.consent_var.get():
            return False, "Consent is required"
        
        return True, None
