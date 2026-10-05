import asyncio
import json
from typing import Any, Dict, List
from groq import Groq
import os
import sys







# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import your ACTUAL MCP servers
from mcp_servers.database_server import DatabaseMCPServer
from mcp_servers.filesystem_server import FilesystemMCPServer
from mcp_servers.rag_server import RAGServer














class CollegeAssistantOrchestrator:
    """
    Orchestrator that uses Groq LLM to intelligently route queries
    to Database, Filesystem, and RAG MCP servers.
    """
    




    def __init__(self, groq_api_key: str):
        self.groq_client = Groq(api_key=groq_api_key)
        
        # Initialize all MCP servers
        print("🔧 Initializing MCP servers...")
        self.db_server = DatabaseMCPServer()
        self.filesystem_server = FilesystemMCPServer()
        self.rag_server = RAGServer()
        
        # Tool registry
        self.tools = self._build_tool_registry()
        
        # Conversation history
        self.conversation_history = []
        
        print(f"✅ Loaded {len(self.tools)} tools from 3 MCP servers")
        







    def _build_tool_registry(self) -> List[Dict[str, Any]]:
        """Build a registry of all available tools from MCP servers."""
        return [
            # Database Server Tools (Employee Data)
            {
                "type": "function",
                "function": {
                    "name": "get_employee",
                    "description": "Get detailed information about an employee by ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "integer",
                                "description": "The employee ID number"
                            }
                        },
                        "required": ["employee_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_employees",
                    "description": "Search for employees by name (partial match)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name or partial name to search for"
                            }
                        },
                        "required": ["name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_employees_by_department",
                    "description": "Get all employees in a specific department",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "department": {
                                "type": "string",
                                "description": "Department name (e.g., 'Engineering', 'HR', 'Sales')"
                            }
                        },
                        "required": ["department"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_employees",
                    "description": "Get a list of all employees in the database",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            
            # Filesystem Server Tools (Announcements)
            {
                "type": "function",
                "function": {
                    "name": "list_announcements",
                    "description": "List all available announcement files",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_announcement",
                    "description": "Read the full content of a specific announcement file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the announcement file (e.g., 'holiday_2024.txt')"
                            }
                        },
                        "required": ["filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_announcements",
                    "description": "Search announcements by keyword",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keyword": {
                                "type": "string",
                                "description": "Keyword to search for in announcements"
                            }
                        },
                        "required": ["keyword"]
                    }
                }
            },
            
            # RAG Server Tools (Policy Documents)
            {
                "type": "function",
                "function": {
                    "name": "search_policies",
                    "description": "Search policy documents. Use this for questions about leave policy, salary policy, or other HR policies.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language question about policies"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_policies",
                    "description": "List all available policy documents",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]
    




    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by routing to the appropriate MCP server."""
        
        try:
            # Database Server Tools
            if tool_name == "get_employee":
                return await self.db_server.get_employee(arguments["employee_id"])
            elif tool_name == "search_employees":
                return await self.db_server.search_employees(arguments["name"])
            elif tool_name == "get_employees_by_department":
                return await self.db_server.get_employees_by_department(arguments["department"])
            elif tool_name == "get_all_employees":
                return await self.db_server.get_all_employees()
            
            # Filesystem Server Tools
            elif tool_name == "list_announcements":
                return await self.filesystem_server.list_announcements()
            elif tool_name == "read_announcement":
                return await self.filesystem_server.read_announcement(arguments["filename"])
            elif tool_name == "search_announcements":
                return await self.filesystem_server.search_announcements(arguments["keyword"])
            
            # RAG Server Tools
            elif tool_name == "search_policies":
                return self.rag_server.search_policies(arguments["query"])
            elif tool_name == "list_policies":
                return self.rag_server.list_policies()
            
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    




    async def process_query(self, user_query: str, verbose: bool = True) -> str:
        """
        Process a user query using Groq LLM to orchestrate MCP servers.
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_query
        })
        
        # System prompt
        system_message = {
            "role": "system",
            "content": """You are a helpful and confident HR assistant with direct access to:

1. **Employee Database**: Employee information, departments, contact details
2. **Announcements**: Company announcements, holidays, team events, policy updates
3. **Policy Documents**: HR policies (leave policy, salary policy, etc.)

Your behavior:
- Provide direct, accurate answers using the tools available
- Be concise and professional
- Format lists clearly with line breaks between items for better readability

Be confident and helpful."""
        }
        
        # Prepare messages for Groq
        messages = [system_message] + self.conversation_history
        
        if verbose:
            print("\n🤔 Thinking...")
        
        # First LLM call to determine which tools to use
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=self.tools,
            tool_choice="auto",
            max_tokens=4096
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        # If no tools needed, return direct response
        if not tool_calls:
            assistant_message = response_message.content
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            return assistant_message
        
        # Execute all tool calls
        self.conversation_history.append({
            "role": "assistant",
            "content": response_message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in tool_calls
            ]
        })
        
        # Execute each tool call
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if verbose:
                print(f"🔧 Using: {function_name}({json.dumps(function_args, indent=2)})")
            
            # Execute the tool
            tool_result = await self._execute_tool(function_name, function_args)
            
            if verbose:
                print(f"✅ Got result from {function_name}")
            
            # Add tool response to history
            self.conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result)
            })
        
        # Second LLM call to generate final response
        if verbose:
            print("💭 Generating response...")
            
        final_response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[system_message] + self.conversation_history,
            max_tokens=4096
        )
        
        final_message = final_response.choices[0].message.content
        
        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": final_message
        })
        
        return final_message
    





    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
        print("🔄 Conversation history cleared")







async def main():
    """Interactive demo of the orchestrator."""
    
    # Get API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("❌ Error: GROQ_API_KEY not found in environment variables")
        return
    
    print("\n" + "="*60)
    print("🎓 RAG-MCP Assistant Orchestrator")
    print("="*60)
    
    # Initialize orchestrator
    try:
        orchestrator = CollegeAssistantOrchestrator(groq_api_key)
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        return
    
    # Demo queries
    demo_queries = [
        "What are the recent announcements?",
        "Who works in the Engineering department?",
        "What's the leave policy for sick leave?",
        "Search for employees named John",
    ]
    
    print("\n📝 Running demo queries...\n")
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}/{len(demo_queries)}: {query}")
        print('='*60)
        
        try:
            response = await orchestrator.process_query(query)
            print(f"\n💬 Response:\n{response}\n")
        except Exception as e:
            print(f"❌ Error processing query: {e}")
        
        await asyncio.sleep(1)
    
    print("\n" + "="*60)
    print("✅ Demo complete! Starting interactive mode...")
    print("="*60)
    print("\n💡 Commands:")
    print("   - Type your question and press Enter")
    print("   - Type 'reset' to clear conversation history")
    print("   - Type 'quit' or 'exit' to leave")
    print()
    
    # Interactive mode
    while True:
        try:
            user_input = input("\n❓ You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == 'reset':
                orchestrator.reset_conversation()
                continue
            
            if not user_input:
                continue
            
            response = await orchestrator.process_query(user_input)
            print(f"\n💬 Assistant: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())