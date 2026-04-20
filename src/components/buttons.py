import flet as ft
import asyncio, inspect
from typing import Optional, Callable
from dataclasses import field

@ft.control
class ToggleThemeButton(ft.IconButton):
    icon: Optional[ft.IconDataOrControl] = ft.Icons.DARK_MODE
    adaptive: Optional[bool] = True
    tooltip: Optional[ft.TooltipValue] = "Press to toggle the theme!"
    
    def init(self):
        self.on_click = self.on_toggle_theme
    
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
        if self.on_click is None:
            self.on_click = self.emphasis
        self.on_animation_end = self._on_animation_end
    
    def emphasis(self, e: ft.Event[ft.FloatingActionButton]) -> None:
        if self.is_animating: return
        e.control.scale = 1.2
        e.control.update()
        self.is_animating = True

    def _on_animation_end(self, e: ft.Event[ft.FloatingActionButton]) -> None:
        e.control.scale = 1.0
        e.control.update()
        self.is_animating = False

@ft.control
class PopDialogButton(ft.Button):
    """Calls `page.pop_dialog()` when clicked."""
    def init(self):
        self.on_click = lambda e: e.page.pop_dialog()

class AnimatedCopyButton(ft.IconButton):
    def __init__(
        self, *,
        get_text_callback: Callable[[], str],
        on_copy_callback: Callable[[str], None]
    ):
        super().__init__()
        self.get_text_callback = get_text_callback
        self.on_copy_callback = on_copy_callback
        self.recently_pressed = False
        
        self.icon = ft.Icons.COPY_ALL_ROUNDED
        self.icon_color = ft.Colors.OUTLINE
        self.tooltip = "Copy to clipboard"
        self.on_click = self.handle_copy

    async def handle_copy(self, _) -> None:
        if self.recently_pressed: return
        
        text = self.get_text_callback()
        if (
            text is None or
            text.startswith("Press") or
            text.startswith("Awaiting") or
            text.startswith("Loading") or
            text.startswith("Error")
        ):
            return
        
        self.recently_pressed = True
        print(f"Copying text to clipboard: {text}")
        
        if self.on_copy_callback:
            if inspect.iscoroutinefunction(self.on_copy_callback):
                await self.on_copy_callback(text)
            else:
                self.on_copy_callback(text)
        
        self.icon = ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED
        self.icon_color = ft.Colors.GREEN_400
        self.update()
        
        await asyncio.sleep(2)
        self.icon = ft.Icons.COPY_ALL_OUTLINED
        self.icon_color = ft.Colors.OUTLINE
        self.update()
        self.recently_pressed = False