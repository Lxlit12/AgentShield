from datetime import datetime, timezone


class AuditEvent:

    def __init__(
        self,
        session_id,
        role,
        tool,
        status,
        authorization=None,
        risk_level=None,
        risk_score=None,
        decision=None,
        egress=None,
        error=None
    ):
        self.timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        self.session_id = session_id
        self.role = role
        self.tool = tool
        self.status = status

        self.authorization = authorization
        self.risk_level = risk_level
        self.risk_score = risk_score
        self.decision = decision
        self.egress = egress
        self.error = error

    def to_dict(self):

        return {
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "role": self.role,
            "tool": self.tool,
            "status": self.status,
            "authorization": self.authorization,
            "risk_level": self.risk_level,
            "risk_score": self.risk_score,
            "decision": self.decision,
            "egress": self.egress,
            "error": self.error
        }