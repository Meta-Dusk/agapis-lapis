import flet as ft
from flet.controls.services.shared_preferences import SharedPreferencesValueType
from typing import Optional, Literal, TypeAlias

PrefsKeys: TypeAlias = Literal["user_name"] | str

class Preferences:
    def __init__(self):
        self.key_prefix_str = "metadusk.agapis_lapis."
    
    def prefix_key(self, key: PrefsKeys) -> str:
        return f"{self.key_prefix_str}{key}"
    
    async def get(self, key: PrefsKeys) -> Optional[SharedPreferencesValueType]:
        return await ft.SharedPreferences().get(self.prefix_key(key))
    
    async def set(self, key: PrefsKeys, value: SharedPreferencesValueType) -> bool:
        return await ft.SharedPreferences().set(self.prefix_key(key), value)
    
    async def clear(self) -> bool:
        return await ft.SharedPreferences().clear()