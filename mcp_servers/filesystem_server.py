"""
MCP Server #3: Filesystem Access (Company Announcements)
Provides tools to read and list company announcement files
"""

import os
import sys
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv







# Fix working directory to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

load_dotenv()






class FilesystemMCPServer:
    """
    Filesystem as MCP-style server
    
    Tools provided:
    1. list_announcements - List all announcement files
    2. read_announcement - Read specific announcement
    3. get_recent_announcements - Get most recent announcements
    """
    
    def __init__(self):
        """Initialize filesystem access"""
        
        print("🔄 Initializing Filesystem Server...")
        
        self.announcements_path = os.getenv("ANNOUNCEMENTS_PATH", "data/announcements")
        
        # Ensure announcements folder exists
        if not os.path.exists(self.announcements_path):
            os.makedirs(self.announcements_path, exist_ok=True)
            print(f"✅ Created announcements folder: {self.announcements_path}")
        
        # Count files
        files = [f for f in os.listdir(self.announcements_path) 
                 if os.path.isfile(os.path.join(self.announcements_path, f))]
        
        print(f"✅ Filesystem Server initialized ({len(files)} announcement files)")
    


    def list_announcements(self) -> Dict:
        """
        Tool 1: List all announcement files
        
        Returns:
            Dict with list of announcement files
        """
        
        print("  📋 Listing announcement files...")
        
        try:
            files = []
            
            if os.path.exists(self.announcements_path):
                for filename in os.listdir(self.announcements_path):
                    filepath = os.path.join(self.announcements_path, filename)
                    
                    if os.path.isfile(filepath):
                        # Get file info
                        stat = os.stat(filepath)
                        modified = datetime.fromtimestamp(stat.st_mtime)
                        size = stat.st_size
                        
                        files.append({
                            "filename": filename,
                            "size": size,
                            "modified": modified.strftime("%Y-%m-%d %H:%M:%S"),
                            "path": filepath
                        })
                
                # Sort by modified date (newest first)
                files.sort(key=lambda x: x['modified'], reverse=True)
            
            return {
                "announcements": files,
                "count": len(files),
                "tool": "list_announcements"
            }
            
        except Exception as e:
            return {
                "error": True,
                "message": str(e),
                "tool": "list_announcements"
            }
    


    def read_announcement(self, filename: str) -> Dict:
        """
        Tool 2: Read a specific announcement file
        
        Args:
            filename: Name of the announcement file
        
        Returns:
            Dict with file content
        """
        
        print(f"  📄 Reading announcement: {filename}")
        
        try:
            filepath = os.path.join(self.announcements_path, filename)
            
            if not os.path.exists(filepath):
                return {
                    "filename": filename,
                    "found": False,
                    "message": f"Announcement '{filename}' not found",
                    "tool": "read_announcement"
                }
            
            # Read file content
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get file info
            stat = os.stat(filepath)
            modified = datetime.fromtimestamp(stat.st_mtime)
            
            return {
                "filename": filename,
                "content": content,
                "modified": modified.strftime("%Y-%m-%d %H:%M:%S"),
                "size": stat.st_size,
                "found": True,
                "tool": "read_announcement"
            }
            
        except Exception as e:
            return {
                "error": True,
                "message": str(e),
                "tool": "read_announcement"
            }
    


    def get_recent_announcements(self, limit: int = 3) -> Dict:
        """
        Tool 3: Get most recent announcements
        
        Args:
            limit: Number of recent announcements to return (default: 3)
        
        Returns:
            Dict with recent announcements and their content
        """
        
        print(f"  📰 Getting {limit} most recent announcements...")
        
        try:
            # First list all files
            all_files = self.list_announcements()
            
            if all_files.get('error'):
                return all_files
            
            files = all_files['announcements'][:limit]
            
            # Read content of each
            announcements = []
            for file_info in files:
                content_result = self.read_announcement(file_info['filename'])
                
                if content_result.get('found'):
                    announcements.append({
                        "filename": file_info['filename'],
                        "content": content_result['content'],
                        "modified": file_info['modified']
                    })
            
            return {
                "announcements": announcements,
                "count": len(announcements),
                "tool": "get_recent_announcements"
            }
            
        except Exception as e:
            return {
                "error": True,
                "message": str(e),
                "tool": "get_recent_announcements"
            }
    


    def search_announcements(self, keyword: str) -> Dict:
        """
        Tool 4 (Bonus): Search announcements by keyword
        
        Args:
            keyword: Keyword to search for
        
        Returns:
            Dict with matching announcements
        """
        
        print(f"  🔍 Searching announcements for: {keyword}")
        
        try:
            all_files = self.list_announcements()
            
            if all_files.get('error'):
                return all_files
            
            matches = []
            keyword_lower = keyword.lower()
            
            for file_info in all_files['announcements']:
                # Read file content
                content_result = self.read_announcement(file_info['filename'])
                
                if content_result.get('found'):
                    content = content_result['content']
                    
                    # Check if keyword in filename or content
                    if (keyword_lower in file_info['filename'].lower() or 
                        keyword_lower in content.lower()):
                        
                        matches.append({
                            "filename": file_info['filename'],
                            "content": content,
                            "modified": file_info['modified']
                        })
            
            return {
                "matches": matches,
                "count": len(matches),
                "keyword": keyword,
                "tool": "search_announcements"
            }
            
        except Exception as e:
            return {
                "error": True,
                "message": str(e),
                "tool": "search_announcements"
            }
    


    def get_tool_descriptions(self) -> List[Dict]:
        """
        Get descriptions of available tools (for LLM to understand)
        """
        return [
            {
                "name": "list_announcements",
                "description": "List all company announcement files. Use when user wants to see what announcements are available.",
                "parameters": {},
                "examples": [
                    "What announcements are available?",
                    "Show me all company announcements",
                    "List recent updates"
                ]
            },
            {
                "name": "read_announcement",
                "description": "Read a specific announcement file. Use when user wants to read a particular announcement.",
                "parameters": {
                    "filename": "Name of the announcement file"
                },
                "examples": [
                    "Read the holiday announcement",
                    "Show me policy_update.txt",
                    "What does team_event.txt say?"
                ]
            },
            {
                "name": "get_recent_announcements",
                "description": "Get the most recent company announcements (default: 3). Use when user asks for latest updates.",
                "parameters": {
                    "limit": "Number of announcements to retrieve (optional, default: 3)"
                },
                "examples": [
                    "What are the latest announcements?",
                    "Show me recent updates",
                    "Any new announcements?"
                ]
            },
            {
                "name": "search_announcements",
                "description": "Search announcements by keyword. Use when user is looking for specific information.",
                "parameters": {
                    "keyword": "Search keyword"
                },
                "examples": [
                    "Find announcements about holidays",
                    "Search for policy changes",
                    "Any announcements about events?"
                ]
            }
        ]
    


    
    def call_tool(self, tool_name: str, **kwargs) -> Dict:
        """
        Generic tool calling interface
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Tool-specific arguments
        
        Returns:
            Tool response
        """
        
        if tool_name == "list_announcements":
            return self.list_announcements()
        
        elif tool_name == "read_announcement":
            filename = kwargs.get("filename", "")
            if not filename:
                return {"error": True, "message": "filename parameter required"}
            return self.read_announcement(filename)
        
        elif tool_name == "get_recent_announcements":
            limit = kwargs.get("limit", 3)
            return self.get_recent_announcements(limit)
        
        elif tool_name == "search_announcements":
            keyword = kwargs.get("keyword", "")
            if not keyword:
                return {"error": True, "message": "keyword parameter required"}
            return self.search_announcements(keyword)
        
        else:
            return {
                "error": True,
                "message": f"Unknown tool: {tool_name}"
            }






# Test function
def test_filesystem_server():
    """Test the filesystem server with sample queries"""
    
    print("\n" + "="*60)
    print("🧪 TESTING FILESYSTEM SERVER")
    print("="*60 + "\n")
    
    # Initialize server
    server = FilesystemMCPServer()
    
    print("\n" + "-"*60)
    print("Test 1: List Announcements")
    print("-"*60)
    
    result = server.list_announcements()
    
    print(f"\n📋 Found {result['count']} announcements:")
    for file in result['announcements']:
        print(f"   - {file['filename']} ({file['size']} bytes)")
        print(f"     Modified: {file['modified']}")
    
    print("\n" + "-"*60)
    print("Test 2: Read Specific Announcement")
    print("-"*60)
    
    if result['count'] > 0:
        filename = result['announcements'][0]['filename']
        content_result = server.read_announcement(filename)
        
        if content_result.get('found'):
            print(f"\n📄 {filename}:")
            print(f"\n{content_result['content'][:300]}...")
            print(f"\n... (truncated, total {content_result['size']} bytes)")
    
    print("\n" + "-"*60)
    print("Test 3: Get Recent Announcements")
    print("-"*60)
    
    recent = server.get_recent_announcements(limit=2)
    
    print(f"\n📰 {recent['count']} Most Recent Announcements:")
    for ann in recent['announcements']:
        print(f"\n   📌 {ann['filename']}")
        print(f"      Modified: {ann['modified']}")
        print(f"      Preview: {ann['content'][:100]}...")
    
    print("\n" + "-"*60)
    print("Test 4: Search Announcements")
    print("-"*60)
    
    search_result = server.search_announcements("holiday")
    
    print(f"\n🔍 Search for 'holiday': {search_result['count']} matches")
    for match in search_result['matches']:
        print(f"   - {match['filename']}")
    
    print("\n" + "-"*60)
    print("Test 5: Tool Descriptions")
    print("-"*60)
    
    tools = server.get_tool_descriptions()
    print(f"\nAvailable Tools: {len(tools)}")
    for tool in tools:
        print(f"\n📌 {tool['name']}")
        print(f"   {tool['description'][:70]}...")
    
    print("\n" + "="*60)
    print("✅ Filesystem Server tests complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_filesystem_server()