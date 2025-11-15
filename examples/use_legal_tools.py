"""Example usage of legal tools with Claude Agent SDK

This is a placeholder example showing how the legal tools would be used
once the Claude Agent SDK is properly integrated.

Note: This requires claude-agent-sdk to be installed and configured.
"""

# Placeholder example - will be implemented once Claude Agent SDK is available

"""
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from app.mcp.legal_tools import legal_tools_server


async def main():
    '''
    Example: Using legal tools with Claude Agent SDK
    '''
    options = ClaudeAgentOptions(
        mcp_servers={"legal": legal_tools_server},
        allowed_tools=[
            "mcp__legal__search_law",
            "mcp__legal__search_case",
            "mcp__legal__ask_legal_question"
        ],
        system_prompt="あなたは日本の法律に詳しいアシスタントです。"
    )

    async with ClaudeSDKClient(options=options) as client:
        # Example 1: Search for laws
        await client.query("会社の株主総会に関する法律について教えてください。")

        async for message in client.receive_response():
            print(message)

        # Example 2: Ask a legal question
        await client.query(
            "株主総会の決議要件について、特別決議と普通決議の違いを教えてください。"
        )

        async for message in client.receive_response():
            print(message)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
"""

print(
    """
Legal Tools Example

This example demonstrates how to use the legal tools with Claude Agent SDK.
To use this functionality:

1. Install dependencies:
   uv pip install -e .

2. Set up environment variables:
   export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/legal_db"
   export ANTHROPIC_API_KEY="your_api_key_here"

3. Initialize database:
   psql -U postgres -f scripts/init_db.sql

4. Generate embeddings:
   python -m app.batch.generate_embeddings

5. Install Claude Agent SDK (when available):
   uv pip install claude-agent-sdk

6. Run this example:
   python examples/use_legal_tools.py

Note: Claude Agent SDK integration is planned for future implementation.
"""
)
