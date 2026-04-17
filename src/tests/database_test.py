import flet as ft
import os, sqlite3, shutil
from pathlib import Path
from typing import Optional
# from flet.controls.services.shared_preferences import SharedPreferencesValueType
from dataclasses import dataclass

from tests.test_handler import setup_test
from components.text import DefaultText

@dataclass
class QuoteData:
    id: int
    quote: str
    author: str

def get_assets_dir() -> Path:
    project_root = Path(__file__).parent.parent 
    default_assets_dir = project_root / "assets"
    return Path(os.environ.get("FLET_ASSETS_DIR", str(default_assets_dir))).resolve()

def get_writable_db() -> Path:
    # Create a hidden, writable folder in the user's OS directory
    user_dir = Path.home() / ".agapis_lapis_data"
    user_dir.mkdir(exist_ok=True)
    
    writable_db = user_dir / "love_quotes.db"
    
    if not writable_db.exists():
        print("First boot detected! Copying database to writable storage...")
        read_only_db = get_assets_dir() / "data" / "love_quotes.db"
        shutil.copy2(read_only_db, writable_db)
        
        conn = sqlite3.connect(writable_db)
        conn.execute("ALTER TABLE quotes ADD COLUMN seen INTEGER DEFAULT 0")
        conn.commit()
        conn.close()
        
    return writable_db

def get_unseen_quote() -> Optional[QuoteData]:
    db_path = get_writable_db()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Ask SQLite for 1 random quote where seen is 0 (False)
        cursor.execute("SELECT id, quote, author FROM quotes WHERE seen = 0 ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            quote_id, quote, author = result
            
            # Immediately update this specific row so it is never seen again
            cursor.execute("UPDATE quotes SET seen = 1 WHERE id = ?", (quote_id,))
            conn.commit()
            
            return QuoteData(quote_id, quote, author)
        else:
            return None # They have seen all 250,000!
    finally:
        conn.close()

def get_progress_stats() -> tuple[int, int]:
    db_path = get_writable_db()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(id) FROM quotes")
        total_quotes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(id) FROM quotes WHERE seen = 1")
        seen_quotes = cursor.fetchone()[0]
        
        return seen_quotes, total_quotes
    finally:
        conn.close()

@setup_test("Database Test (Local Quotes)")
def test(page: ft.Page) -> None:
    async def fetch_quote(_) -> None:
        quote = get_unseen_quote()
        seen, total = get_progress_stats()
        
        if quote:
            txt.value = f"{quote.quote}\n— {quote.author}"
        else:
            txt.value = f"🏆 ACHIEVEMENT UNLOCKED 🏆\nYou have read all {total} quotes!"
        
        txt.update()
        progress_txt.value = f"Discovered: {seen} / {total}"
        progress_txt.update()
    
    txt = DefaultText("Press the heart for a love quote!")
    progress_txt = DefaultText("", size=14, color=ft.Colors.OUTLINE)
    
    initial_seen, intial_total = get_progress_stats()
    progress_txt.value = f"Discovered: {initial_seen} / {intial_total}"
    
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.FAVORITE, on_click=fetch_quote
    )
    page.add(
        ft.AnimatedSwitcher(txt, duration=100, reverse_duration=100),
        progress_txt
    )

if __name__ == "__main__":
    ft.run(test)