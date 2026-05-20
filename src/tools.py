import os
from typing import Any, Dict

import requests
from dotenv import load_dotenv

load_dotenv()

def _normalize_domain(value: str) -> str:
    normalized = value.strip().rstrip("/")
    if normalized.startswith("https://"):
        normalized = normalized[len("https://"):]
    elif normalized.startswith("http://"):
        normalized = normalized[len("http://"):]
    return normalized


FRESHWORKS_DOMAIN = _normalize_domain(os.getenv("FRESHWORKS_DOMAIN", ""))
FRESHWORKS_API_KEY = os.getenv("FRESHWORKS_API_KEY", "").strip()
BASE_URL = f"https://{FRESHWORKS_DOMAIN}/api/v2"
AUTH = (FRESHWORKS_API_KEY, "X")


def parse_description(description: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for line in description.split("\n"):
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        raw = value.strip()
        if raw.lower() in {"true", "false"}:
            result[key] = raw.lower() == "true"
        else:
            try:
                result[key] = int(raw)
            except ValueError:
                result[key] = raw
    return result


def _validate_config() -> Dict[str, str]:
    if not FRESHWORKS_DOMAIN:
        return {"error": "Missing FRESHWORKS_DOMAIN in .env"}
    if not FRESHWORKS_API_KEY:
        return {"error": "Missing FRESHWORKS_API_KEY in .env"}
    return {}


def _request(method: str, path: str, **kwargs: Any) -> Any:
    config_error = _validate_config()
    if config_error:
        return config_error

    try:
        response = requests.request(
            method=method,
            url=f"{BASE_URL}{path}",
            auth=AUTH,
            timeout=30,
            **kwargs,
        )
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        response_body = ""
        if exc.response is not None:
            response_body = exc.response.text
        return {"error": f"Freshworks API error: {exc}", "details": response_body}
    except requests.RequestException as exc:
        return {"error": f"Request failed: {exc}"}


def create_ticket(description: str) -> Any:
    """Create a ticket.

    Required fields in description:
    - subject: Ticket subject
    - email: Requester email
    - description: Ticket description/body

    Example:
    subject: Login issue
    email: user@example.com
    description: Unable to login since morning.
    priority: 1
    status: 2
    """
    fields = parse_description(description)
    return _request("POST", "/tickets", json=fields)


def get_ticket(ticket_id: str) -> Any:
    """Get a ticket by ID.

    Required fields:
    - ticket_id: Freshworks ticket ID
    """
    return _request("GET", f"/tickets/{ticket_id}")


def update_ticket(ticket_id: str, description: str) -> Any:
    """Update a ticket by ID.

    Required fields:
    - ticket_id: Freshworks ticket ID
    - description: key:value lines of fields to update

    Example:
    subject: Updated title
    status: 4
    priority: 2
    """
    fields = parse_description(description)
    return _request("PUT", f"/tickets/{ticket_id}", json=fields)


def list_user_tickets(user_email: str) -> Any:
    """List all tickets for a specific user email.

    Required fields:
    - user_email: Requester email
    """
    # Freshworks ticket listing supports filtering by requester email.
    return _request("GET", "/tickets", params={"email": user_email})


def add_ticket_note(ticket_id: str, description: str) -> Any:
    """Add a note to a ticket.

    Required fields:
    - ticket_id: Freshworks ticket ID
    - description: key:value lines containing at least:
      - body: Note text
      - private: true/false (optional, default true)
    """
    fields = parse_description(description)
    note_data = {
        "body": fields.get("body", ""),
        "private": fields.get("private", True),
    }
    return _request("POST", f"/tickets/{ticket_id}/notes", json=note_data)
