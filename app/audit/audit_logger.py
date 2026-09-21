import json
import os

from app.audit.audit_event import AuditEvent


class AuditLogger:

    def __init__(self, log_file="logs/audit.log"):

        self.log_file = log_file

        log_directory = os.path.dirname(
            self.log_file
        )

        if log_directory:
            os.makedirs(
                log_directory,
                exist_ok=True
            )

    def log(self, event: AuditEvent):

        with open(
            self.log_file,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                json.dumps(
                    event.to_dict()
                ) + "\n"
            )

    def read_events(self):

        if not os.path.exists(
            self.log_file
        ):
            return []

        events = []

        with open(
            self.log_file,
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                events.append(
                    json.loads(line)
                )

        return events