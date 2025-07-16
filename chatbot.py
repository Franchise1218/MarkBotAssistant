import re
import pandas as pd
from typing import Dict, Any, List
from file_processor import FileProcessor
from rapidfuzz import fuzz
from loginbot import LoginBot

class MarkBot:
    """Main chatbot class for handling user queries about uploaded files"""
    
    def __init__(self):
        self.file_processor = FileProcessor()
        self.conversation_context = []
        self.loginbot = LoginBot()
    
    def generate_response(self, user_query: str, uploaded_files: Dict[str, Any]) -> str:
        """
        Generate response to user query based on uploaded files
        
        Args:
            user_query: User's question
            uploaded_files: Dictionary of processed file data
            
        Returns:
            Bot response string
        """
        try:
            # Analyze the query to determine intent
            intent = self._analyze_query_intent(user_query)
            
            # Generate response based on intent
            response = self._generate_response_by_intent(intent, user_query, uploaded_files)
            
            return response
            
        except Exception as e:
            return f"Sorry, I encountered an error processing your query: {str(e)}"
    
    def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze user query to determine intent and extract key information"""
        query_lower = query.lower()
        
        intent = {
            'type': 'general',
            'action': None,
            'target': None,
            'keywords': []
        }
        
        # Extract keywords
        intent['keywords'] = [word for word in query_lower.split() if len(word) > 2]
        
        # Check for special Mark-bot commands (inspired by original Mark.py)
        if query.startswith('search:'):
            intent['type'] = 'search'
            intent['target'] = {'type': 'search_command', 'value': query[7:].strip()}
        elif query.startswith('count:'):
            intent['type'] = 'count'
            intent['target'] = {'type': 'count_command', 'value': query[6:].strip()}
        elif query.startswith('first disc:'):
            intent['type'] = 'first_disc'
            intent['target'] = {'type': 'first_disc_command', 'value': query[11:].strip()}
        elif query.startswith('disc:'):
            intent['type'] = 'disc'
            intent['target'] = {'type': 'disc_command', 'value': query[5:].strip()}
        elif query.startswith('autograph:'):
            intent['type'] = 'autograph'
            intent['target'] = {'type': 'autograph_command', 'value': query[10:].strip()}
        elif query.startswith('login for:'):
            intent['type'] = 'login'
            intent['target'] = {'type': 'login_command', 'value': query[10:].strip()}
        elif query.startswith('prefix:'):
            intent['type'] = 'prefix'
            intent['target'] = {'type': 'prefix_command', 'value': query[7:].strip()}
        # Determine intent type for natural language queries
        elif any(word in query_lower for word in ['show', 'display', 'what', 'tell me about']):
            intent['type'] = 'show'
        elif any(word in query_lower for word in ['find', 'search', 'look for']):
            intent['type'] = 'search'
        elif any(word in query_lower for word in ['count', 'how many']):
            intent['type'] = 'count'
        elif any(word in query_lower for word in ['summary', 'summarize', 'overview']):
            intent['type'] = 'summary'
        elif any(word in query_lower for word in ['column', 'columns']):
            intent['type'] = 'column_info'
        elif any(word in query_lower for word in ['row', 'rows']):
            intent['type'] = 'row_info'
        elif any(word in query_lower for word in ['sheet', 'sheets']):
            intent['type'] = 'sheet_info'
        elif any(word in query_lower for word in ['help', 'what can you do']):
            intent['type'] = 'help'
        
        # Extract specific targets
        if 'row' in query_lower:
            row_match = re.search(r'row\s+(\d+)', query_lower)
            if row_match:
                intent['target'] = {'type': 'row', 'value': int(row_match.group(1))}
        
        if 'column' in query_lower:
            col_match = re.search(r'column\s+(\w+)', query_lower)
            if col_match:
                intent['target'] = {'type': 'column', 'value': col_match.group(1)}
        
        return intent
    
    def _generate_response_by_intent(self, intent: Dict[str, Any], query: str, uploaded_files: Dict[str, Any]) -> str:
        """Generate response based on analyzed intent"""
        
        if intent['type'] == 'help':
            return self._generate_help_response()
        
        if intent['type'] == 'summary':
            return self._generate_summary_response(uploaded_files)
        
        if intent['type'] == 'search':
            if intent['target'] and intent['target']['type'] == 'search_command':
                return self._handle_search_command(intent, uploaded_files)
            return self._generate_search_response(query, uploaded_files)
        
        if intent['type'] == 'show':
            return self._generate_show_response(intent, uploaded_files)
        
        if intent['type'] == 'count':
            if intent['target'] and intent['target']['type'] == 'count_command':
                return self._handle_count_command(intent, uploaded_files)
            return self._generate_count_response(uploaded_files)
        
        if intent['type'] == 'column_info':
            return self._generate_column_info_response(uploaded_files)
        
        if intent['type'] == 'sheet_info':
            return self._generate_sheet_info_response(uploaded_files)
        
        if intent['type'] == 'row_info':
            return self._generate_row_info_response(intent, uploaded_files)
        
        # Handle special Mark-bot commands
        if intent['type'] == 'first_disc':
            return self._handle_first_disc_command(intent, uploaded_files)
        
        if intent['type'] == 'disc':
            return self._handle_disc_command(intent, uploaded_files)
        
        if intent['type'] == 'autograph':
            return self._handle_autograph_command(intent, uploaded_files)
        
        if intent['type'] == 'login':
            return self._handle_login_command(intent, uploaded_files)
        
        if intent['type'] == 'prefix':
            return self._handle_prefix_command(intent, uploaded_files)
        
        # Default response for general queries
        return self._generate_general_response(query, uploaded_files)
    
    def _generate_help_response(self) -> str:
        """Generate help response"""
        return """
🤖 **Mark-bot Help**

I can help you analyze your uploaded files! Here's what I can do:

**For Excel files:**
- Show me the data in sheet X
- What columns are in this file?
- How many rows are there?
- Show me row 5
- Find all data containing "keyword"
- Summarize the Excel file

**For Text files:**
- Summarize the text
- Find "keyword" in the text
- How many words/lines are there?
- Show me lines containing "keyword"

**Special Mark-bot commands:**
- `search:keyword` - Advanced fuzzy search with scores
- `count:keyword` - Count occurrences of keyword
- `first disc:name` - Find first match for disc name
- `disc:ID` - Find specific disc by ID
- `autograph:name` - Search in autograph sheets
- `login for:alias` - Get login credentials for alias
- `prefix:text` - List all aliases starting with text

**General commands:**
- Show me all uploaded files
- What's in my files?
- Help or what can you do?

Just ask me naturally about your files or use the special commands!
        """
    
    def _generate_summary_response(self, uploaded_files: Dict[str, Any]) -> str:
        """Generate summary of all uploaded files"""
        if not uploaded_files:
            return "No files uploaded yet. Please upload some files first!"
        
        response = "📊 **File Summary**\n\n"
        
        for filename, file_data in uploaded_files.items():
            response += f"**{filename}**\n"
            
            if file_data['type'] == 'excel':
                summary = file_data['summary']
                response += f"- Type: Excel file\n"
                response += f"- Sheets: {summary['total_sheets']} ({', '.join(summary['sheet_names'])})\n"
                response += f"- Total rows: {summary['total_rows']}\n"
                response += f"- Total columns: {summary['total_columns']}\n\n"
                
                # Show sheet details
                for sheet_name, sheet_data in file_data['sheets'].items():
                    response += f"  **Sheet: {sheet_name}**\n"
                    response += f"  - Dimensions: {sheet_data['shape'][0]} rows × {sheet_data['shape'][1]} columns\n"
                    response += f"  - Columns: {', '.join(sheet_data['columns'][:5])}"
                    if len(sheet_data['columns']) > 5:
                        response += f" ... ({len(sheet_data['columns'])} total)"
                    response += "\n\n"
            
            elif file_data['type'] == 'text':
                response += f"- Type: Text file\n"
                response += f"- Lines: {file_data['line_count']}\n"
                response += f"- Words: {file_data['word_count']}\n"
                response += f"- Characters: {file_data['char_count']}\n"
                
                if file_data['summary']['top_words']:
                    top_words = [f"{word} ({count})" for word, count in file_data['summary']['top_words'][:5]]
                    response += f"- Top words: {', '.join(top_words)}\n"
                response += "\n"
        
        return response
    
    def _generate_search_response(self, query: str, uploaded_files: Dict[str, Any]) -> str:
        """Generate search response"""
        # Extract search terms from query
        search_terms = self._extract_search_terms(query)
        
        if not search_terms:
            return "I couldn't identify what to search for. Please specify what you're looking for."
        
        response = f"🔍 **Search results for: {', '.join(search_terms)}**\n\n"
        found_results = False
        
        for filename, file_data in uploaded_files.items():
            file_results = []
            
            for term in search_terms:
                results = self.file_processor.search_in_file(term, file_data)
                file_results.extend(results)
            
            if file_results:
                found_results = True
                response += f"**{filename}:**\n"
                
                for result in file_results:
                    response += f"- {result['description']}\n"
                    
                    if result['type'] == 'fuzzy_match' and len(result['matches']) <= 5:
                        for score, match in result['matches']:
                            response += f"  - Match ({score}%): {match}\n"
                    elif result['type'] == 'fuzzy_text_match' and len(result['matches']) <= 5:
                        for match in result['matches']:
                            response += f"  - Line {match['line_number']} ({match['score']}%): {match['content']}\n"
                    elif result['type'] == 'column_match':
                        for col, score in zip(result['columns'], result.get('scores', [])):
                            response += f"  - Column: {col} ({score}%)\n"
                
                response += "\n"
        
        if not found_results:
            response += "No results found for your search terms."
        
        return response
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract search terms from query"""
        # Look for quoted terms first
        quoted_terms = re.findall(r'"([^"]*)"', query)
        
        # If no quoted terms, look for common search patterns
        if not quoted_terms:
            patterns = [
                r'find\s+(.+?)(?:\s+in|\s+from|$)',
                r'search\s+(?:for\s+)?(.+?)(?:\s+in|\s+from|$)',
                r'look\s+for\s+(.+?)(?:\s+in|\s+from|$)',
                r'containing\s+(.+?)(?:\s+in|\s+from|$)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, query.lower())
                if match:
                    return [match.group(1).strip()]
        
        return quoted_terms
    
    def _generate_show_response(self, intent: Dict[str, Any], uploaded_files: Dict[str, Any]) -> str:
        """Generate show response"""
        if intent['target'] and intent['target']['type'] == 'row':
            return self._show_specific_row(intent['target']['value'], uploaded_files)
        
        # Default show response - show file contents
        response = "📋 **File Contents**\n\n"
        
        for filename, file_data in uploaded_files.items():
            response += f"**{filename}**\n"
            
            if file_data['type'] == 'excel':
                for sheet_name, sheet_data in file_data['sheets'].items():
                    response += f"\n**Sheet: {sheet_name}**\n"
                    df = sheet_data['data']
                    
                    # Show first few rows
                    if len(df) > 0:
                        response += f"Columns: {', '.join(df.columns.tolist())}\n\n"
                        response += "First 5 rows:\n"
                        
                        for i, row in df.head().iterrows():
                            response += f"Row {i+1}: {dict(row)}\n"
                    else:
                        response += "Empty sheet\n"
            
            elif file_data['type'] == 'text':
                lines = file_data['lines'][:10]  # Show first 10 lines
                response += f"First {len(lines)} lines:\n"
                for i, line in enumerate(lines, 1):
                    response += f"{i}: {line}\n"
                
                if len(file_data['lines']) > 10:
                    response += f"... ({len(file_data['lines']) - 10} more lines)\n"
            
            response += "\n"
        
        return response
    
    def _show_specific_row(self, row_number: int, uploaded_files: Dict[str, Any]) -> str:
        """Show specific row from Excel files"""
        response = f"📊 **Row {row_number}**\n\n"
        found_data = False
        
        for filename, file_data in uploaded_files.items():
            if file_data['type'] == 'excel':
                for sheet_name, sheet_data in file_data['sheets'].items():
                    df = sheet_data['data']
                    
                    if row_number <= len(df):
                        row_data = df.iloc[row_number - 1]
                        response += f"**{filename} - Sheet: {sheet_name}**\n"
                        
                        for col, value in row_data.items():
                            response += f"- {col}: {value}\n"
                        
                        response += "\n"
                        found_data = True
        
        if not found_data:
            response += f"Row {row_number} not found in any Excel files."
        
        return response
    
    def _generate_count_response(self, uploaded_files: Dict[str, Any]) -> str:
        """Generate count response"""
        response = "🔢 **File Statistics**\n\n"
        
        for filename, file_data in uploaded_files.items():
            response += f"**{filename}**\n"
            
            if file_data['type'] == 'excel':
                summary = file_data['summary']
                response += f"- Total sheets: {summary['total_sheets']}\n"
                response += f"- Total rows: {summary['total_rows']}\n"
                response += f"- Total columns: {summary['total_columns']}\n"
                
                for sheet_name, sheet_data in file_data['sheets'].items():
                    response += f"  - {sheet_name}: {sheet_data['shape'][0]} rows × {sheet_data['shape'][1]} columns\n"
            
            elif file_data['type'] == 'text':
                response += f"- Lines: {file_data['line_count']}\n"
                response += f"- Words: {file_data['word_count']}\n"
                response += f"- Characters: {file_data['char_count']}\n"
            
            response += "\n"
        
        return response
    
    def _generate_column_info_response(self, uploaded_files: Dict[str, Any]) -> str:
        """Generate column information response"""
        response = "📊 **Column Information**\n\n"
        found_excel = False
        
        for filename, file_data in uploaded_files.items():
            if file_data['type'] == 'excel':
                found_excel = True
                response += f"**{filename}**\n"
                
                for sheet_name, sheet_data in file_data['sheets'].items():
                    response += f"\n**Sheet: {sheet_name}**\n"
                    columns = sheet_data['columns']
                    dtypes = sheet_data['dtypes']
                    
                    for col in columns:
                        response += f"- {col} ({dtypes[col]})\n"
                
                response += "\n"
        
        if not found_excel:
            response += "No Excel files found. Column information is only available for Excel files."
        
        return response
    
    def _generate_sheet_info_response(self, uploaded_files: Dict[str, Any]) -> str:
        """Generate sheet information response"""
        response = "📋 **Sheet Information**\n\n"
        found_excel = False
        
        for filename, file_data in uploaded_files.items():
            if file_data['type'] == 'excel':
                found_excel = True
                response += f"**{filename}**\n"
                
                for sheet_name, sheet_data in file_data['sheets'].items():
                    response += f"- **{sheet_name}**: {sheet_data['shape'][0]} rows × {sheet_data['shape'][1]} columns\n"
                    response += f"  Columns: {', '.join(sheet_data['columns'])}\n"
                
                response += "\n"
        
        if not found_excel:
            response += "No Excel files found. Sheet information is only available for Excel files."
        
        return response
    
    def _generate_row_info_response(self, intent: Dict[str, Any], uploaded_files: Dict[str, Any]) -> str:
        """Generate row information response"""
        if intent['target'] and intent['target']['type'] == 'row':
            return self._show_specific_row(intent['target']['value'], uploaded_files)
        
        # General row information
        response = "📊 **Row Information**\n\n"
        
        for filename, file_data in uploaded_files.items():
            if file_data['type'] == 'excel':
                response += f"**{filename}**\n"
                
                for sheet_name, sheet_data in file_data['sheets'].items():
                    response += f"- {sheet_name}: {sheet_data['shape'][0]} rows\n"
                
                response += "\n"
        
        return response
    
    def _generate_general_response(self, query: str, uploaded_files: Dict[str, Any]) -> str:
        """Generate general response for unrecognized queries"""
        # Try to find relevant information based on keywords
        keywords = [word.lower() for word in query.split() if len(word) > 3]
        
        if not keywords:
            return "I'm not sure what you're asking about. Try asking about your files or type 'help' for available commands."
        
        # Search for keywords in files
        response = f"🔍 I found some information related to your query:\n\n"
        found_something = False
        
        for keyword in keywords:
            for filename, file_data in uploaded_files.items():
                results = self.file_processor.search_in_file(keyword, file_data)
                
                if results:
                    found_something = True
                    response += f"**{filename}** (searching for '{keyword}'):\n"
                    
                    for result in results[:3]:  # Limit to top 3 results
                        response += f"- {result['description']}\n"
                    
                    response += "\n"
        
        if not found_something:
            response = "I couldn't find specific information for your query. You can ask me to:\n"
            response += "- Show file contents\n"
            response += "- Search for specific terms\n"
            response += "- Provide file summaries\n"
            response += "- Show column/row information\n"
            response += "- Type 'help' for more options"
        
        return response
    
    def _handle_first_disc_command(self, intent: Dict[str, Any], uploaded_files: Dict[str, Any]) -> str:
        """Handle first disc command - find the first match for a query"""
        query = intent['target']['value']
        
        for filename, file_data in uploaded_files.items():
            if file_data['type'] == 'excel':
                results = self.file_processor.search_in_file(query, file_data)
                
                if results:
                    for result in results:
                        if result['type'] == 'fuzzy_match' and result['matches']:
                            first_match = result['matches'][0]
                            score, match_data = first_match
                            
                            response = f"🎯 **First disc match for '{query}':**\n\n"
                            response += f"**File:** {filename}\n"
                            response += f"**Sheet:** {result['sheet']}\n"
                            response += f"**Match Score:** {score}%\n\n"
                            
                            for key, value in match_data.items():
                                response += f"- **{key}:** {value}\n"
                            
                            return response
        
        return f"🛑 No disc found for '{query}'. Maybe it's imaginary."
    
    def _handle_disc_command(self, intent: Dict[str, Any], uploaded_files: Dict[str, Any]) -> str:
        """Handle disc command - find specific disc by ID"""
        disc_id = intent['target']['value']
        
        for filename, file_data in uploaded_files.items():
            if file_data['type'] == 'excel':
                for sheet_name, sheet_data in file_data['sheets'].items():
                    df = sheet_data['data']
                    
                    # Look for disc ID in common column names
                    disc_columns = [col for col in df.columns if 'disc' in col.lower() or 'id' in col.lower()]
                    
                    for col in disc_columns:
                        matches = df[df[col].astype(str).str.contains(disc_id, case=False, na=False)]
                        
                        if not matches.empty:
                            response = f"💿 **Disc '{disc_id}' found:**\n\n"
                            response += f"**File:** {filename}\n"
                            response += f"**Sheet:** {sheet_name}\n\n"
                            
                            for _, row in matches.iterrows():
                                for key, value in row.items():
                                    response += f"- **{key}:** {value}\n"
                                response += "\n"
                            
                            return response
        
        return f"🛑 No disc found for '{disc_id}'. Maybe it's imaginary."
    
    def _handle_autograph_command(self, intent: Dict[str, Any], uploaded_files: Dict[str, Any]) -> str:
        """Handle autograph command - search in autograph-related sheets"""
        query = intent['target']['value']
        
        for filename, file_data in uploaded_files.items():
            if file_data['type'] == 'excel':
                # Look for autograph-related sheets
                autograph_sheets = [name for name in file_data['sheets'].keys() 
                                  if 'autograph' in name.lower() or 'signature' in name.lower()]
                
                if autograph_sheets:
                    response = f"✍️ **Autograph search results for '{query}':**\n\n"
                    found_matches = False
                    
                    for sheet_name in autograph_sheets:
                        sheet_data = file_data['sheets'][sheet_name]
                        df = sheet_data['data']
                        
                        # Search in autograph sheet
                        fuzzy_matches = []
                        for _, row in df.iterrows():
                            row_text = " ".join(map(str, row.fillna("")))
                            score = fuzz.partial_ratio(query.lower(), row_text.lower())
                            if score >= 75:
                                fuzzy_matches.append((score, row))
                        
                        if fuzzy_matches:
                            found_matches = True
                            fuzzy_matches.sort(reverse=True, key=lambda x: x[0])
                            
                            response += f"**Sheet: {sheet_name}**\n"
                            
                            for score, row in fuzzy_matches[:5]:  # Top 5 matches
                                response += f"- Match ({score}%):\n"
                                for key, value in row.items():
                                    response += f"  - **{key}:** {value}\n"
                                response += "\n"
                    
                    if not found_matches:
                        response += "🫠 No autographs found. Maybe they bailed on the signing table."
                    
                    return response
                else:
                    # Search in all sheets if no autograph-specific sheet found
                    results = self.file_processor.search_in_file(query, file_data)
                    if results:
                        response = f"✍️ **Autograph search results for '{query}' (searched all sheets):**\n\n"
                        
                        for result in results:
                            if result['type'] == 'fuzzy_match' and result['matches']:
                                response += f"**Sheet: {result['sheet']}**\n"
                                for score, match_data in result['matches'][:3]:
                                    response += f"- Match ({score}%):\n"
                                    for key, value in match_data.items():
                                        response += f"  - **{key}:** {value}\n"
                                    response += "\n"
                        
                        return response
        
        return f"🫠 No autographs found for '{query}'. Maybe they're dodging fans."
    
    def _handle_search_command(self, intent: Dict[str, Any], uploaded_files: Dict[str, Any]) -> str:
        """Handle search command with enhanced fuzzy search"""
        query = intent['target']['value']
        
        response = f"🔍 **Enhanced search results for: {query}**\n\n"
        found_results = False
        
        for filename, file_data in uploaded_files.items():
            results = self.file_processor.search_in_file(query, file_data)
            
            if results:
                found_results = True
                response += f"**{filename}:**\n"
                
                for result in results:
                    response += f"- {result['description']}\n"
                    
                    if result['type'] == 'fuzzy_match':
                        for score, match_data in result['matches'][:10]:
                            response += f"  - Match ({score}%):\n"
                            for key, value in match_data.items():
                                response += f"    - **{key}:** {value}\n"
                            response += "\n"
                    
                    elif result['type'] == 'fuzzy_text_match':
                        for match in result['matches'][:10]:
                            response += f"  - Line {match['line_number']} ({match['score']}%): {match['content']}\n"
                
                response += "\n"
        
        if not found_results:
            response += "🫠 Zero matches. Maybe spellcheck is your friend."
        
        return response
    
    def _handle_count_command(self, intent: Dict[str, Any], uploaded_files: Dict[str, Any]) -> str:
        """Handle count command for keyword occurrences"""
        keyword = intent['target']['value']
        
        response = f"📦 **Count results for '{keyword}':**\n\n"
        total_count = 0
        
        for filename, file_data in uploaded_files.items():
            file_count = 0
            
            if file_data['type'] == 'excel':
                for sheet_name, sheet_data in file_data['sheets'].items():
                    df = sheet_data['data']
                    
                    # Count in each column
                    for col in df.columns:
                        col_count = df[col].astype(str).str.lower().str.contains(keyword.lower(), na=False).sum()
                        file_count += col_count
            
            elif file_data['type'] == 'text':
                content = file_data['content'].lower()
                file_count = content.count(keyword.lower())
            
            if file_count > 0:
                response += f"**{filename}:** {file_count} occurrences\n"
                total_count += file_count
        
        response += f"\n**Total:** '{keyword}' appears {total_count} times across all files."
        
        if total_count > 0:
            response += " That's probably more than your monthly cardio."
        
        return response
    
    def _handle_login_command(self, intent: Dict[str, Any], uploaded_files: Dict[str, Any]) -> str:
        """Handle login command to get credentials"""
        alias = intent['target']['value']
        
        credentials = self.loginbot.get_login(alias)
        if credentials:
            return f"🔐 **Credentials found:**\n\n{credentials}"
        else:
            return f"🛑 No login info found for '{alias}'. Try uploading a credentials file first or check the alias spelling."
    
    def _handle_prefix_command(self, intent: Dict[str, Any], uploaded_files: Dict[str, Any]) -> str:
        """Handle prefix command to list clouds starting with prefix"""
        prefix = intent['target']['value']
        
        clouds = self.loginbot.list_clouds_starting(prefix)
        if clouds:
            response = f"📡 **Aliases matching '{prefix}':**\n\n"
            for cloud in clouds:
                response += f"• {cloud}\n"
            return response
        else:
            return f"📡 No aliases found starting with '{prefix}'. Try a broader prefix or upload a credentials file."
