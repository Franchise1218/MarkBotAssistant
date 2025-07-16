# Mark-bot Repository

## Overview

Mark-bot is a Streamlit-based file processing and chatbot application that allows users to upload Excel and text files and ask questions about their content. The system is designed to provide intelligent responses based on file analysis using fuzzy string matching and data processing capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for web interface
- **Components**: 
  - Main chat interface for user interactions
  - Sidebar for file management and uploads
  - Session state management for conversation history
- **File Support**: Excel (.xlsx, .xls) and text (.txt) files

### Backend Architecture
- **Core Components**:
  - `MarkBot` class for chatbot logic and response generation
  - `FileProcessor` class for handling file uploads and data extraction
  - SQLite database for data storage and querying
- **Data Processing**: Pandas for Excel/CSV manipulation and analysis
- **Search Engine**: RapidFuzz for fuzzy string matching with 75% similarity threshold

### Data Storage
- **Primary Database**: SQLite (`mark_database.db`)
- **Data Source**: Excel file (`MASTER DVD.xlsx`) as the primary data source
- **In-Memory Processing**: Pandas DataFrames for real-time data manipulation
- **Session Management**: Streamlit session state for temporary data storage

## Key Components

### 1. File Processing System (`file_processor.py`)
- Handles multiple file format support
- Extracts structured data from Excel sheets
- Processes text files for content analysis
- Validates file formats and handles errors gracefully

### 2. Chatbot Engine (`chatbot.py`)
- Intent analysis for user queries
- Context-aware response generation
- Integration with file processing results
- Conversation history management

### 3. Legacy Mark System (`Mark.py`)
- SQLite database operations
- Excel-to-SQL data synchronization
- Specialized autograph data search functionality
- Disc lookup capabilities

### 4. Web Interface (`app.py`)
- Streamlit-based UI with chat interface
- File upload management
- Real-time response display
- Session state persistence

## Data Flow

1. **File Upload**: Users upload Excel/text files through Streamlit interface
2. **File Processing**: `FileProcessor` extracts and structures data from uploaded files
3. **Data Storage**: Processed data stored in session state and optionally in SQLite
4. **Query Processing**: User queries analyzed for intent and keywords
5. **Search & Match**: Fuzzy string matching against processed file content
6. **Response Generation**: Relevant information formatted and returned to user

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **RapidFuzz**: Fuzzy string matching for search functionality
- **SQLite3**: Embedded database for data persistence

### File Processing
- **openpyxl/xlrd**: Excel file reading capabilities
- **io**: Stream processing for file handling

### Authentication (Legacy)
- **loginbot**: Custom authentication module for cloud services

## Deployment Strategy

### Local Development
- Python environment with required dependencies
- SQLite database for local data storage
- Streamlit development server for testing

### Production Considerations
- Streamlit Cloud or similar platform deployment
- File upload size limitations management
- Database persistence across sessions
- Error handling and logging implementation

### Scalability Notes
- Current architecture suitable for single-user or small team usage
- SQLite may need upgrade to PostgreSQL for larger deployments
- Session state management may require external storage for production scale

## Development Notes

- The system uses fuzzy matching with a 75% similarity threshold for search results
- File processing is done in-memory using Pandas DataFrames
- Session state manages temporary data and conversation history
- Error handling implemented at multiple levels for robust operation
- The legacy Mark.py system suggests this is an evolution of an existing tool