"""Optional local read-only MCP example: python -m document_ai.integrations.mcp_server.
No web search, external credentials or document access is exposed.
"""
from mcp.server.fastmcp import FastMCP
server = FastMCP('DocAI scaffold')
@server.tool()
def project_status() -> str:
    """Describe this scaffold's capabilities without accessing private documents."""
    return 'Local extractive retrieval works; external model, Pinecone, and web search integration are pending.'
if __name__ == '__main__': server.run(transport='stdio')
