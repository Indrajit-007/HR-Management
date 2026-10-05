"""
Check if all paths are correct
"""

import os

print("\n🔍 Checking Project Structure...\n")

# Expected structure
structure = {
    "data": {
        "type": "folder",
        "children": {
            "policies": {"type": "folder", "should_contain": "PDF files"},
            "announcements": {"type": "folder"},
            "employees.db": {"type": "file"}
        }
    },
    "mcp_servers": {
        "type": "folder",
        "children": {
            "rag_server.py": {"type": "file"}
        }
    },
    ".env": {"type": "file"},
    "requirements.txt": {"type": "file"}
}

def check_item(path, name, info, indent=0):
    full_path = os.path.join(path, name)
    prefix = "  " * indent
    
    if info["type"] == "folder":
        if os.path.isdir(full_path):
            print(f"{prefix}✅ {name}/ (folder)")
            
            # Check children
            if "children" in info:
                for child_name, child_info in info["children"].items():
                    check_item(full_path, child_name, child_info, indent + 1)
            
            # Check if should contain files
            if "should_contain" in info:
                files = os.listdir(full_path)
                if files:
                    print(f"{prefix}   ✅ Contains {len(files)} files:")
                    for f in files[:3]:  # Show first 3
                        print(f"{prefix}      - {f}")
                    if len(files) > 3:
                        print(f"{prefix}      ... and {len(files) - 3} more")
                else:
                    print(f"{prefix}   ⚠️  Empty (should contain {info['should_contain']})")
        else:
            print(f"{prefix}❌ {name}/ (folder missing)")
            print(f"{prefix}   Creating: {os.path.abspath(full_path)}")
            os.makedirs(full_path, exist_ok=True)
            print(f"{prefix}   ✅ Created")
    
    elif info["type"] == "file":
        if os.path.isfile(full_path):
            print(f"{prefix}✅ {name} (file)")
        else:
            print(f"{prefix}❌ {name} (file missing)")

# Check from current directory
current = os.getcwd()
print(f"📂 Current directory: {current}\n")

for name, info in structure.items():
    check_item(".", name, info)

print("\n" + "="*50)
print("✅ Structure check complete!")
print("="*50 + "\n")