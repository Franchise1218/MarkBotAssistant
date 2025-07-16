import streamlit as st
import pandas as pd
import os
from file_processor import FileProcessor
from chatbot import MarkBot
from loginbot import LoginBot

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}
if 'file_processor' not in st.session_state:
    st.session_state.file_processor = FileProcessor()
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = MarkBot()
if 'loginbot' not in st.session_state:
    st.session_state.loginbot = LoginBot()

def main():
    st.set_page_config(
        page_title="Mark-bot",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Mark-bot")
    st.markdown("Upload Excel or text files and ask questions about their content!")
    
    # Add terminal mode toggle
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🖥️ Terminal Mode"):
            st.switch_page("terminal_mark.py")
    
    # Sidebar for file management
    with st.sidebar:
        st.header("📁 File Management")
        
        # File upload section
        uploaded_files = st.file_uploader(
            "Upload Files",
            type=['xlsx', 'xls', 'txt'],
            accept_multiple_files=True,
            key="file_uploader"
        )
        
        # Special handling for credential files
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if uploaded_file.name.lower().endswith('.txt') and ('log' in uploaded_file.name.lower() or 'credential' in uploaded_file.name.lower()):
                    try:
                        # Load credential data into loginbot
                        content = uploaded_file.read().decode('utf-8')
                        st.session_state.loginbot.load_credentials_from_file(content)
                        st.success(f"🔐 Loaded {len(st.session_state.loginbot.get_all_clouds())} credentials from {uploaded_file.name}")
                        # Reset file pointer for normal processing
                        uploaded_file.seek(0)
                    except Exception as e:
                        st.error(f"Error loading credentials: {str(e)}")
        
        # Process uploaded files
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in st.session_state.uploaded_files:
                    try:
                        # Process the file
                        file_data = st.session_state.file_processor.process_file(uploaded_file)
                        st.session_state.uploaded_files[uploaded_file.name] = file_data
                        st.success(f"✅ {uploaded_file.name} uploaded successfully!")
                    except Exception as e:
                        st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
        
        # Display uploaded files
        if st.session_state.uploaded_files:
            st.subheader("📋 Uploaded Files")
            for filename, file_data in st.session_state.uploaded_files.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📄 {filename}")
                    st.caption(f"Type: {file_data['type']}")
                with col2:
                    if st.button("🗑️", key=f"delete_{filename}", help="Delete file"):
                        del st.session_state.uploaded_files[filename]
                        st.rerun()
        else:
            st.info("No files uploaded yet.")
        
        # Clear chat history button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    # Main chat interface
    st.header("💬 Chat with Mark-bot")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about your uploaded files..."):
        # Check if files are uploaded
        if not st.session_state.uploaded_files:
            st.warning("Please upload some files first!")
            return
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot.generate_response(
                    prompt, 
                    st.session_state.uploaded_files
                )
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Display instructions if no files uploaded
    if not st.session_state.uploaded_files:
        st.info("""
        👋 Welcome to Mark-bot! 
        
        To get started:
        1. Upload Excel (.xlsx, .xls) or text (.txt) files using the sidebar
        2. Ask questions about your file content
        3. I can help you with:
           - Finding specific data in Excel sheets
           - Summarizing text content
           - Analyzing data patterns
           - Extracting information from your files
        """)

if __name__ == "__main__":
    main()
