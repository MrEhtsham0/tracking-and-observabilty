# app/mcp/mcp_debug.py
import asyncio

from fastmcp import Client
from fastmcp.client.transports import StdioTransport


async def main():
    # Connect to the server
    async with Client(StdioTransport(
        command="uv",
        args=["run", "app/mcp/mcp_server.py"]
    )) as client:
        print("Connected to server")
        
        # List all available tools
        tools = await client.list_tools()
        print("\nAvailable tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Try to call get_counter if it exists
        tool_names = [tool.name for tool in tools]
        if "get_counter" in tool_names:
            result = await client.call_tool("get_counter", {})
            print(f"\nget_counter result: {result}")
        else:
            print("\n'get_counter' tool not found!")

if __name__ == "__main__":
    asyncio.run(main())