class SchemaValidator:

    def __init__(self, policy_loader):
        self.policy_loader = policy_loader

    def validate(self, tool_name: str, arguments: dict):

        # Get tool policy
        tool_policy = self.policy_loader.get_tool_policy(
            tool_name
        )

        if tool_policy is None:
            return {
                "valid": False,
                "reason": f"Tool '{tool_name}' is not defined"
            }

        parameter_rules = tool_policy.get(
            "parameters",
            {}
        )

        # Check required parameters
        for parameter_name, rules in parameter_rules.items():

            required = rules.get("required", False)

            if required and parameter_name not in arguments:

                return {
                    "valid": False,
                    "reason": (
                        f"Missing required parameter: "
                        f"{parameter_name}"
                    )
                }

        # Check parameter types
        for parameter_name, value in arguments.items():

            # Reject unknown parameters
            if parameter_name not in parameter_rules:

                return {
                    "valid": False,
                    "reason": (
                        f"Unexpected parameter: "
                        f"{parameter_name}"
                    )
                }

            rules = parameter_rules[parameter_name]

            expected_type = rules.get("type")

            if not self._check_type(
                value,
                expected_type
            ):

                return {
                    "valid": False,
                    "reason": (
                        f"Invalid type for '{parameter_name}'. "
                        f"Expected {expected_type}"
                    )
                }

        return {
            "valid": True,
            "reason": "Schema validation successful"
        }

    def _check_type(self, value, expected_type):

        if expected_type == "integer":
            return (
                isinstance(value, int)
                and not isinstance(value, bool)
            )

        if expected_type == "number":
            return (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
            )

        if expected_type == "string":
            return isinstance(value, str)

        if expected_type == "boolean":
            return isinstance(value, bool)

        return False