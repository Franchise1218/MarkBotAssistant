import os
import pandas as pd
import sqlite3
from rapidfuzz import fuzz

# Paths relative to the root of your project
excel_file = os.path.join(os.path.dirname(__file__), "..", "MASTER DVD.xlsx")
db_file = os.path.join(os.path.dirname(__file__), "..", "mark_database.db")

def ensure_db_ready():
    if not os.path.exists(db_file):
        refresh_sql_from_excel()

def refresh_sql_from_excel():
    print("🧠 Booting MARK’s brain from Excel...")
    df = pd.read_excel(excel_file)
    conn = sqlite3.connect(db_file)
    df.to_sql("mark_table", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()
    print("✅ Database loaded. MARK’s memory is sharp.")

def search_sql_data(query):
    ensure_db_ready()
    conn = sqlite3.connect(db_file)
    df = pd.read_sql_query("SELECT * FROM mark_table", conn)
    conn.close()
    results = []
    for _, row in df.iterrows():
        text = " ".join(map(str, row.fillna("")))
        score = fuzz.partial_ratio(query.lower(), text.lower())
        if score >= 75:
            results.append((score, row))
    results.sort(reverse=True, key=lambda x: x[0])
    return results[:10]

def search_autograph_data(query):
    try:
        df = pd.read_excel(excel_file, sheet_name="Autographs")
    except Exception:
        print("🛑 Couldn't load 'Autographs'. Maybe they're dodging fans.")
        return []
    results = []
    for _, row in df.iterrows():
        row_text = " ".join(map(str, row.fillna("")))
        score = fuzz.partial_ratio(query.lower(), row_text.lower())
        if score >= 75:
            results.append((score, row))
    results.sort(reverse=True, key=lambda x: x[0])
    return results[:10]

def get_disc(disc_id):
    ensure_db_ready()
    conn = sqlite3.connect(db_file)
    try:
        df = pd.read_sql_query("SELECT * FROM mark_table WHERE [Disc #] = ?", conn, params=[disc_id])
        if df.empty and disc_id.isdigit():
            formatted_id = f"DVD{disc_id.zfill(3)}"
            df = pd.read_sql_query("SELECT * FROM mark_table WHERE [Disc #] = ?", conn, params=[formatted_id])
        if df.empty:
            df = pd.read_sql_query("SELECT * FROM mark_table WHERE [Disc #] LIKE ?", conn, params=[f"%{disc_id}%"])
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

def count_discs(keyword):
    ensure_db_ready()
    conn = sqlite3.connect(db_file)
    df = pd.read_sql_query("SELECT * FROM mark_table", conn)
    conn.close()
    keyword = keyword.lower()
    count = sum(df[col].astype(str).str.lower().str.contains(keyword).sum() for col in df.columns)
    return count

def first_disc(name_query):
    matches = search_sql_data(name_query)
    return matches[0][1] if matches else None

def filter_by_company(company):
    ensure_db_ready()
    conn = sqlite3.connect(db_file)
    df = pd.read_sql_query("SELECT * FROM mark_table WHERE Company = ?", conn, params=[company])
    conn.close()
    return df

def filter_by_date(event_date):
    ensure_db_ready()
    conn = sqlite3.connect(db_file)
    df = pd.read_sql_query("SELECT * FROM mark_table WHERE Date = ?", conn, params=[event_date])
    conn.close()
    return df

def roast_unknown_command():
    burns = [
        "If that was a command, it’s in a dialect even I don’t speak.",
        "I’d respond... if I knew what that was.",
        "404: Brain not found. Try `search:` or something I actually support."
    ]
    return f"🤷‍♂️ {burns[0]}"
