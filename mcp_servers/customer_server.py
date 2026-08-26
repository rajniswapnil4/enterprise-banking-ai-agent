from mcp.server.mcpserver import MCPServer

# Create the MCP server
mcp = MCPServer("Customer Service")


# Mock customer database
CUSTOMERS = {
    "CUST001": {
        "name": "John Smith",
        "account_type": "Current Account",
        "status": "Active",
        "city": "Johannesburg"
    },
    "CUST002": {
        "name": "Sarah Williams",
        "account_type": "Savings Account",
        "status": "Active",
        "city": "Cape Town"
    }
}


@mcp.tool()
def get_customer(customer_id: str) -> dict:
    """Retrieve customer information using a customer ID."""

    customer = CUSTOMERS.get(customer_id)

    if not customer:
        return {
            "error": f"Customer {customer_id} was not found"
        }

    return customer


@mcp.tool()
def get_customer_accounts(customer_id: str) -> list:
    """Retrieve bank accounts belonging to a customer."""

    accounts = {
        "CUST001": [
            {
                "account_number": "XXXX-1234",
                "account_type": "Current Account",
                "balance": 125000.50,
                "currency": "ZAR"
            },
            {
                "account_number": "XXXX-5678",
                "account_type": "Savings Account",
                "balance": 85000.75,
                "currency": "ZAR"
            }
        ],
        "CUST002": [
            {
                "account_number": "XXXX-9012",
                "account_type": "Savings Account",
                "balance": 45000.00,
                "currency": "ZAR"
            }
        ]
    }

    return accounts.get(customer_id, [])


if __name__ == "__main__":
    mcp.run()