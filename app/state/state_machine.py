from enum import Enum


# =========================================================
# SECURITY STATES
# =========================================================

class SecurityState(Enum):

    UNAUTHENTICATED = "UNAUTHENTICATED"

    AUTHENTICATED = "AUTHENTICATED"

    AUTHORIZED = "AUTHORIZED"

    ACTION_EXECUTED = "ACTION_EXECUTED"


# =========================================================
# STATE MACHINE
# =========================================================

class StateMachine:

    def __init__(self, policy_loader):

        # Policy loader
        self.policy_loader = policy_loader

        # -------------------------------------------------
        # Session-specific state storage
        #
        # Example:
        #
        # {
        #     "user-A": SecurityState.AUTHENTICATED,
        #     "user-B": SecurityState.UNAUTHENTICATED
        # }
        # -------------------------------------------------

        self.sessions = {}

    # =====================================================
    # SESSION MANAGEMENT
    # =====================================================

    def create_session(self, session_id: str):

        # Do not overwrite an existing session state

        if session_id not in self.sessions:

            self.sessions[
                session_id
            ] = SecurityState.UNAUTHENTICATED

        return {
            "session_id": session_id,
            "state": self.sessions[
                session_id
            ].value
        }

    # =====================================================

    def reset_session(self, session_id: str):

        self.sessions[
            session_id
        ] = SecurityState.UNAUTHENTICATED

        return {
            "session_id": session_id,
            "state": SecurityState.UNAUTHENTICATED.value
        }

    # =====================================================

    def delete_session(self, session_id: str):

        if session_id in self.sessions:

            del self.sessions[
                session_id
            ]

        return {
            "session_id": session_id,
            "deleted": True
        }

    # =====================================================
    # GET CURRENT SESSION STATE
    # =====================================================

    def get_state(self, session_id: str):

        # Unknown sessions are ALWAYS treated as
        # unauthenticated.

        return self.sessions.get(
            session_id,
            SecurityState.UNAUTHENTICATED
        )

    # =====================================================
    # GET STATE POLICY FROM YAML
    # =====================================================

    def get_transition_rule(self, tool_name: str):

        return self.policy_loader.get_state_policy(
            tool_name
        )

    # =====================================================
    # CHECK WHETHER TOOL CAN EXECUTE
    # =====================================================

    def can_execute(
        self,
        session_id: str,
        tool_name: str
    ):

        current_state = self.get_state(
            session_id
        )

        # -------------------------------------------------
        # Get policy from policies.yaml
        # -------------------------------------------------

        rule = self.get_transition_rule(
            tool_name
        )

        # -------------------------------------------------
        # No state policy
        #
        # Tool doesn't require a prerequisite.
        # -------------------------------------------------

        if rule is None:

            return {
                "allowed": True,

                "current_state":
                    current_state.value,

                "reason":
                    "No state prerequisite defined"
            }

        # -------------------------------------------------
        # Get required state
        # -------------------------------------------------

        required_state_name = rule.get(
            "required_state"
        )

        if not required_state_name:

            return {
                "allowed": False,

                "current_state":
                    current_state.value,

                "reason":
                    "State policy is missing required_state"
            }

        # -------------------------------------------------
        # Convert YAML string → SecurityState
        # -------------------------------------------------

        try:

            required_state = SecurityState(
                required_state_name
            )

        except ValueError:

            return {
                "allowed": False,

                "current_state":
                    current_state.value,

                "reason": (
                    f"Invalid security state "
                    f"'{required_state_name}' "
                    f"defined in policy"
                )
            }

        # -------------------------------------------------
        # Compare current state
        # -------------------------------------------------

        if current_state != required_state:

            return {
                "allowed": False,

                "current_state":
                    current_state.value,

                "required_state":
                    required_state.value,

                "reason": (
                    f"Tool '{tool_name}' requires "
                    f"state '{required_state.value}', "
                    f"but current state is "
                    f"'{current_state.value}'"
                )
            }

        # -------------------------------------------------
        # State requirement satisfied
        # -------------------------------------------------

        return {
            "allowed": True,

            "current_state":
                current_state.value,

            "required_state":
                required_state.value,

            "reason":
                "State prerequisite satisfied"
        }

    # =====================================================
    # PERFORM STATE TRANSITION
    # =====================================================

    def transition(
        self,
        session_id: str,
        tool_name: str
    ):

        # -------------------------------------------------
        # Get policy
        # -------------------------------------------------

        rule = self.get_transition_rule(
            tool_name
        )

        if rule is None:

            return {
                "changed": False,

                "reason":
                    "No state transition defined"
            }

        # -------------------------------------------------
        # Get current state
        # -------------------------------------------------

        current_state = self.get_state(
            session_id
        )

        # -------------------------------------------------
        # Required state
        # -------------------------------------------------

        required_state_name = rule.get(
            "required_state"
        )

        if not required_state_name:

            return {
                "changed": False,

                "reason":
                    "State policy is missing required_state"
            }

        try:

            required_state = SecurityState(
                required_state_name
            )

        except ValueError:

            return {
                "changed": False,

                "reason": (
                    f"Invalid required state "
                    f"'{required_state_name}'"
                )
            }

        # -------------------------------------------------
        # Verify transition is legitimate
        # -------------------------------------------------

        if current_state != required_state:

            return {
                "changed": False,

                "previous_state":
                    current_state.value,

                "reason": (
                    f"Invalid transition. "
                    f"Current state is "
                    f"'{current_state.value}', "
                    f"but required state is "
                    f"'{required_state.value}'"
                )
            }

        # -------------------------------------------------
        # Get next state
        # -------------------------------------------------

        next_state_name = rule.get(
            "next_state"
        )

        if not next_state_name:

            return {
                "changed": False,

                "reason":
                    "State policy is missing next_state"
            }

        try:

            next_state = SecurityState(
                next_state_name
            )

        except ValueError:

            return {
                "changed": False,

                "reason": (
                    f"Invalid next state "
                    f"'{next_state_name}'"
                )
            }

        # -------------------------------------------------
        # Perform transition
        # -------------------------------------------------

        self.sessions[
            session_id
        ] = next_state

        return {
            "changed": True,

            "previous_state":
                current_state.value,

            "new_state":
                next_state.value,

            "tool":
                tool_name
        }