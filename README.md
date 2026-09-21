@"
# AgentShield

AgentShield is a local security gateway for MCP-based AI agents.

## Architecture

Client / Swagger
        ↓
AgentShield Gateway
        ↓
Ingress Guard
        ↓
Tool Allowlist
        ↓
Schema & Parameter Validation
        ↓
State Machine
        ↓
Authorization & Risk Engine
        ↓
Egress Security
        ↓
Audit Logging
        ↓
MCP Server

## Security Phases

- Phase 1 — Foundation
- Phase 2 — Ingress Guard
- Phase 3 — Tool Security
- Phase 4 — State Machine
- Phase 5 — Authorization & Risk Engine
- Phase 6 — Egress Security
- Phase 7 — Audit & Security Dashboard

## Project Structure

```text
app/          AgentShield gateway and security components
mcp_server/   Demo MCP server
policies/     Security policies
logs/         Local audit logs