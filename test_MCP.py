import asyncio
import json
import os
import sys
from contextlib import AsyncExitStack
from typing import Any, Dict

from dotenv import load_dotenv
from groq import Groq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


load_dotenv()

PYTHON = r"D:\Git\Gen-AI\.venv\Scripts\python.exe"

SERVERS = {
    "database": r"D:\Git\Gen-AI\mcp_servers\database_server.py",
    "filesystem": r"D:\Git\Gen-AI\mcp_servers\filesystem_server.py",
    "rag": r"D:\Git\Gen-AI\mcp_servers\rag_server.py",
}


class MCPClient:
    """Connect to multiple stdio MCP servers and manage their lifetimes."""

    def __init__(
        self,
        servers: dict[str, str],
        groq_api_key: str,
        python: str = PYTHON,
        model: str | None = None,
    ):
        self.servers = servers
        self.python = python
        self.groq_client = Groq(api_key=groq_api_key)
        self.model = model or os.getenv("GROQ_MODEL")
        self.conversation_history = []
        self.sessions: dict[str, ClientSession] = {}
        self.available_tools = {}
        self.tools = []
        self.tool_servers: dict[str, str] = {}
        self._exit_stack = AsyncExitStack()

    async def __aenter__(self):
        await self._exit_stack.__aenter__()
        try:
            for name, path in self.servers.items():
                params = StdioServerParameters(command=self.python, args=[path])
                read, write = await self._exit_stack.enter_async_context(
                    stdio_client(params)
                )
                session = await self._exit_stack.enter_async_context(
                    ClientSession(read, write)
                )
                await session.initialize()
                self.sessions[name] = session

                result = await session.list_tools()
                self.available_tools[name] = result.tools
            self._build_tool_registry()
        except BaseException:
            await self._exit_stack.__aexit__(*sys.exc_info())
            raise
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return await self._exit_stack.__aexit__(exc_type, exc_value, traceback)
    
    async def call_tool(
        self,
        server: str,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Call a named MCP tool on one of the connected servers."""
        if server not in self.sessions:
            raise ValueError(f"Unknown or disconnected MCP server: {server}")
        result = await self.sessions[server].call_tool(
            tool_name, arguments=arguments or {}
        )
        return result.model_dump(by_alias=True)

    def _build_tool_registry(self):
        """Convert discovered MCP tools to Groq's function-tool format."""
        for server, server_tools in self.available_tools.items():
            for tool in server_tools:
                if tool.name in self.tool_servers:
                    raise ValueError(f"Duplicate MCP tool name: {tool.name}")

                self.tool_servers[tool.name] = server
                self.tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.inputSchema,
                    },
                })

    async def _execute_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route a Groq function call to the MCP server that owns the tool."""
        server = self.tool_servers.get(tool_name)
        if server is None:
            raise ValueError(f"Unknown MCP tool: {tool_name}")
        return await self.call_tool(server, tool_name, arguments)
    
    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
        print("🔄 Conversation history cleared")

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
            print("\n Thinking...")

        # First LLM call to determine which tools to use
        response = self.groq_client.chat.completions.create(
            model=self.model,
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
            function_args = json.loads(tool_call.function.arguments or "{}")
            
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
            model=self.model,
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
    


async def main():
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise RuntimeError("GROQ_API_KEY is missing from the environment or .env file")

    async with MCPClient(SERVERS, groq_api_key) as client:
        answer = await client.process_query(
            "Give me the details for employee EMP001."
        )
        print(answer)


if __name__ == "__main__":
    asyncio.run(main())
