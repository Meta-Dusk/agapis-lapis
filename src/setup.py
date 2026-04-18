import flet as ft
import inspect
from typing import TypeAlias, Optional, Callable
from functools import wraps

from components.appbar import GlobalAppBar


OptionalCallableKeyboardEvent: TypeAlias = Optional[Callable[[ft.KeyboardEvent], None]]
MOBILE_PLATFORMS = {ft.PagePlatform.ANDROID, ft.PagePlatform.IOS}
PC_PLATFORMS = {ft.PagePlatform.LINUX, ft.PagePlatform.MACOS, ft.PagePlatform.WINDOWS}

def setup_page(page: ft.Page, title: str = "Unknown") -> None:
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.title = title
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(ft.Colors.PINK_100)

def setup_main(
    title: str = "Agapis Lapis", *,
    center_page: bool = True
):
    """
    Wrapper that applies the expected configurations for all the pages.
    
    Args:
        title (str): The title of the page (Optional).
        center_page (bool): Centers page if True.
    
    Examples:
    ```
    # Simple setup example
    @setup_config()
    def main(page: ft.Page):
        page.add(ft.Text("Hello"))
        
    ft.run(main)
    ```
    """
    def decorator(page_fn: Callable[[ft.Page], None]):
        @wraps(page_fn)
        async def wrapper_fn(page: ft.Page):
            # Page configurations and stuff
            setup_page(page, title)
            page.appbar = GlobalAppBar()
            
            if page.platform in PC_PLATFORMS:
                # Centering the page only works on pc
                if center_page: await page.window.center()
                page.appbar.actions.append(
                    ft.IconButton(
                        ft.Icons.CLOSE,
                        on_click=lambda _: page.run_task(page.window.close)
                    )
                )
                page.window.title_bar_hidden = True
                current_title: str = None
                if isinstance(page.appbar.title, ft.Text):
                    current_title = page.appbar.title.value
                elif isinstance(page.appbar.title, str):
                    current_title = page.appbar.title
                if current_title:
                    page.appbar.title = ft.WindowDragArea(
                        ft.Text(current_title), expand=True, maximizable=False
                    )
            
            # This variable will store whatever page_fn returns (if anything)
            handler = None
            
            if inspect.iscoroutinefunction(page_fn):
                handler = await page_fn(page)
            else:
                handler = page_fn(page)
                
            return handler
        return wrapper_fn
    return decorator