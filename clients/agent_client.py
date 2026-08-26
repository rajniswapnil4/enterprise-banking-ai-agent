import asyncio
import json
import urllib.request

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:7b"


def ask_qwen(messages, tools=None):
    """Send messages to Qwen through Ollama."""

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
    }

    if tools:
        payload["tools"] = tools

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


server_params = StdioServerParameters(
    command="/Users/rajnimehra/enterprise-banking-ai-agent/.venv/bin/python",
    args=["mcp_servers/customer_server.py"],
)


async def main():

    async with stdio_client(server_params) as (read_stream, write_stream):

        async with ClientSession(read_stream, write_stream) as session:

            await session.initialize()

            # --------------------------------------------------
            # 1. Discover MCP tools
            # --------------------------------------------------

            tools_response = await session.list_tools()

            ollama_tools = []

            for tool in tools_response.tools:

                ollama_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.input_schema,
                    },
                })

            print("\nMCP tools discovered:")

            for tool in tools_response.tools:
                print(f"- {tool.name}")

            # --------------------------------------------------
            # 2. Send user request to Qwen
            # --------------------------------------------------

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a banking assistant. "
                        "Use the available tools when you need "
                        "customer or account information."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Give me the customer details and bank accounts "
                        "for customer CUST001."
                    ),
                },
            ]

            response = ask_qwen(
                messages,
                tools=ollama_tools
            )

            assistant_message = response["message"]

            # Add Qwen's response to conversation
            messages.append(assistant_message)

            # --------------------------------------------------
            # 3. Execute Qwen's tool calls
            # --------------------------------------------------

            tool_calls = assistant_message.get("tool_calls", [])

            if tool_calls:

                print("\nQwen requested these tools:\n")

                for tool_call in tool_calls:

                    function = tool_call["function"]

                    tool_name = function["name"]
                    arguments = function["arguments"]

                    print(f"Calling: {tool_name}")
                    print(f"Arguments: {arguments}")

                    result = await session.call_tool(
                        tool_name,
                        arguments
                    )

                    # Extract returned text
                    result_text = []

                    for content in result.content:
                        if hasattr(content, "text"):
                            result_text.append(content.text)

                    tool_result = "\n".join(result_text)

                    print(f"Result: {tool_result}\n")

                    # Send tool result back to Qwen
                    messages.append({
                        "role": "tool",
                        "content": tool_result,
                    })

            # --------------------------------------------------
            # 4. Ask Qwen to produce the final answer
            # --------------------------------------------------

            final_response = ask_qwen(messages)

            print("\n==============================")
            print("FINAL AI RESPONSE")
            print("==============================\n")

            print(final_response["message"]["content"])


if __name__ == "__main__":
    asyncio.run(main())