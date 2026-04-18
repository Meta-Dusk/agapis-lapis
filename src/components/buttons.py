import flet as ft
from typing import Optional
from dataclasses import field

@ft.control
class ToggleThemeButton(ft.IconButton):
    def init(self):
        self.on_click = self.on_toggle_theme
        self.icon = ft.Icons.DARK_MODE
        self.adaptive = True
    
    def did_mount(self):
        self.icon = (
            ft.Icons.DARK_MODE if
            self.page.theme_mode == ft.ThemeMode.DARK
            else ft.Icons.LIGHT_MODE
        )
    
    def on_toggle_theme(self, _) -> None:
        if self.page.theme_mode == ft.ThemeMode.DARK:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.icon = ft.Icons.DARK_MODE
        self.page.update()

@ft.control
class AnimatedFAB(ft.FloatingActionButton):
    icon: Optional[ft.IconDataOrControl] = ft.Icons.FAVORITE
    animate_scale: Optional[ft.AnimationValue] = field(
        default_factory=lambda: ft.Animation(200, ft.AnimationCurve.BOUNCE_IN_OUT)
    )
    is_animating: bool = False
    
    def init(self) -> None:
        self.on_click = self._emphasis
        self.on_animation_end = self._on_animation_end
    
    def _emphasis(self, e: ft.Event[ft.FloatingActionButton]) -> None:
        if self.is_animating: return
        e.control.scale = 1.2
        e.control.update()
        self.is_animating = True

    def _on_animation_end(self, e: ft.Event[ft.FloatingActionButton]) -> None:
        e.control.scale = 1.0
        e.control.update()
        self.is_animating = False