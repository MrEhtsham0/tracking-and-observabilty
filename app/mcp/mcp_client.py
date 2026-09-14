# client.py
import asyncio

from fastmcp import Client
from fastmcp.client.transports import StdioTransport


async def main():
    # Connect to the server via stdio
    server_params = StdioTransport(
        command="uv",
        args=["run", "app/mcp/mcp_server.py"]
        )
    async with Client(server_params) as client:
        print("Connected to server")
        
        # 1. Get initial counter (should be 0)
        result = await client.call_tool("get_counter", {})
        print("Result 1:", result)
        
        # 2. Increment by 5
        result = await client.call_tool("increment_counter", {"amount": 5})
        print("Result 2:", result)
        
        # 3. Get counter again (should be 5)
        result = await client.call_tool("get_counter", {})
        print("Result 3:", result)
        
        # 4. Add 3 more
        result = await client.call_tool("increment_counter", {"amount": 3})
        print("Result 4:", result)
        
        # 5. Get final value (should be 8)
        result = await client.call_tool("get_counter", {})
        print("Result 5:", result)
        
        # 6. Reset to 0
        result = await client.call_tool("reset_counter", {})
        print("Result 6:", result)
        
        # 7. Set to 42
        result = await client.call_tool("set_counter", {"value": 42})
        print("Result 7:", result)
        
        # 8. Get final value (should be 42)
        result = await client.call_tool("get_counter", {})
        print("Result 8:", result)

if __name__ == "__main__":
    asyncio.run(main())