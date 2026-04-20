import flet as ft
from datetime import datetime
from typing import Optional

from components.layouts import CenteredColumn
from components.buttons import PopDialogButton
from core.assets import Assets
from core.test_handler import setup_test

class BdayManager:
    def __init__(self, page: ft.Page):
        self.page = page
    
    def check(
        self, user_name: Optional[str],
        date: Optional[datetime] = None
    ) -> bool:
        if user_name is None: return
        user_name = user_name.lower()
        now = date if date else datetime.now()
        if (
            now.month == 4 and
            now.day == 22 and
            user_name == "isaac"
        ):
            print("[check_bday] It is Isaac's bday!")
            return True
        print("[check_bday] It is NOT yet Isaac's bday.")
        return False
    
    def show_dlg(self) -> None:
        async def open_menu(e: ft.TapEvent[ft.GestureDetector]) -> None:
            await menu.open(
                local_position=e.local_position,
                global_position=e.global_position
            )
        
        def eat_cake(e: ft.Event[ft.PopupMenuItem]) -> None:
            nonlocal cake_ok
            if not cake_ok: return
            cake_ok = False
            
            if image.src == Assets.images.redvelvet:
                image.src = Assets.images.redvelvet_sliced
                e.control.content = "Undo Cake Slice?"
                e.control.icon = ft.Icons.CAKE
            else:
                image.src = Assets.images.redvelvet
                e.control.content = "Get a Cake Slice?"
                e.control.icon = ft.Icons.CUT
            image.scale = 0.9
            image.update()
            e.control.update()
        
        def after_eating_cake(_) -> None:
            nonlocal cake_ok
            image.scale = 1
            image.update()
            cake_ok = True
        
        img_min_dim: float = self.page.width * 0.25
        cake_ok: bool = True
        
        image = ft.Image(
            Assets.images.redvelvet, fit=ft.BoxFit.COVER,
            filter_quality=ft.FilterQuality.NONE,
            width=img_min_dim, error_content=ft.Placeholder(
                width=img_min_dim, height=img_min_dim,
                color=ft.Colors.ERROR
            ),
            animate_scale=ft.Animation(300, ft.AnimationCurve.BOUNCE_IN_OUT),
            on_animation_end=after_eating_cake, gapless_playback=True
        )
        
        menu = ft.ContextMenu(
            items=[ft.PopupMenuItem("Eat cake?", ft.Icons.CAKE, on_click=eat_cake)],
            content=image
        )
        
        gesture_detector = ft.GestureDetector(content=menu, on_double_tap_down=open_menu)
        
        controls: list[ft.Control] = [
            gesture_detector,
            ft.Text(
                "This post was made by MetaDusk", size=16,
                color=ft.Colors.SECONDARY, italic=True,
                text_align=ft.TextAlign.CENTER
            )
        ]
        
        dlg = ft.AlertDialog(
            title="Happy Birthday, Isaac!",
            content=CenteredColumn(controls=controls, tight=True),
            actions=[PopDialogButton("Thanks", ft.Icons.CAKE_ROUNDED)]
        )
        self.page.show_dialog(dlg)
    
    def greet(self, user_name: Optional[str]) -> None:
        """
        Checks and shows the birthday dialog if today is the
        `user_name`'s bday. Only works for one person.
        """
        if self.check(user_name): self.show_dlg()


@setup_test("Bday Popup Test")
def test(page: ft.Page) -> None:
    bday_manager = BdayManager(page)
    bday_manager.show_dlg()

if __name__ == "__main__":
    ft.run(test, assets_dir="../assets")