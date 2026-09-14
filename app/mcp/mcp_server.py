from typing import Any

from fastmcp import Context, FastMCP

session_store:dict[str,dict[str,Any]]={}

mcp = FastMCP("Stateful MCP servers")

@mcp.tool()
async def get_counter(context:Context):
    session_id = context.session_id
    print(f"Session ID: {session_id}")
    if session_id not in session_store:
        session_store[session_id] = {"counter": 0}
    session_store[session_id]["counter"] += 1
    return {"counter": session_store[session_id]["counter"]}

@mcp.tool()
async def increment_counter(ctx: Context, amount: int = 1) -> str:
    """Increment the counter for this session by a given amount."""
    session_id = ctx.session_id
    if not session_id:
        return "Error: No session found"
    
    # Initialize if new session
    if session_id not in session_store:
        session_store[session_id] = {"counter": 0}
    
    session_store[session_id]["counter"] += amount
    new_value = session_store[session_id]["counter"]
    return f"Counter incremented by {amount}. New value: {new_value}"

@mcp.tool()
async def reset_counter(ctx: Context) -> str:
    """Reset the counter to 0 for this session."""
    session_id = ctx.session_id
    if not session_id:
        return "Error: No session found"
    
    session_store[session_id] = {"counter": 0}
    return f"Counter reset to 0 for session {session_id[:8]}"

@mcp.tool()
async def set_counter(ctx: Context, value: int) -> str:
    """Set the counter to a specific value."""
    session_id = ctx.session_id
    if not session_id:
        return "Error: No session found"
    
    session_store[session_id] = {"counter": value}
    return f"Counter set to {value} for session {session_id[:8]}"

# Run with stdio transport
if __name__ == "__main__":
    mcp.run(transport="stdio")
