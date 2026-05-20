import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from tools import add_ticket_note, create_ticket, get_ticket, list_user_tickets, update_ticket

load_dotenv()

mcp = FastMCP(
    "freshwork-mcp-server",
    # Recommended for production streamable-http deployments.
    stateless_http=True,
    json_response=True,
)


def _get_env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_env_list(name: str) -> list[str]:
    value = os.getenv(name, "")
    if not value.strip():
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


@mcp.tool()
def create_ticket_tool(description: str):
    """Create a Freshworks ticket.

    Provide required fields in description as key:value lines.
    Required keys:
    - subject
    - email
    - description
    """
    return create_ticket(description)


@mcp.tool()
def get_ticket_tool(ticket_id: str):
    """Get a specific Freshworks ticket by ID.

    Required fields:
    - ticket_id
    """
    return get_ticket(ticket_id)


@mcp.tool()
def update_ticket_tool(ticket_id: str, description: str):
    """Update an existing Freshworks ticket.

    Required fields:
    - ticket_id
    - description (key:value lines of fields to update)
    """
    return update_ticket(ticket_id, description)


@mcp.tool()
def list_user_tickets_tool(user_email: str):
    """List all tickets for a specific user.

    Required fields:
    - user_email
    """
    return list_user_tickets(user_email)


@mcp.tool()
def add_ticket_note_tool(ticket_id: str, description: str):
    """Add a note to a ticket.

    Required fields:
    - ticket_id
    - description with at least:
      - body
      - private (optional, true/false)
    """
    return add_ticket_note(ticket_id, description)


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()

    # Network/path settings are applied for HTTP transports.
    mcp.settings.host = os.getenv("MCP_HOST", "127.0.0.1")
    mcp.settings.port = int(os.getenv("MCP_PORT", "8000"))
    mcp.settings.streamable_http_path = os.getenv("MCP_HTTP_PATH", "/mcp")
    mcp.settings.mount_path = os.getenv("MCP_SSE_PATH", "/sse")
    mcp.settings.debug = _get_env_bool("MCP_DEBUG", False)

    # Explicitly control transport security via env so EC2 behavior is deterministic.
    mcp.settings.transport_security.enable_dns_rebinding_protection = _get_env_bool(
        "FASTMCP_TRANSPORT_SECURITY__ENABLE_DNS_REBINDING_PROTECTION",
        True,
    )
    allowed_hosts = _get_env_list("FASTMCP_TRANSPORT_SECURITY__ALLOWED_HOSTS")
    if allowed_hosts:
        mcp.settings.transport_security.allowed_hosts = allowed_hosts

    if transport == "streamable-http":
        mcp.run(transport="streamable-http")
    elif transport == "sse":
        mcp.run(transport="sse", mount_path=mcp.settings.mount_path)
    else:
        mcp.run(transport="stdio")
