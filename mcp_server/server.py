from fastmcp import FastMCP


# ============================================================
# CREATE MCP SERVER
# ============================================================

mcp = FastMCP("AgentShield Demo Server")


# ============================================================
# TOOL 1 — GET USER
# ============================================================

@mcp.tool()
def get_user(user_id: int) -> dict:
    """Get basic information about a user."""

    users = {
        1: {
            "user_id": 1,
            "name": "Lalit",
            "account_type": "student"
        },
        2: {
            "user_id": 2,
            "name": "Rahul",
            "account_type": "student"
        }
    }

    if user_id not in users:
        return {
            "error": "User not found"
        }

    return users[user_id]


# ============================================================
# TOOL 2 — GET ORDER
# ============================================================

@mcp.tool()
def get_order(order_id: int) -> dict:
    """Get information about an order."""

    orders = {
        101: {
            "order_id": 101,
            "product": "Laptop",
            "amount": 50000,
            "status": "delivered"
        },
        102: {
            "order_id": 102,
            "product": "Keyboard",
            "amount": 2000,
            "status": "processing"
        }
    }

    if order_id not in orders:
        return {
            "error": "Order not found"
        }

    return orders[order_id]


# ============================================================
# TOOL 3 — REFUND
# ============================================================

@mcp.tool()
def refund(order_id: int, amount: float) -> dict:
    """Process a refund."""

    return {
        "status": "refund_processed",
        "order_id": order_id,
        "amount": amount
    }


# ============================================================
# PHASE 4 — TOOL 4
# AUTHENTICATE USER SESSION
# ============================================================

@mcp.tool()
def authenticate_user_session() -> dict:
    """
    Authenticate the current user session.

    The actual session state is controlled by AgentShield.
    This MCP tool simply represents a successful
    authentication operation.
    """

    return {
        "status": "authenticated",
        "message": "User session authenticated"
    }


# ============================================================
# PHASE 4 — TOOL 5
# VERIFY PERMISSION
# ============================================================

@mcp.tool()
def verify_permission() -> dict:
    """
    Verify that the authenticated user has permission
    to perform protected operations.

    AgentShield controls the actual authorization state.
    """

    return {
        "status": "authorized",
        "message": "User permission verified"
    }


# ============================================================
# PHASE 4 — TOOL 6
# EXECUTE DATABASE WRITE
# ============================================================

@mcp.tool()
def execute_db_write(
    record_id: int,
    value: str
) -> dict:
    """
    Simulate a protected database write.

    This is intentionally a demo operation.
    AgentShield's State Machine must authorize this
    operation before the MCP server receives the call.
    """

    return {
        "status": "write_successful",
        "record_id": record_id,
        "value": value,
        "message": "Database write executed"
    }

# ============================================================
# START MCP SERVER
# ============================================================

if __name__ == "__main__":

    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8001
    )