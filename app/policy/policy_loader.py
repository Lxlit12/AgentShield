import yaml
from pathlib import Path


class PolicyLoader:

    def __init__(self, policy_path: str):

        self.policy_path = Path(policy_path)

        self.policies = self._load_policies()

    # =========================================================
    # LOAD POLICIES
    # =========================================================

    def _load_policies(self):

        if not self.policy_path.exists():

            raise FileNotFoundError(
                f"Policy file not found: {self.policy_path}"
            )

        with open(
            self.policy_path,
            "r",
            encoding="utf-8"
        ) as file:

            policies = yaml.safe_load(file)

        if not policies:

            raise ValueError(
                "Policy file is empty"
            )

        return policies

    # =========================================================
    # TOOL POLICY
    # =========================================================

    def get_tool_policy(self, tool_name: str):

        tools = self.policies.get(
            "tools",
            {}
        )

        return tools.get(tool_name)

    # =========================================================
    # TOOL ALLOWLIST
    # =========================================================

    def is_tool_enabled(self, tool_name: str) -> bool:

        tool_policy = self.get_tool_policy(
            tool_name
        )

        if tool_policy is None:
            return False

        return tool_policy.get(
            "enabled",
            False
        )

    def is_tool_allowed(self, tool_name: str) -> bool:

        tool_policy = self.get_tool_policy(
            tool_name
        )

        if tool_policy is None:
            return False

        return tool_policy.get(
            "enabled",
            False
        )

    # =========================================================
    # STATE MACHINE POLICY
    # =========================================================

    def get_state_policy(self, tool_name: str):

        state_machine = self.policies.get(
            "state_machine",
            {}
        )

        return state_machine.get(
            tool_name
        )
    # =========================================================
    # AUTHORIZATION POLICY
    # =========================================================

    def get_role_policy(self, role: str):

        authorization = self.policies.get(
            "authorization",
            {}
        )

        roles = authorization.get(
            "roles",
            {}
        )

        return roles.get(role)

    # =========================================================
    # CHECK ROLE TOOL PERMISSION
    # =========================================================

    def is_role_allowed(
        self,
        role: str,
        tool_name: str
    ) -> bool:

        role_policy = self.get_role_policy(
            role
        )

        if role_policy is None:
            return False

        allowed_tools = role_policy.get(
            "allowed_tools",
            []
        )

        return tool_name in allowed_tools

    # =========================================================
    # RISK POLICY
    # =========================================================

    def get_risk_policy(self, tool_name: str):

        risk = self.policies.get(
            "risk",
            {}
        )

        tools = risk.get(
            "tools",
            {}
        )

        return tools.get(
            tool_name
        )