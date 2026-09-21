from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field

from app.gateway.proxy import call_mcp_tool

from app.policy.policy_loader import PolicyLoader
from app.policy.schema_validator import SchemaValidator
from app.policy.parameter_validator import ParameterValidator

from app.ingress.ingress_guard import IngressGuard
from app.ingress.semantic_matcher import SemanticScopeMatcher

from app.state.state_machine import StateMachine

from app.authorization.decision_engine import DecisionEngine
from app.risk.risk_engine import RiskEngine

from app.egress.egress_inspector import EgressInspector

from app.audit.audit_event import AuditEvent
from app.audit.audit_logger import AuditLogger
audit_logger = AuditLogger()

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse

from app.dashboard import create_dashboard

# ============================================================
# AgentShield Gateway
# ============================================================

app = FastAPI(
    title="AgentShield Gateway",
    version="0.1.0"
)


# ============================================================
# POLICY LOADER
# ============================================================

policy_loader = PolicyLoader(
    "policies/policies.yaml"
)


# ============================================================
# PHASE 3 — TOOL SECURITY
# ============================================================

schema_validator = SchemaValidator(
    policy_loader
)

parameter_validator = ParameterValidator(
    policy_loader
)


# ============================================================
# PHASE 4 — STATE MACHINE
# ============================================================

state_machine = StateMachine(
    policy_loader
)


# ============================================================
# PHASE 5 — AUTHORIZATION
# ============================================================

decision_engine = DecisionEngine(
    policy_loader
)


# ============================================================
# PHASE 5 — RISK ENGINE
# ============================================================

risk_engine = RiskEngine(
    policy_loader
)


# ============================================================
# PHASE 6 — EGRESS SECURITY
# ============================================================

egress_inspector = EgressInspector()


# ============================================================
# PHASE 7 — AUDIT LOGGER
# ============================================================

audit_logger = AuditLogger()


# ============================================================
# PHASE 2 — INGRESS SECURITY
# ============================================================

ingress_guard = IngressGuard()

semantic_matcher = SemanticScopeMatcher(
    threshold=0.35
)


# ============================================================
# REQUEST MODELS
# ============================================================

class ToolCallRequest(BaseModel):

    tool_name: str

    arguments: dict = Field(
        default_factory=dict
    )


class PromptCheckRequest(BaseModel):

    prompt: str


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def home():

    return {
        "message": "AgentShield Gateway is running",
        "status": "active",
        "version": "0.1.0"
    }


# ============================================================
# PHASE 2 — INGRESS GUARD
# ============================================================

@app.post("/prompt/check")
async def check_prompt(
    request: PromptCheckRequest
):

    prompt = request.prompt

    # --------------------------------------------------------
    # SECURITY CHECK 1
    # REGEX PROMPT INJECTION DETECTION
    # --------------------------------------------------------

    regex_result = ingress_guard.check_regex(
        prompt
    )

    if not regex_result["allowed"]:

        raise HTTPException(
            status_code=403,
            detail={
                "error": "PROMPT_INJECTION_DETECTED",
                "method": "regex",
                "reason": regex_result["reason"]
            }
        )

    # --------------------------------------------------------
    # SECURITY CHECK 2
    # MINILM SEMANTIC SCOPE
    # --------------------------------------------------------

    semantic_result = semantic_matcher.check_scope(
        prompt
    )

    if not semantic_result["allowed"]:

        raise HTTPException(
            status_code=403,
            detail={
                "error": "PROMPT_OUT_OF_SCOPE",
                "method": "semantic",
                "similarity":
                    semantic_result["similarity"],
                "threshold":
                    semantic_result["threshold"],
                "matched_scope":
                    semantic_result["matched_scope"]
            }
        )

    # --------------------------------------------------------
    # PROMPT PASSED INGRESS SECURITY
    # --------------------------------------------------------

    return {
        "status": "allowed",
        "prompt": prompt,

        "security": {
            "regex": "passed",
            "semantic": "passed"
        },

        "similarity":
            semantic_result["similarity"],

        "threshold":
            semantic_result["threshold"],

        "matched_scope":
            semantic_result["matched_scope"]
    }


# ============================================================
# PHASE 3 + PHASE 4 + PHASE 5 + PHASE 6 + PHASE 7
# MCP TOOL SECURITY PIPELINE
# ============================================================
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    events = audit_logger.read_events()
    return create_dashboard(events)


@app.get("/audit/events")
def get_audit_events():
    events = audit_logger.read_events()

    return {
        "status": "success",
        "count": len(events),
        "events": events
    }

@app.post("/tools/call")
async def tools_call(
    request: ToolCallRequest,
    x_session_id: str = Header(...),
    x_user_role: str = Header(...)
):

    tool_name = request.tool_name

    arguments = request.arguments

    session_id = x_session_id

    role = x_user_role


    # ========================================================
    # PHASE 3 — SECURITY CHECK 1
    # TOOL ALLOWLIST
    # ========================================================

    if not policy_loader.is_tool_allowed(
        tool_name
    ):

        raise HTTPException(
            status_code=403,
            detail={
                "error": "TOOL_NOT_ALLOWED",
                "tool": tool_name,
                "reason": (
                    f"Tool '{tool_name}' "
                    "is not allowed by security policy"
                )
            }
        )


    # ========================================================
    # PHASE 3 — SECURITY CHECK 2
    # SCHEMA VALIDATION
    # ========================================================

    schema_result = schema_validator.validate(
        tool_name,
        arguments
    )

    if not schema_result["valid"]:

        raise HTTPException(
            status_code=403,
            detail={
                "error": "SCHEMA_VALIDATION_FAILED",
                "tool": tool_name,
                "reason": schema_result["reason"]
            }
        )


    # ========================================================
    # PHASE 3 — SECURITY CHECK 3
    # PARAMETER BOUNDARIES
    # ========================================================

    parameter_result = parameter_validator.validate(
        tool_name,
        arguments
    )

    if not parameter_result["allowed"]:

        raise HTTPException(
            status_code=403,
            detail={
                "error": "PARAMETER_VALIDATION_FAILED",
                "tool": tool_name,
                "reason":
                    parameter_result["reason"]
            }
        )


    # ========================================================
    # PHASE 4 — SECURITY CHECK 4
    # STATE MACHINE
    # ========================================================

    state_result = state_machine.can_execute(
        session_id,
        tool_name
    )

    if not state_result["allowed"]:

        raise HTTPException(
            status_code=403,
            detail={
                "error":
                    "STATE_PREREQUISITE_FAILED",

                "tool":
                    tool_name,

                "session_id":
                    session_id,

                "current_state":
                    state_result["current_state"],

                "required_state":
                    state_result.get(
                        "required_state"
                    ),

                "reason":
                    state_result["reason"]
            }
        )


    # ========================================================
    # PHASE 5 — RISK SCORING
    # ========================================================

    risk_result = risk_engine.calculate_score(
        tool_name
    )

    risk_score = risk_result["score"]


    # ========================================================
    # PHASE 5 — AUTHORIZATION + RISK DECISION
    # ========================================================

    decision_result = decision_engine.evaluate(
        role,
        tool_name,
        risk_score
    )


    # ========================================================
    # BLOCK
    # ========================================================

    if decision_result["decision"] == "BLOCK":

        raise HTTPException(
            status_code=403,
            detail={
                "error":
                    "AUTHORIZATION_BLOCKED",

                "tool":
                    tool_name,

                "session_id":
                    session_id,

                "role":
                    role,

                "risk":
                    risk_result,

                "decision":
                    decision_result
            }
        )


    # ========================================================
    # REVIEW
    # ========================================================

    if decision_result["decision"] == "REVIEW":

        raise HTTPException(
            status_code=403,
            detail={
                "error":
                    "RISK_REVIEW_REQUIRED",

                "tool":
                    tool_name,

                "session_id":
                    session_id,

                "role":
                    role,

                "risk":
                    risk_result,

                "decision":
                    decision_result
            }
        )


    # ========================================================
    # ALL SECURITY CHECKS PASSED
    # ========================================================

    try:

        result = await call_mcp_tool(
            tool_name,
            arguments
        )


        # ====================================================
        # PHASE 6 — EGRESS INSPECTION
        # ====================================================

        egress_result = egress_inspector.inspect(
            result
        )

        if not egress_result["allowed"]:

            raise HTTPException(
                status_code=403,
                detail={
                    "error": "EGRESS_BLOCKED",
                    "tool": tool_name,
                    "session_id": session_id,
                    "reason": egress_result["reason"]
                }
            )

        result = egress_result["result"]


        # ====================================================
        # PHASE 7 — AUDIT SUCCESSFUL REQUEST
        # ====================================================

        audit_event = AuditEvent(
            session_id=session_id,
            role=role,
            tool=tool_name,
            status="success",
            authorization="passed",
            risk_level=risk_result["level"],
            risk_score=risk_result["score"],
            decision=decision_result["decision"],
            egress="passed"
        )

        audit_logger.log(
            audit_event
        )


        # ====================================================
        # PHASE 4 — STATE TRANSITION
        # ====================================================

        transition_result = state_machine.transition(
            session_id,
            tool_name
        )


        # ====================================================
        # SUCCESS RESPONSE
        # ====================================================

        return {

            "status":
                "success",

            "tool":
                tool_name,

            "security": {

                "allowlist":
                    "passed",

                "schema":
                    "passed",

                "parameters":
                    "passed",

                "state":
                    "passed",

                "authorization":
                    "passed",

                "risk":
                    "passed",

                "egress":
                    "passed",

                "audit":
                    "logged"
            },

            "identity": {

                "session_id":
                    session_id,

                "role":
                    role
            },

            "risk": {

                "level":
                    risk_result["level"],

                "score":
                    risk_result["score"],

                "decision":
                    decision_result["decision"]
            },

            "session": {

                "session_id":
                    session_id,

                "state_transition":
                    transition_result
            },

            "result":
                result
        }


    # ========================================================
    # SECURITY BLOCK FROM EGRESS
    # ========================================================

    except HTTPException:
        raise


    # ========================================================
    # MCP FAILURE
    # ========================================================

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )