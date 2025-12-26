import os
from pathlib import Path
from dynaconf import Dynaconf
from typing import List


class GUIConfig:
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GUIConfig, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        if self._config is None:
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "config.toml"
            
            original_cwd = os.getcwd()
            try:
                os.chdir(project_root / "config")
                self._config = Dynaconf(
                    settings_files=[str(config_path.name)],
                    environments=False,
                )
            finally:
                os.chdir(original_cwd)
    
    @property
    def id_types(self) -> List[str]:
        return self._config.get("gui.id_types", ["UIN", "VID"])
    
    @property
    def gender_options(self) -> List[str]:
        return self._config.get("gui.gender_options", ["Male", "Female", "Other"])
    
    @property
    def languages(self) -> List[str]:
        return self._config.get("gui.languages", ["eng", "ara", "fra"])
    
    @property
    def default_id_type(self) -> str:
        id_types = self.id_types
        return id_types[0] if id_types else "UIN"
    
    @property
    def default_gender(self) -> str:
        genders = self.gender_options
        return genders[0] if genders else "Male"
    
    @property
    def default_language(self) -> str:
        languages = self.languages
        return languages[0] if languages else "eng"
