import flet as ft
from dataclasses import dataclass

from core.test_handler import setup_test
from components.appbar import GlobalAppBar

@dataclass
class AppRoutes:
    root = "/"
    store = "/store"

@setup_test("Routes Test")
def main(page: ft.Page):
    def route_change():
        view_root = ft.View(
            route=AppRoutes.root,
            controls=[
                GlobalAppBar(),
                ft.Button(
                    "Visit Store",
                    on_click=lambda: page.run_task(
                        page.push_route, AppRoutes.store
                    ),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            padding=0, expand=True
        )
        
        page.views.clear()
        page.views.append(view_root)
        
        if page.route == AppRoutes.store:
            view_store = ft.View(
                route=AppRoutes.store,
                controls=[
                    GlobalAppBar(),
                    ft.Button(
                        "Go Home",
                        on_click=lambda: page.run_task(
                            page.push_route, AppRoutes.root
                        ),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                padding=0, expand=True
            )
            page.views.append(view_store)
        page.update()

    async def view_pop(e: ft.ViewPopEvent):
        if e.view is None: return
        print(f"View pop: {e.view}")
        page.views.remove(e.view)
        top_view = page.views[-1]
        await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    route_change()


if __name__ == "__main__":
    ft.run(main)