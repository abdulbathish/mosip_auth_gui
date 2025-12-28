import customtkinter as ctk
from typing import Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.config_loader import GUIConfig
from mosip_auth_sdk.models import DemographicsModel, IdentityInfo


class AuthForm(ctk.CTkScrollableFrame):
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=0)
        
        self.gui_config = GUIConfig()
        self.languages = self.gui_config.languages
        self.gender_options = self.gui_config.gender_options
        
        self.field_widgets = {}
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
        
        consent_frame = ctk.CTkFrame(self, corner_radius=8, fg_color=("#e8f5e9", "#1a3a1a"))
        consent_frame.grid(row=row, column=0, columnspan=4, pady=10, padx=15, sticky="ew")
        
        self.consent_var = ctk.BooleanVar(value=True)
        consent_checkbox = ctk.CTkCheckBox(
            consent_frame,
            text="I consent to share my demographic information for authentication",
            variable=self.consent_var,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        consent_checkbox.grid(row=0, column=0, pady=8, padx=12, sticky="w")
        row += 1
        
        self._create_field_with_checkbox("dob", "Date of Birth (YYYY/MM/DD)", ctk.CTkEntry, placeholder_text="YYYY/MM/DD", row=row)
        row += 1
        
        self._create_field_with_checkbox("gender", "Gender", ctk.CTkComboBox, values=self.gender_options, has_language=True, row=row)
        row += 1
        
        self._create_field_with_checkbox("name", "Name", ctk.CTkEntry, placeholder_text="Enter Name", has_language=True, row=row)
        row += 1
        
        self._create_field_with_checkbox("age", "Age", ctk.CTkEntry, placeholder_text="Enter Age", row=row)
        row += 1
        
        self._create_field_with_checkbox("fullAddress", "Address", ctk.CTkEntry, placeholder_text="Enter Full Address", has_language=True, row=row)
    
    def _create_field_with_checkbox(self, field_name: str, label_text: str, widget_class, has_language: bool = False, row: int = None, **kwargs):
        if row is None:
            row = len(self.field_widgets) + 1
        
        field_card = ctk.CTkFrame(self, corner_radius=8)
        field_card.grid(row=row, column=0, columnspan=4, pady=4, padx=15, sticky="ew")
        field_card.grid_columnconfigure(2, weight=1)
        
        checkbox_var = ctk.BooleanVar(value=False)
        checkbox = ctk.CTkCheckBox(field_card, text="", variable=checkbox_var, width=20)
        checkbox.grid(row=0, column=0, pady=6, padx=(10, 6), sticky="w")
        
        label = ctk.CTkLabel(
            field_card,
            text=label_text,
            anchor="w",
            width=180,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        label.grid(row=0, column=1, pady=6, padx=6, sticky="w")
        
        if widget_class == ctk.CTkComboBox:
            entry_widget = widget_class(field_card, **kwargs, font=ctk.CTkFont(size=11), height=28)
            entry_widget.set(kwargs.get("values", [""])[0] if kwargs.get("values") else "")
        else:
            entry_widget = widget_class(field_card, **kwargs, font=ctk.CTkFont(size=11), height=28)
        
        entry_widget.grid(row=0, column=2, pady=6, padx=6, sticky="ew")
        entry_widget.configure(state="disabled")
        
        lang_combo = None
        lang_var = None
        if has_language:
            lang_var = ctk.StringVar(value=self.gui_config.default_language)
            lang_combo = ctk.CTkComboBox(field_card, values=self.languages, variable=lang_var, width=80, font=ctk.CTkFont(size=10), height=28)
            lang_combo.grid(row=0, column=3, pady=6, padx=(0, 10), sticky="w")
            lang_combo.configure(state="disabled")
        
        self.field_widgets[field_name] = {
            "checkbox_var": checkbox_var,
            "entry_widget": entry_widget,
            "lang_var": lang_var,
            "lang_combo": lang_combo,
        }
        
        checkbox.configure(command=lambda: self._toggle_field_state(field_name))
    
    def _toggle_field_state(self, field_name: str):
        widgets = self.field_widgets[field_name]
        is_checked = widgets["checkbox_var"].get()
        state = "normal" if is_checked else "disabled"
        widgets["entry_widget"].configure(state=state)
        if widgets["lang_combo"]:
            widgets["lang_combo"].configure(state=state)
    
    def get_demographic_data(self) -> Optional[DemographicsModel]:
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
        if not self.consent_var.get():
            return False
        
        for widgets in self.field_widgets.values():
            if widgets["checkbox_var"].get():
                value = widgets["entry_widget"].get()
                if value:
                    return True
        
        return False
