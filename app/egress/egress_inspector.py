class EgressInspector:
    """
    Phase 6:
    Inspects tool results before they are returned to the client.
    """

    SENSITIVE_KEYS = {
        "password",
        "passwd",
        "token",
        "api_key",
        "apikey",
        "secret",
        "access_token",
        "refresh_token",
        "authorization"
    }

    def inspect(self, result):
        """
        Inspect an MCP tool result for sensitive information.
        """

        if result is None:
            return {
                "allowed": True,
                "result": result,
                "reason": "Empty result is safe"
            }

        sensitive_key = self._find_sensitive_key(result)

        if sensitive_key is not None:
            return {
                "allowed": False,
                "result": None,
                "reason": f"Sensitive field '{sensitive_key}' detected"
            }

        return {
            "allowed": True,
            "result": result,
            "reason": "Egress result passed inspection"
        }

    def _find_sensitive_key(self, value):

        if isinstance(value, dict):

            for key, item in value.items():

                if str(key).lower() in self.SENSITIVE_KEYS:
                    return key

                found = self._find_sensitive_key(item)

                if found is not None:
                    return found

        elif isinstance(value, list):

            for item in value:

                found = self._find_sensitive_key(item)

                if found is not None:
                    return found

        return None