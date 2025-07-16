import os
import io
from typing import Dict, List, Optional, Tuple

class LoginBot:
    """Handle credential management for Mark-bot"""
    
    def __init__(self):
        self.credentials = {}
        self.loaded = False
    
    def load_credentials_from_file(self, file_content: str) -> None:
        """Load credentials from uploaded LOGS.txt file content"""
        self.credentials = {}
        
        for line in file_content.strip().split('\n'):
            if ',' in line:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    # Format: email,password (from LOGS.txt)
                    email = parts[0].strip()
                    password = parts[1].strip()
                    
                    # Extract cloud name from email (part before @)
                    cloud_name = email.split('@')[0].lower()
                    self.credentials[cloud_name] = (email, password)
        
        self.loaded = True
    
    def get_login(self, cloud_name: str) -> Optional[str]:
        """Get login information for a specific cloud"""
        if not self.loaded:
            return None
            
        cloud_name = cloud_name.lower().strip()
        if cloud_name in self.credentials:
            email, password = self.credentials[cloud_name]
            if email:
                return f"📦 {cloud_name.upper()}\nEmail: {email}\nPassword: {password}"
            else:
                return f"📦 {cloud_name.upper()}\nPassword: {password}"
        return None
    
    def list_clouds_starting(self, prefix: str, limit: int = 10) -> List[str]:
        """Returns a list of cloud aliases that start with a given prefix"""
        if not self.loaded:
            return []
            
        matches = []
        for cloud in self.credentials.keys():
            if cloud.startswith(prefix.lower()):
                matches.append(cloud)
                if len(matches) >= limit:
                    break
        return matches
    
    def get_all_clouds(self) -> List[str]:
        """Get all available cloud aliases"""
        if not self.loaded:
            return []
        return list(self.credentials.keys())
    
    def search_clouds(self, query: str) -> List[str]:
        """Search for clouds containing the query"""
        if not self.loaded:
            return []
            
        query = query.lower()
        matches = []
        for cloud in self.credentials.keys():
            if query in cloud:
                matches.append(cloud)
        return matches

# Legacy functions for compatibility
def get_login(cloud_name: str) -> Optional[str]:
    """Legacy function - requires global loginbot instance"""
    return None

def list_clouds_starting(prefix: str, limit: int = 10) -> List[str]:
    """Legacy function - requires global loginbot instance"""
    return []