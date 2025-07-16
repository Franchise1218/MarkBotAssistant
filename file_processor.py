import pandas as pd
import io
import re
from typing import Dict, Any, List, Union

class FileProcessor:
    """Handles processing of uploaded Excel and text files"""
    
    def __init__(self):
        self.supported_formats = ['.xlsx', '.xls', '.txt']
    
    def process_file(self, uploaded_file) -> Dict[str, Any]:
        """
        Process an uploaded file and return structured data
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Dictionary containing processed file data
        """
        filename = uploaded_file.name
        file_extension = self._get_file_extension(filename)
        
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        try:
            if file_extension in ['.xlsx', '.xls']:
                return self._process_excel_file(uploaded_file)
            elif file_extension == '.txt':
                return self._process_text_file(uploaded_file)
        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename"""
        return '.' + filename.split('.')[-1].lower()
    
    def _process_excel_file(self, uploaded_file) -> Dict[str, Any]:
        """Process Excel file and return structured data"""
        try:
            # Read Excel file
            excel_data = pd.read_excel(uploaded_file, sheet_name=None)
            
            processed_data = {
                'type': 'excel',
                'filename': uploaded_file.name,
                'sheets': {},
                'summary': {}
            }
            
            for sheet_name, df in excel_data.items():
                # Convert DataFrame to dictionary for easier querying
                sheet_data = {
                    'data': df,
                    'shape': df.shape,
                    'columns': df.columns.tolist(),
                    'dtypes': df.dtypes.to_dict(),
                    'sample_data': df.head().to_dict('records'),
                    'summary_stats': self._get_dataframe_summary(df)
                }
                processed_data['sheets'][sheet_name] = sheet_data
            
            processed_data['summary'] = self._create_excel_summary(processed_data['sheets'])
            
            return processed_data
            
        except Exception as e:
            raise Exception(f"Failed to process Excel file: {str(e)}")
    
    def _process_text_file(self, uploaded_file) -> Dict[str, Any]:
        """Process text file and return structured data"""
        try:
            # Read text content
            content = uploaded_file.read().decode('utf-8')
            
            processed_data = {
                'type': 'text',
                'filename': uploaded_file.name,
                'content': content,
                'lines': content.split('\n'),
                'word_count': len(content.split()),
                'line_count': len(content.split('\n')),
                'char_count': len(content),
                'summary': self._create_text_summary(content)
            }
            
            return processed_data
            
        except Exception as e:
            raise Exception(f"Failed to process text file: {str(e)}")
    
    def _get_dataframe_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics for a DataFrame"""
        summary = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'null_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.astype(str).to_dict()
        }
        
        # Add numeric summary if there are numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        return summary
    
    def _create_excel_summary(self, sheets: Dict[str, Any]) -> Dict[str, Any]:
        """Create overall summary for Excel file"""
        total_rows = sum(sheet['shape'][0] for sheet in sheets.values())
        total_columns = sum(sheet['shape'][1] for sheet in sheets.values())
        
        return {
            'total_sheets': len(sheets),
            'sheet_names': list(sheets.keys()),
            'total_rows': total_rows,
            'total_columns': total_columns,
            'sheet_summaries': {name: sheet['summary_stats'] for name, sheet in sheets.items()}
        }
    
    def _create_text_summary(self, content: str) -> Dict[str, Any]:
        """Create summary for text content"""
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        
        # Find most common words (basic implementation)
        word_freq = {}
        for word in words:
            word_clean = re.sub(r'[^\w]', '', word.lower())
            if word_clean and len(word_clean) > 3:  # Ignore short words
                word_freq[word_clean] = word_freq.get(word_clean, 0) + 1
        
        # Get top 10 most common words
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
            'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'top_words': top_words
        }
    
    def search_in_file(self, query: str, file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for specific content in processed file data"""
        results = []
        
        if file_data['type'] == 'excel':
            results.extend(self._search_excel(query, file_data))
        elif file_data['type'] == 'text':
            results.extend(self._search_text(query, file_data))
        
        return results
    
    def _search_excel(self, query: str, file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for content in Excel file"""
        results = []
        query_lower = query.lower()
        
        for sheet_name, sheet_data in file_data['sheets'].items():
            df = sheet_data['data']
            
            # Search in column names
            matching_columns = [col for col in df.columns if query_lower in str(col).lower()]
            if matching_columns:
                results.append({
                    'type': 'column_match',
                    'sheet': sheet_name,
                    'columns': matching_columns,
                    'description': f"Found matching columns in sheet '{sheet_name}'"
                })
            
            # Search in cell values
            for col in df.columns:
                mask = df[col].astype(str).str.lower().str.contains(query_lower, na=False)
                if mask.any():
                    matching_rows = df[mask]
                    results.append({
                        'type': 'cell_match',
                        'sheet': sheet_name,
                        'column': col,
                        'matches': matching_rows.to_dict('records'),
                        'description': f"Found {len(matching_rows)} matching rows in column '{col}' of sheet '{sheet_name}'"
                    })
        
        return results
    
    def _search_text(self, query: str, file_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for content in text file"""
        results = []
        query_lower = query.lower()
        content = file_data['content']
        lines = file_data['lines']
        
        # Search for query in content
        if query_lower in content.lower():
            matching_lines = []
            for i, line in enumerate(lines):
                if query_lower in line.lower():
                    matching_lines.append({
                        'line_number': i + 1,
                        'content': line.strip()
                    })
            
            if matching_lines:
                results.append({
                    'type': 'text_match',
                    'matches': matching_lines,
                    'description': f"Found {len(matching_lines)} matching lines"
                })
        
        return results
