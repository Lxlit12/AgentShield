from fastmcp import Client


MCP_SERVER_URL = "http://127.0.0.1:8001/mcp"


async def list_mcp_tools():

    client = Client(MCP_SERVER_URL)

    async with client:
        tools = await client.list_tools()

        for tool in tools:
            print(f"Tool: {tool.name}")
            print(f"Description: {tool.description}")
            print("-" * 40)


async def call_mcp_tool(tool_name: str, arguments: dict):

    client = Client(MCP_SERVER_URL)

    async with client:

        result = await client.call_tool(
            tool_name,
            arguments
        )

        return result.data