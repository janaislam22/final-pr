
from Engine.detectors.base_detector import BaseBugDetector


class FanOutDetector(BaseBugDetector):
    """Detects possible JOIN fan-out using execution row counts."""

    def detect(self, parsed_steps: list, execution_results: list) -> dict | None:
        if not isinstance(execution_results, list):
            return None

        previous_rows = None

        for result in execution_results:
            if not isinstance(result, dict):
                continue

            step_type = str(result.get("step_type", "")).upper()
            rows = result.get("rows")

            if not isinstance(rows, (int, float)):
                continue

            if step_type in {"BASE_TABLE", "TABLE"}:
                previous_rows = rows
                continue

            if step_type == "JOIN":
                if previous_rows is not None and rows > previous_rows:
                    ratio = rows / previous_rows if previous_rows else 0

                    return {
                        "bug_type": "Possible JOIN Fan-out",
                        "severity": "High" if ratio >= 2 else "Medium",
                        "description": (
                            f"Row count increased from {previous_rows} "
                            f"to {rows} after a JOIN "
                            f"(x{ratio:.2f}). Check whether the joined "
                            "table contains multiple matching rows per key."
                        ),
                    }

                previous_rows = rows

        return None

