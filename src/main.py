import flet as ft

from setup import setup_main
from app import MainApp
from core.routes import AppRoutes

@setup_main()
async def main(page: ft.Page):
    app = MainApp(page)
    
    def route_change():
        match (page.route):
            case AppRoutes.root:
                view_container.content = app.get_home_view()
            case AppRoutes.love_quotes_generator:
                view_container.content = app.get_lqg_view()
            case AppRoutes.magic_eight_ball:
                view_container.content = app.get_meb_view()
        
        page.update()
    
    view_container = ft.SafeArea(
        content=ft.AnimatedSwitcher(
            content=app.get_home_view(),
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=400, reverse_duration=200,
            switch_in_curve=ft.AnimationCurve.EASE_OUT
        ),
        expand=True, align=ft.Alignment.CENTER
    )
    
    page.on_route_change = route_change
    page.add(view_container)
    app.setup()
    route_change()
    await app.check_bday()

ft.run(main)