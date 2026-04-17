import csv, sqlite3

def convert_csv_to_sqlite():
    csv_file = "quotes.csv"
    db_file = "love_quotes.db"

    print("Creating database...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create the table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote TEXT NOT NULL,
            author TEXT
        )
    """)

    print("Reading CSV and filtering for short love quotes...")
    db_data = []
    
    with open(csv_file, "r", encoding="utf-8") as f:
        # DictReader automatically uses the first row as column names
        reader = csv.DictReader(f)
        
        for row in reader:
            quote_text = row.get("quote", "").strip()
            author_text = row.get("author", "Unknown").strip()
            tags_text = row.get("tags", row.get("category", "")).lower()
            
            if quote_text and len(quote_text) < 120:
                if "love" in tags_text:
                    db_data.append((quote_text, author_text))

    print(f"Inserting {len(db_data)} filtered quotes into SQLite...")
    # Insert everything at once for maximum speed
    cursor.executemany("INSERT INTO quotes (quote, author) VALUES (?, ?)", db_data)
    
    conn.commit()
    conn.close()
    
    print(f"Done! Your optimized {db_file} is ready.")

if __name__ == "__main__":
    convert_csv_to_sqlite()