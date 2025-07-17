import streamlit as st
import pandas as pd
import sqlite3
from rapidfuzz import fuzz
import os
import sys
sys.path.append('..')
from loginbot import LoginBot

# Mark.py functionality - use absolute paths from project root
excel_file = os.path.join(os.path.dirname(__file__), "..", "MASTER DVD.xlsx")
db_file = os.path.join(os.path.dirname(__file__), "..", "mark_database.db")

def refresh_sql_from_excel():
    st.write("🧠 Booting MARK's brain from Excel...")
    df = pd.read_excel(excel_file)
    conn = sqlite3.connect(db_file)
    df.to_sql("mark_table", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()
    st.write("✅ Database loaded. MARK's memory is sharp.")

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
        st.write("🛑 Couldn't load 'Autographs'. Maybe they're dodging fans.")
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
        # Try exact match first
        df = pd.read_sql_query("SELECT * FROM mark_table WHERE [Disc #] = ?", conn, params=[disc_id])
        
        # If no results and input is just a number, try DVD format
        if df.empty and disc_id.isdigit():
            formatted_id = f"DVD{disc_id.zfill(3)}"
            df = pd.read_sql_query("SELECT * FROM mark_table WHERE [Disc #] = ?", conn, params=[formatted_id])
        
        # If still no results, try partial match
        if df.empty:
            df = pd.read_sql_query("SELECT * FROM mark_table WHERE [Disc #] LIKE ?", conn, params=[f"%{disc_id}%"])
            
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
        "If that was a command, it's in a dialect even I don't speak.",
        "I'd respond... if I knew what that was.",
        "404: Brain not found. Try `search:` or something I actually support."
    ]
    return f"🤷‍♂️ {burns[0]}"

def main():
    st.set_page_config(
        page_title="Mark Terminal",
        page_icon="💻",
        layout="wide"
    )
    
    st.title("💻 Mark Terminal Interface")
    st.markdown("Command-line interface for Mark.py - Enter commands as if you're in a Python terminal")
    
    # Initialize loginbot
    if 'loginbot' not in st.session_state:
        st.session_state.loginbot = LoginBot()
    
    # Initialize database
    if not os.path.exists(db_file):
        st.write("⚙️ MARK needs his brain installed...")
        refresh_sql_from_excel()
    
    # Command history
    if 'command_history' not in st.session_state:
        st.session_state.command_history = []
    
    # Sidebar for credentials
    with st.sidebar:
        st.header("🔐 Credentials")
        uploaded_logs = st.file_uploader("Upload LOGS.txt", type=['txt'])
        if uploaded_logs:
            try:
                content = uploaded_logs.read().decode('utf-8')
                st.session_state.loginbot.load_credentials_from_file(content)
                st.success(f"Loaded {len(st.session_state.loginbot.get_all_clouds())} credentials")
            except Exception as e:
                st.error(f"Error loading credentials: {str(e)}")
        
        st.header("📊 Database Info")
        if os.path.exists(db_file):
            conn = sqlite3.connect(db_file)
            df = pd.read_sql_query("SELECT COUNT(*) as count FROM mark_table", conn)
            conn.close()
            st.write(f"Records in database: {df['count'].iloc[0]}")
        else:
            st.write("Database not initialized")
    
    # Command input
    st.write("---")
    st.write("**Available Commands:**")
    st.code("""
search:keyword          - Search for keyword in database
autograph:name          - Search autograph data
disc:ID                 - Get specific disc by ID (e.g., disc:1 or disc:DVD001)
count:keyword           - Count occurrences of keyword
first disc:name         - Get first match for name
login for:alias         - Get login credentials
prefix:text             - List aliases starting with text
company:name            - Filter by company
date:YYYY-MM-DD         - Filter by date
refresh                 - Reload database from Excel file
exit                    - Close terminal
    """)
    
    # Command input area
    command = st.text_input("📣 Command:", key="command_input", placeholder="Enter command (e.g., search:matrix)")
    
    if st.button("Execute") or command:
        if command:
            st.session_state.command_history.append(command)
            
            # Display command being executed
            st.write(f"**> {command}**")
            
            # Process command
            if command.lower() in ["exit", "quit"]:
                st.write("👋 MARK shutting down. Come back when you've got real questions.")
                
            elif command.startswith("search:"):
                query = command[7:].strip()
                results = search_sql_data(query)
                if results:
                    for score, row in results:
                        st.write(f"🔍 **Match ({score}%):**")
                        st.json(row.to_dict())
                else:
                    st.write("🫠 Zero matches. Maybe spellcheck is your friend.")
                    
            elif command.startswith("autograph:"):
                query = command[10:].strip()
                results = search_autograph_data(query)
                if results:
                    for score, row in results:
                        st.write(f"✍️ **Autograph match ({score}%):**")
                        st.json(row.to_dict())
                else:
                    st.write("🫠 No autographs found. Maybe they bailed on the signing table.")
                    
            elif command.startswith("disc:"):
                disc_id = command[5:].strip()
                st.write(f"🔍 Looking for disc: '{disc_id}'")
                df = get_disc(disc_id)
                st.write(f"📊 Query returned {len(df)} rows")
                if not df.empty:
                    st.write(f"💿 **Disc '{disc_id}':**")
                    st.dataframe(df)
                    st.json(df.iloc[0].to_dict())
                else:
                    st.write(f"🛑 No disc found for '{disc_id}'. Maybe it's imaginary.")
                    
            elif command.startswith("count:"):
                keyword = command[6:].strip()
                total = count_discs(keyword)
                st.write(f"📦 '{keyword}' appears {total} times. That's probably more than your monthly cardio.")
                
            elif command.startswith("first disc:"):
                name = command[11:].strip()
                result = first_disc(name)
                if result is not None:
                    st.write("🎯 **First match:**")
                    st.json(result.to_dict())
                else:
                    st.write("🛑 Nothing. Move along, Sherlock.")
                    
            elif command.startswith("login for:"):
                alias = command[10:].strip()
                creds = st.session_state.loginbot.get_login(alias)
                if creds:
                    st.write("🔐 **Credentials incoming:**")
                    st.code(creds)
                else:
                    st.write("🛑 Login not found. Try remembering where you wrote it down.")
                    
            elif command.startswith("prefix:"):
                prefix = command[7:].strip()
                clouds = st.session_state.loginbot.list_clouds_starting(prefix)
                if clouds:
                    st.write("📡 **Aliases matching your vibe:**")
                    for c in clouds:
                        st.write(f"• {c}")
                else:
                    st.write("📡 No aliases found. Try a broader prefix before you start crying.")
                    
            elif command.startswith("company:"):
                company = command[8:].strip()
                df = filter_by_company(company)
                if not df.empty:
                    st.write(f"🏢 **Company '{company}':**")
                    st.dataframe(df)
                else:
                    st.write(f"🛑 No events found for '{company}'. Even they forgot to show up.")
                    
            elif command.startswith("date:"):
                date = command[5:].strip()
                df = filter_by_date(date)
                if not df.empty:
                    st.write(f"📅 **Date '{date}':**")
                    st.dataframe(df)
                else:
                    st.write(f"🛑 No events for '{date}'. Maybe it's a holiday.")
                    
            elif command.lower() == "refresh":
                st.write("🔄 Refreshing database from Excel file...")
                refresh_sql_from_excel()
                st.write("✅ Database refreshed successfully!")
                    
            else:
                st.write(roast_unknown_command())
            
            st.write("---")
    
    # Command history
    if st.session_state.command_history:
        st.write("**Command History:**")
        for i, cmd in enumerate(reversed(st.session_state.command_history[-10:])):
            st.write(f"{len(st.session_state.command_history)-i}: {cmd}")

if __name__ == "__main__":
    main()