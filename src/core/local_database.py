import os, shutil, sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class QuoteData:
    id: int
    quote: str
    author: str

@dataclass
class ProgressStats:
    seen: int
    total: int

def get_assets_dir() -> Path:
    project_root = Path(__file__).parent.parent 
    default_assets_dir = project_root / "assets"
    return Path(os.environ.get("FLET_ASSETS_DIR", str(default_assets_dir))).resolve()

def get_writable_db() -> Path:
    # Ask Flet for the official, safe mobile storage directory
    storage_env = os.environ.get("FLET_APP_STORAGE_DATA")
    
    if storage_env:
        # On Mobile (APK), put it safely inside the app's internal sandbox
        user_dir = Path(storage_env) / "agapis_lapis_data"
    else:
        # On local Desktop runs, fallback to the Windows/Mac home directory
        user_dir = Path.home() / ".agapis_lapis_data"
        
    # Add 'parents=True' to ensure it builds the whole folder tree without crashing
    user_dir.mkdir(parents=True, exist_ok=True)
    
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

def force_fresh_database() -> None:
    db_path = get_writable_db()
    
    if db_path.exists():
        os.remove(db_path)
        print("Old database deleted.")
        
    get_writable_db()
    print("Fresh database installed!")

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

def get_progress_stats() -> ProgressStats:
    db_path = get_writable_db()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(id) FROM quotes")
        total_quotes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(id) FROM quotes WHERE seen = 1")
        seen_quotes = cursor.fetchone()[0]
        
        return ProgressStats(seen_quotes, total_quotes)
    finally:
        conn.close()

def set_all_progress(value: int) -> None:
    """Sets the 'seen' value in the entire database to `value`."""
    db_path = get_writable_db() 
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"UPDATE quotes SET seen = {value}")
        conn.commit()
    finally:
        conn.close()