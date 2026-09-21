class ParameterValidator:

    def __init__(self, policy_loader):
        self.policy_loader = policy_loader

    def validate(self, tool_name: str, arguments: dict):

        # --------------------------------
        # 1. TOOL ALLOWLIST CHECK
        # --------------------------------

        if not self.policy_loader.is_tool_allowed(tool_name):

            return {
                "allowed": False,
                "reason": (
                    f"Tool '{tool_name}' is not allowed "
                    "by security policy"
                )
            }

        # --------------------------------
        # 2. GET TOOL POLICY
        # --------------------------------

        tool_policy = self.policy_loader.get_tool_policy(
            tool_name
        )

        # --------------------------------
        # 3. PARAMETER RULES
        # --------------------------------

        parameter_rules = tool_policy.get(
            "parameters",
            {}
        )

        # --------------------------------
        # 4. VALIDATE PARAMETERS
        # --------------------------------

        for parameter_name, rules in parameter_rules.items():

            if parameter_name not in arguments:

                return {
                    "allowed": False,
                    "reason": (
                        f"Missing parameter: "
                        f"{parameter_name}"
                    )
                }

            value = arguments[parameter_name]

            # Minimum boundary
            if "min" in rules and value < rules["min"]:

                return {
                    "allowed": False,
                    "reason": (
                        f"{parameter_name} is below "
                        f"minimum value of {rules['min']}"
                    )
                }

            # Maximum boundary
            if "max" in rules and value > rules["max"]:

                return {
                    "allowed": False,
                    "reason": (
                        f"{parameter_name} exceeds "
                        f"maximum value of {rules['max']}"
                    )
                }

        # --------------------------------
        # 5. EVERYTHING PASSED
        # --------------------------------

        return {
            "allowed": True,
            "reason": "Security policy validation successful"
        }