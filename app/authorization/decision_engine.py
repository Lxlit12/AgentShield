from app.authorization.authorization_engine import AuthorizationEngine
from app.risk.threshold_engine import ThresholdEngine


class DecisionEngine:

    def __init__(
        self,
        policy_loader
    ):

        self.authorization_engine = (
            AuthorizationEngine(
                policy_loader
            )
        )

        self.threshold_engine = (
            ThresholdEngine()
        )

    # =========================================================
    # FINAL SECURITY DECISION
    # =========================================================

    def evaluate(
        self,
        role: str,
        tool_name: str,
        risk_score: int
    ):

        # -----------------------------------------------------
        # STEP 1 — AUTHORIZATION
        # -----------------------------------------------------

        authorization_result = (
            self.authorization_engine.check_permission(
                role,
                tool_name
            )
        )

        # -----------------------------------------------------
        # AUTHORIZATION FAILURE ALWAYS WINS
        # -----------------------------------------------------

        if not authorization_result["allowed"]:

            return {
                "decision": "BLOCK",
                "role": role,
                "tool": tool_name,
                "risk_score": risk_score,
                "authorization": authorization_result,
                "reason": (
                    "Role is not authorized "
                    "to use this tool"
                )
            }

        # -----------------------------------------------------
        # STEP 2 — RISK THRESHOLD
        # -----------------------------------------------------

        risk_result = (
            self.threshold_engine.evaluate(
                risk_score
            )
        )

        # -----------------------------------------------------
        # FINAL DECISION
        # -----------------------------------------------------

        return {
            "decision": risk_result["decision"],
            "role": role,
            "tool": tool_name,
            "risk_score": risk_score,
            "authorization": authorization_result,
            "risk": risk_result,
            "reason": risk_result["reason"]
        }