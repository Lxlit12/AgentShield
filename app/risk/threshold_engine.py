class ThresholdEngine:

    # =========================================================
    # RISK THRESHOLDS
    # =========================================================

    ALLOW_MAX = 30

    REVIEW_MAX = 60

    BLOCK_MAX = 100

    # =========================================================
    # EVALUATE RISK SCORE
    # =========================================================

    def evaluate(self, score: int):

        # -----------------------------------------------------
        # Validate score
        # -----------------------------------------------------

        if not isinstance(score, (int, float)):

            return {
                "decision": "BLOCK",
                "score": score,
                "reason": "Risk score must be numeric"
            }

        # -----------------------------------------------------
        # Reject invalid negative scores
        # -----------------------------------------------------

        if score < 0:

            return {
                "decision": "BLOCK",
                "score": score,
                "reason": "Risk score cannot be negative"
            }

        # -----------------------------------------------------
        # ALLOW
        # -----------------------------------------------------

        if score <= self.ALLOW_MAX:

            return {
                "decision": "ALLOW",
                "score": score,
                "reason": (
                    f"Risk score {score} is within "
                    f"the allow threshold"
                )
            }

        # -----------------------------------------------------
        # REVIEW
        # -----------------------------------------------------

        if score <= self.REVIEW_MAX:

            return {
                "decision": "REVIEW",
                "score": score,
                "reason": (
                    f"Risk score {score} requires "
                    f"additional review"
                )
            }

        # -----------------------------------------------------
        # BLOCK
        # -----------------------------------------------------

        if score <= self.BLOCK_MAX:

            return {
                "decision": "BLOCK",
                "score": score,
                "reason": (
                    f"Risk score {score} exceeds "
                    f"the review threshold"
                )
            }

        # -----------------------------------------------------
        # Scores above 100 are invalid
        # -----------------------------------------------------

        return {
            "decision": "BLOCK",
            "score": score,
            "reason": "Risk score exceeds maximum value of 100"
        }