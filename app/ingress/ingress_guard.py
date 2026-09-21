import re


class IngressGuard:

    def __init__(self):

        # Known prompt-injection patterns
        self.injection_patterns = [

            r"ignore\s+(all\s+)?previous\s+instructions",

            r"ignore\s+(all\s+)?prior\s+instructions",

            r"disregard\s+(all\s+)?previous\s+instructions",

            r"disregard\s+(all\s+)?prior\s+instructions",

            r"forget\s+(all\s+)?previous\s+instructions",

            r"override\s+(the\s+)?system\s+instructions",

            r"bypass\s+(the\s+)?system\s+instructions",

            r"you\s+are\s+now\s+unrestricted",

            r"you\s+are\s+now\s+free",

            r"act\s+as\s+an?\s+unrestricted",

            r"reveal\s+(the\s+)?system\s+prompt",

            r"show\s+(me\s+)?(the\s+)?system\s+prompt",

            r"print\s+(the\s+)?system\s+prompt",
        ]

        self.compiled_patterns = [
            re.compile(
                pattern,
                re.IGNORECASE
            )
            for pattern in self.injection_patterns
        ]


    def check_regex(self, prompt: str):

        """
        Check the prompt against known
        prompt-injection patterns.
        """

        for pattern in self.compiled_patterns:

            if pattern.search(prompt):

                return {
                    "allowed": False,
                    "detected": True,
                    "method": "regex",
                    "reason": "Prompt injection detected"
                }

        return {
            "allowed": True,
            "detected": False,
            "method": "regex",
            "reason": "No known injection pattern detected"
        }