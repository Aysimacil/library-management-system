import json
import logging
from pathlib import Path
import traceback


class SafeJSONFormatter(logging.Formatter):
    """Keep operational context without request bodies, secrets or exception text."""
    EVENTS = {"cover_publish_retry_required", "readiness_failed"}

    def format(self, record):
        payload = {
            "time": self.formatTime(record), "level": record.levelname,
            "logger": record.name,
            "event": record.msg if isinstance(record.msg, str) and record.msg in self.EVENTS else "application_log",
        }
        if record.exc_info and record.exc_info[0]:
            payload["exception_type"] = record.exc_info[0].__name__
            payload["frames"] = [
                {"file": Path(frame.filename).name, "line": frame.lineno, "function": frame.name}
                for frame in traceback.extract_tb(record.exc_info[2])
            ]
        if getattr(record, "status_code", None):
            payload["status"] = record.status_code
        request = getattr(record, "request", None)
        match = getattr(request, "resolver_match", None)
        if match:
            payload["route"] = match.route
        return json.dumps(payload, ensure_ascii=False)
