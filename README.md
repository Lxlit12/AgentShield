# AgentShield

### Security Gateway for MCP-Based AI Agents

AgentShield is a modular security gateway designed to place a policy-driven security boundary between AI agents and MCP tool execution.

It evaluates tool requests through multiple security layers, including ingress inspection, policy and schema validation, session-state enforcement, authorization, risk assessment, egress inspection, and structured security auditing.

> **Status:** Phase 1–7 implemented
> **Project type:** Security engineering / AI agent security research project

---

## Overview

As AI agents increasingly interact with external tools and services, tool execution becomes an important security boundary.

AgentShield addresses this boundary by introducing a dedicated gateway that evaluates requests before they reach the underlying MCP server.

The architecture follows a defense-in-depth approach:

```text
AI Agent / Client
       │
       ▼
┌──────────────────────┐
│   AgentShield        │
│   Security Gateway   │
└──────────┬───────────┘
           │
           ▼
     Ingress Guard
           │
           ▼
 Tool Allowlist / Policy
           │
           ▼
 Schema & Parameter
     Validation
           │
           ▼
     State Machine
           │
           ▼
 Authorization Engine
           │
           ▼
      Risk Engine
           │
           ▼
    Egress Inspector
           │
           ▼
     Audit Logger
           │
           ▼
      MCP Server
```

Each layer provides an independent security control and contributes to the final request decision.

---

## Security Pipeline

A request entering AgentShield passes through the following stages:

| Layer                    | Responsibility                                     |
| ------------------------ | -------------------------------------------------- |
| **Ingress**              | Inspects and validates incoming requests           |
| **Tool Policy**          | Determines whether the requested tool is permitted |
| **Schema Validation**    | Validates the structure of tool requests           |
| **Parameter Validation** | Enforces configured parameter constraints          |
| **State Machine**        | Controls valid session/action transitions          |
| **Authorization**        | Evaluates role-based tool permissions              |
| **Risk Engine**          | Calculates risk level and risk score               |
| **Egress**               | Inspects outgoing tool responses                   |
| **Audit**                | Records security decisions and events              |

The architecture intentionally separates these responsibilities to make the security pipeline easier to reason about, test, and extend.

---

# Architecture

```text
                    ┌─────────────────┐
                    │   AI Agent /    │
                    │      Client     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Gateway     │
                    │ Request Handler │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Ingress Guard   │
                    │ Semantic Match  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Policy Engine   │
                    │ Schema / Params │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ State Machine   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Authorization   │
                    │ Decision Engine │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Risk Engine   │
                    │   Thresholds    │
                    └────────┬────────┘
                             │
                       ┌─────┴─────┐
                       │           │
                       ▼           ▼
                     DENY        ALLOW
                                   │
                                   ▼
                          ┌─────────────────┐
                          │ Egress Inspector│
                          └────────┬────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │   Audit Logger  │
                          └────────┬────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │    MCP Server   │
                          └─────────────────┘
```

---

# Core Components

## Ingress Security

Located in:

```text
app/ingress/
├── ingress_guard.py
└── semantic_matcher.py
```

The ingress layer provides the first security boundary for incoming requests.

Responsibilities include request inspection and semantic matching before requests enter the downstream security pipeline.

---

## Policy Enforcement

Located in:

```text
app/policy/
├── policy_loader.py
├── schema_validator.py
└── parameter_validator.py
```

Policy enforcement provides configuration-driven controls for:

* Tool availability
* Request schemas
* Required parameters
* Parameter types
* Parameter constraints

Policies are defined in:

```text
policies/policies.yaml
```

This keeps security rules separate from application logic.

---

## Session State Management

Located in:

```text
app/state/
└── state_machine.py
```

AgentShield uses a state-machine model to represent valid security transitions.

For example:

```text
UNAUTHENTICATED
        │
        ▼
AUTHENTICATED
        │
        ▼
AUTHORIZED
        │
        ▼
ACTION_EXECUTED
```

This prevents sensitive operations from being treated as independent requests without considering the current session state.

---

## Authorization

Located in:

```text
app/authorization/
├── authorization_engine.py
└── decision_engine.py
```

Authorization determines whether a given role is permitted to invoke a particular tool.

For example, the current policy distinguishes between roles such as:

```text
student
admin
```

with different tool permissions.

Unauthorized tool requests are rejected by the gateway.

---

## Risk Assessment

Located in:

```text
app/risk/
├── risk_engine.py
└── threshold_engine.py
```

AgentShield separates authorization from risk evaluation.

A request can therefore be:

```text
Authorized
     +
Risk Evaluated
     ↓
Final Security Decision
```

Risk classifications currently include levels such as:

```text
LOW
MEDIUM
HIGH
```

with associated risk scores and threshold-based decisions.

---

## Egress Security

Located in:

```text
app/egress/
└── egress_inspector.py
```

Egress inspection provides a security boundary after the internal authorization and risk pipeline.

A request that passes authorization can still be subjected to outgoing-response inspection before the result is returned.

---

## Audit & Observability

Located in:

```text
app/audit/
├── audit_event.py
└── audit_logger.py
```

Phase 7 introduced structured security audit events.

An audit event can contain:

```json
{
  "timestamp": "2026-09-20T14:38:22.712826+00:00",
  "session_id": "phase7-test-session",
  "role": "student",
  "tool": "get_user",
  "status": "success",
  "authorization": "passed",
  "risk_level": "LOW",
  "risk_score": 10,
  "decision": "ALLOW",
  "egress": "passed",
  "error": null
}
```

This provides traceability for security decisions and supports post-execution analysis.

---

# Security Validation

AgentShield has been tested against authorization and security-policy scenarios during development.

Examples include:

### Authorized request

```text
HTTP 200
```

with:

```text
allowlist       → passed
schema          → passed
parameters      → passed
state           → passed
authorization   → passed
risk            → passed
egress          → passed
decision        → ALLOW
```

### Unauthorized request

Security-policy violations were validated to return:

```text
HTTP 403
```

Examples included attempts to:

* Invoke restricted tools using an unauthorized role
* Bypass role-based authorization
* Use invalid or unknown roles
* Manipulate role casing
* Access privileged operations without authorization

These tests form part of the project's Phase 5 security validation.

---

# Project Structure

```text
AgentShield/
│
├── app/
│   ├── audit/
│   │   ├── audit_event.py
│   │   └── audit_logger.py
│   │
│   ├── authorization/
│   │   ├── authorization_engine.py
│   │   └── decision_engine.py
│   │
│   ├── config/
│   │   └── settings.py
│   │
│   ├── egress/
│   │   └── egress_inspector.py
│   │
│   ├── gateway/
│   │   ├── proxy.py
│   │   └── request_handler.py
│   │
│   ├── ingress/
│   │   ├── ingress_guard.py
│   │   └── semantic_matcher.py
│   │
│   ├── policy/
│   │   ├── parameter_validator.py
│   │   ├── policy_loader.py
│   │   └── schema_validator.py
│   │
│   ├── risk/
│   │   ├── __init__.py
│   │   ├── risk_engine.py
│   │   └── threshold_engine.py
│   │
│   ├── state/
│   │   └── state_machine.py
│   │
│   ├── dashboard.py
│   └── main.py
│
├── mcp_server/
│   └── server.py
│
├── policies/
│   └── policies.yaml
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# Development Roadmap

| Phase | Capability                     |  Status |
| :---: | ------------------------------ | :-----: |
|   1   | Foundation & Gateway           |    ✅    |
|   2   | Ingress Security               |    ✅    |
|   3   | MCP Tool Security              |    ✅    |
|   4   | Session State Machine          |    ✅    |
|   5   | Authorization & Risk           |    ✅    |
|   6   | Egress Security                |    ✅    |
|   7   | Audit & Dashboard              |    ✅    |
|   8   | Extended Security Capabilities | Planned |

---

# Installation

## Requirements

* Python 3.x
* Git
* Windows, Linux, or macOS
* Python virtual environment

## Clone

```bash
git clone https://github.com/Lxlit12/AgentShield.git
cd AgentShield
```

## Create virtual environment

### Windows

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

---

# Configuration

AgentShield uses policy configuration stored under:

```text
policies/policies.yaml
```

Environment-specific configuration can be placed in:

```text
.env
```

A template is provided as:

```text
.env.example
```

Sensitive environment files are excluded from version control through `.gitignore`.

---

# Running Locally

The repository contains the AgentShield gateway and a demonstration MCP server.

Main gateway:

```text
app/main.py
```

MCP server:

```text
mcp_server/server.py
```

The exact startup configuration depends on the local development environment and installed dependencies.

---

# Design Principles

### Defense in Depth

Security is distributed across multiple independent layers.

### Least Privilege

Roles are granted access only to explicitly permitted tools.

### Policy-Driven Controls

Security rules are maintained in policy configuration rather than being entirely hard-coded.

### Separation of Concerns

Each security capability has a dedicated module.

### Explicit Decisions

Security decisions expose authorization and risk information rather than silently executing tool calls.

### Auditability

Important security events are recorded in structured form.

### Extensibility

Individual security layers can be extended without redesigning the entire gateway.

---

# Limitations

AgentShield is currently a **development and security-engineering project**.

It should not be interpreted as:

* A production security certification
* A guarantee of complete protection against prompt injection
* A complete MCP security standard
* A replacement for infrastructure security
* A replacement for authentication or network-level controls
* Proof that arbitrary AI-agent attacks can be detected

Production deployments would require additional security review, threat modeling, testing, monitoring, and operational controls.

---

# Future Development

Potential areas for future work include:

* Expanded adversarial testing
* Automated security regression tests
* Policy versioning
* Improved identity and session management
* Expanded MCP tool coverage
* Security metrics and analytics
* Containerized deployment
* CI/CD security validation
* Enhanced dashboard capabilities
* Additional threat-detection mechanisms

---

# Project Objective

AgentShield explores how a dedicated security gateway can provide a structured control boundary around AI-agent tool execution.

The project brings together:

```text
AI Agents
    +
MCP Tool Execution
    +
Policy Enforcement
    +
Authorization
    +
Risk Assessment
    +
Egress Inspection
    +
Auditability
```

The result is a modular security architecture intended for experimentation, learning, and further security engineering development.

---

# Author

**Lalit Aditya**

GitHub:
https://github.com/Lxlit12

Repository:
https://github.com/Lxlit12/AgentShield

---

## Project Status

**Phase 1–7 completed.**

Current architecture:

```text
Ingress
   ↓
Policy
   ↓
Schema
   ↓
Parameters
   ↓
State
   ↓
Authorization
   ↓
Risk
   ↓
Egress
   ↓
Audit
   ↓
Dashboard
```

**Next milestone: Phase 8**
