class RiskEngine:

    # =========================================================
    # RISK LEVEL → NUMERICAL SCORE
    # =========================================================

    RISK_SCORES = {
        "LOW": 10,
        "MEDIUM": 40,
        "HIGH": 70,
        "CRITICAL": 100
    }

    def __init__(self, policy_loader):

        self.policy_loader = policy_loader

    # =========================================================
    # GET TOOL RISK POLICY
    # =========================================================

    def get_risk_level(self, tool_name: str):

        risk_policy = self.policy_loader.get_risk_policy(
            tool_name
        )

        if risk_policy is None:

            return None

        return risk_policy.get(
            "level"
        )

    # =========================================================
    # CALCULATE RISK SCORE
    # =========================================================

    def calculate_score(self, tool_name: str):

        risk_level = self.get_risk_level(
            tool_name
        )

        # No risk policy
        if risk_level is None:

            return {
                "tool": tool_name,
                "level": None,
                "score": 0,
                "reason": "No risk policy defined"
            }

        # Invalid risk level
        if risk_level not in self.RISK_SCORES:

            return {
                "tool": tool_name,
                "level": risk_level,
                "score": 0,
                "reason": (
                    f"Invalid risk level "
                    f"'{risk_level}'"
                )
            }

        score = self.RISK_SCORES[
            risk_level
        ]

        return {
            "tool": tool_name,
            "level": risk_level,
            "score": score,
            "reason": "Risk score calculated successfully"
        }