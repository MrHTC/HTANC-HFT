# MCP (Model Context Protocol) Servers

This directory defines **MCP servers** that allow any AI coding tool
(opencode, Claude Code, Cursor, VS Code + GitHub Copilot, etc.)
to interact directly with the HTANC HFT trading system.

## Available MCP Servers

| Server | Endpoint | Purpose |
|--------|----------|---------|
| **trading-execution** | `/mcp/trade` | Place orders, cancel, get order status |
| **market-data** | `/mcp/market` | Real-time + historical OHLCV, order book |
| **portfolio** | `/mcp/portfolio` | Positions, P&L, balances, risk metrics |
| **signals** | `/mcp/signals` | AI-generated buy/sell/hold signals |
| **backtest** | `/mcp/backtest` | Run backtests, retrieve performance reports |

## How to Use

### 1. Start the system (paper mode by default):
```bash
docker compose up --build
```

### 2. Configure your AI tool to use the MCP servers

**opencode** – add to your `.opencode/mcp.json`:
```json
{
  "mcpServers": {
    "htanc-trading": {
      "command": "node",
      "args": ["path/to/mcp-client.js"],
      "env": {
        "API_URL": "http://localhost:8000",
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

**Claude Code** – run:
```
claude mcp add htanc-trading -- http://localhost:8000/mcp
```

**Cursor** – add in Settings → MCP Servers.

### 3. Authenticate
All trading endpoints require an API key.
Set `API_KEY` in your `.env` file and pass it in the `X-API-Key` header.

## MCP Protocol

Each endpoint follows the standard MCP tool format:

```json
{
  "tool": "place_order",
  "params": {
    "symbol": "RELIANCE",
    "qty": 10,
    "side": "BUY",
    "order_type": "MARKET"
  }
}
```

Full MCP specification: https://modelcontextprotocol.io
