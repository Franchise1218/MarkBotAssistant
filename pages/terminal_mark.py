import streamlit as st
import os
import sys
sys.path.append('..')
from loginbot import LoginBot
from mark_core import *  # Bring in all shared MARK functions

# 💻 UI Setup
st.set_page_config(
    page_title="Mark Terminal",
    page_icon="💻",
    layout="wide"
)

st.title("💻 Mark Terminal Interface")
st.markdown("Command-line interface for Mark.py — Enter commands as if you're in a Python terminal")

# 🔐 Initialize loginbot
if 'loginbot' not in st.session_state:
    st.session_state.loginbot = LoginBot()
    try:
        logs_file = os.path.join(os.path.dirname(__file__), "..", "LOGS.txt")
        with open(logs_file, 'r') as f:
            content = f.read()
        st.session_state.loginbot.load_credentials_from_file(content)
    except Exception as e:
        st.write(f"⚠️ Could not load credentials — {e}")

# 📂 Check for database & load if needed
ensure_db_ready()

# 📚 Command history
if 'command_history' not in st.session_state:
    st.session_state.command_history = []

# 🧭 SIDEBAR
with st.sidebar:
    st.header("🔐 Credentials")
    uploaded_logs = st.file_uploader("Passwords.txt", type=['txt'])
    if uploaded_logs:
        try:
            content = uploaded_logs.read().decode('utf-8')
            st.session_state.loginbot.load_credentials_from_file(content)
            st.success(f"Loaded {len(st.session_state.loginbot.get_all_clouds())} credentials")
        except Exception as e:
            st.error(f"Error loading credentials: {str(e)}")

    st.header("📊 Database Info")
    try:
        conn = sqlite3.connect(db_file)
        df = pd.read_sql_query("SELECT COUNT(*) as count FROM mark_table", conn)
        conn.close()
        st.write(f"Records in database: {df['count'].iloc[0]}")
    except Exception as e:
        st.error(f"🛑 Database query failed: {e}")

    st.header("🔐 Login Status")
    if st.session_state.loginbot.loaded:
        st.write(f"Credentials loaded: {len(st.session_state.loginbot.get_all_clouds())} accounts")
    else:
        st.write("No credentials loaded")

# 🎛️ Command Interface
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

# 🔍 Command Input + Execution
command = st.text_input("📣 Command:", key="command_input", placeholder="Enter command (e.g., search:matrix)")

if st.button("Execute") or command:
    if command:
        st.session_state.command_history.append(command)
        st.write(f"**> {command}**")

        # 🧠 Command Parser
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
            df = get_disc(disc_id)
            st.write(f"📊 Query returned {len(df)} rows")
            if not df.empty:
                st.dataframe(df)
                st.json(df.iloc[0].to_dict())
            else:
                st.write(f"🛑 No disc found for '{disc_id}'. Maybe it's imaginary.")

        elif command.startswith("count:"):
            keyword = command[6:].strip()
            total = count_discs(keyword)
            st.write(f"📦 '{keyword}' appears {total} times. That’s probably more than your monthly cardio.")

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
                st.write("📡 Aliases matching your vibe:")
                for c in clouds:
                    st.write(f"• {c}")
            else:
                st.write("📡 No aliases found. Try a broader prefix before you start crying.")

        elif command.startswith("company:"):
            company = command[8:].strip()
            df = filter_by_company(company)
            if not df.empty:
                st.dataframe(df)
            else:
                st.write(f"🛑 No events found for '{company}'. Even they forgot to show up.")

        elif command.startswith("date:"):
            date = command[5:].strip()
            df = filter_by_date(date)
            if not df.empty:
                st.dataframe(df)
            else:
                st.write(f"🛑 No events for '{date}'. Maybe it’s a holiday.")

        elif command.lower() == "refresh":
            refresh_sql_from_excel()
            st.success("📂 Database reloaded from Excel.")

        else:
            st.write(roast_unknown_command())
