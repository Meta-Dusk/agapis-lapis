import flet as ft

from core.test_handler import setup_test
from components.text import DefaultText
from core.local_database import get_progress_stats, get_unseen_quote, set_all_progress

@setup_test("Database Test (Local Quotes)")
def test(page: ft.Page) -> None:
    def update_text() -> None:
        stats = get_progress_stats()
        progress_txt.value = f"Discovered: {stats.seen} / {stats.total}"
        progress_txt.update()
        
    async def fetch_quote(_) -> None:
        quote = get_unseen_quote()
        txt.value = (
            f"{quote.quote}\n— {quote.author}"
            if quote else
            f"🏆 ACHIEVEMENT UNLOCKED 🏆\nYou have read all {stats.total} quotes!"
        )
        txt.update()
        update_text()
    
    def set_progress(value: int) -> None:
        set_all_progress(value)
        update_text()
    
    txt = DefaultText("Press the heart for a love quote!")
    
    stats = get_progress_stats()
    progress_txt = DefaultText(
        f"Discovered: {stats.seen} / {stats.total}",
        size=14, color=ft.Colors.OUTLINE
    )
    
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.FAVORITE, on_click=fetch_quote
    )
    page.add(
        ft.AnimatedSwitcher(txt, duration=100, reverse_duration=100),
        progress_txt,
        ft.Row(
            controls=[
                ft.Button("Reset Stats", on_click=lambda _: set_progress(0)),
                ft.Button("Finish Stats", on_click=lambda _: set_progress(1)),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        ),
    )

if __name__ == "__main__":
    ft.run(test)