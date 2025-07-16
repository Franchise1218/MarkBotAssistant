import pandas as pd
import sqlite3
from rapidfuzz import fuzz
import os
from loginbot import get_login, list_clouds_starting

excel_file = "./MASTER DVD.xlsx"
db_file = "mark_database.db"

def refresh_sql_from_excel():
    print("🧠 Booting MARK’s brain from Excel...")
    df = pd.read_excel(excel_file)
    conn = sqlite3.connect(db_file)
    df.to_sql("mark_table", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()
    print("✅ Database loaded. MARK’s memory is sharp.")

def search_sql_data(query):
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
    conn = sqlite3.connect(db_file)
    try:
        df = pd.read_sql_query("SELECT * FROM mark_table WHERE [Disc #] = ?", conn, params=[disc_id])
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

def count_discs(keyword):
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
    conn = sqlite3.connect(db_file)
    df = pd.read_sql_query("SELECT * FROM mark_table WHERE Company = ?", conn, params=[company])
    conn.close()
    return df

def filter_by_date(event_date):
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
    print(f"🤷‍♂️ {burns[0]}")

def main():
    if not os.path.exists(db_file):
        print("⚙️ MARK needs his brain installed...")
        refresh_sql_from_excel()

    while True:
        user_input = input("\n📣 Command: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("👋 MARK shutting down. Come back when you’ve got real questions.")
            break

        elif user_input.startswith("search:"):
            query = user_input[7:].strip()
            results = search_sql_data(query)
            if results:
                for score, row in results:
                    print(f"\n🔍 Match ({score}%):\n{row.to_dict()}")
            else:
                print("🫠 Zero matches. Maybe spellcheck is your friend.")

        elif user_input.startswith("autograph:"):
            query = user_input[10:].strip()
            results = search_autograph_data(query)
            if results:
                for score, row in results:
                    print(f"\n✍️ Autograph match ({score}%):\n{row.to_dict()}")
            else:
                print("🫠 No autographs found. Maybe they bailed on the signing table.")

        elif user_input.startswith("disc:"):
            disc_id = user_input[5:].strip()
            df = get_disc(disc_id)
            print(df.to_string(index=False) if not df.empty else f"🛑 No disc found for '{disc_id}'. Maybe it's imaginary.")

        elif user_input.startswith("count:"):
            keyword = user_input[6:].strip()
            total = count_discs(keyword)
            print(f"📦 '{keyword}' appears {total} times. That’s probably more than your monthly cardio.")

        elif user_input.startswith("first disc:"):
            name = user_input[11:].strip()
            result = first_disc(name)
            print(f"🎯 First match:\n{result.to_dict() if result is not None else '🛑 Nothing. Move along, Sherlock.'}")

        elif user_input.startswith("login for:"):
            alias = user_input[10:].strip()
            creds = get_login(alias)
            print(f"🔐 Credentials incoming:\n{creds if creds else '🛑 Login not found. Try remembering where you wrote it down.'}")

        elif user_input.startswith("prefix:"):
            prefix = user_input[7:].strip()
            clouds = list_clouds_starting(prefix)
            if clouds:
                print("\n📡 Aliases matching your vibe:")
                for c in clouds:
                    print(f"• {c}")
            else:
                print("📡 No aliases found. Try a broader prefix before you start crying.")

        elif user_input.startswith("company:"):
            company = user_input[8:].strip()
            df = filter_by_company(company)
            print(df.to_string(index=False) if not df.empty else f"🛑 No events found for '{company}'. Even they forgot to show up.")

        elif user_input.startswith("date:"):
            date = user_input[5:].strip()
            df = filter_by_date(date)
            print(df.to_string(index=False) if not df.empty else f"🛑 No events for '{date}'. Maybe it's a holiday.")

        else:
            roast_unknown_command()

if __name__ == "__main__":
    main()
