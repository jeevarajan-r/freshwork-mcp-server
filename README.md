# Freshworks MCP Server (Python)

This project is a proper MCP server implemented with the Python MCP SDK.

Available tools:

- **create_ticket_tool**: Creates a Freshworks ticket.
- **get_ticket_tool**: Gets a ticket by ID.
- **update_ticket_tool**: Updates an existing ticket.
- **list_user_tickets_tool**: Lists tickets for a specific user email.
- **add_ticket_note_tool**: Adds a note to a ticket.

Each tool accepts required fields through parameters, and where applicable, through `description` as `key:value` lines.

## Setup

- Configure `.env` with:
	- `FRESHWORKS_DOMAIN`
	- `FRESHWORKS_API_KEY`
- Create virtual env: `py -m venv .venv`
- Activate: `./.venv/Scripts/activate`
- Install dependencies: `pip install -r requirements.txt`

## Run Server

- Start MCP server (stdio): `python src/main.py`

### Remote Hosting (EC2 / Internet)

This server supports both local stdio and remote Streamable HTTP transport.

Set these environment variables before starting:

- `MCP_TRANSPORT=streamable-http`
- `MCP_HOST=0.0.0.0`
- `MCP_PORT=8000`
- `MCP_HTTP_PATH=/mcp`

Start server:

`python src/main.py`

Remote MCP endpoint becomes:

`http://<your-ec2-public-ip>:8000/mcp`

For local VS Code Copilot stdio usage, keep:

- `MCP_TRANSPORT=stdio` (or leave unset)

Security notes for internet hosting:

- Put the server behind HTTPS (ALB/Nginx/Caddy).
- Restrict inbound access (security groups/IP allow-list).
- Add authentication before exposing publicly.
- Prefer `127.0.0.1` binding unless remote access is required.

VS Code Copilot MCP configuration is in `.vscode/mcp.json` and launches this server as a stdio process.

## Description format example

For create/update tools, pass fields like:

```
subject: Test Ticket
email: user@example.com
description: This is a test ticket.
priority: 1
status: 2
```

For add note:

```
body: Added investigation note
private: true
```
