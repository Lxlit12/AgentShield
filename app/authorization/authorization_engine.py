class AuthorizationEngine:

    def __init__(self, policy_loader):

        self.policy_loader = policy_loader

    # =========================================================
    # CHECK ROLE → TOOL PERMISSION
    # =========================================================

    def check_permission(
        self,
        role: str,
        tool_name: str
    ):

        # ---------------------------------------------
        # Check whether role exists
        # ---------------------------------------------

        role_policy = self.policy_loader.get_role_policy(
            role
        )

        if role_policy is None:

            return {
                "allowed": False,
                "role": role,
                "tool": tool_name,
                "reason": (
                    f"Unknown role '{role}'"
                )
            }

        # ---------------------------------------------
        # Get allowed tools
        # ---------------------------------------------

        allowed_tools = role_policy.get(
            "allowed_tools",
            []
        )

        # ---------------------------------------------
        # Check permission
        # ---------------------------------------------

        if tool_name not in allowed_tools:

            return {
                "allowed": False,
                "role": role,
                "tool": tool_name,
                "reason": (
                    f"Role '{role}' is not "
                    f"authorized to use tool "
                    f"'{tool_name}'"
                )
            }

        # ---------------------------------------------
        # Permission granted
        # ---------------------------------------------

        return {
            "allowed": True,
            "role": role,
            "tool": tool_name,
            "reason": "Role is authorized for this tool"
        }