
import importlib
import pkgutil

from Engine.detectors.base_detector import BaseBugDetector
import Engine.detectors as detectors


class EchoEngineRunner:
    """Loads detectors and runs them against parsed SQL steps."""

    def __init__(self, db_connection):
        self.db = db_connection

    def load_all_detectors(self):
        detector_plugins = []

        for _, module_name, _ in pkgutil.iter_modules(detectors.__path__):
            module = importlib.import_module(
                f"Engine.detectors.{module_name}"
            )

            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                if (
                    isinstance(attr, type)
                    and issubclass(attr, BaseBugDetector)
                    and attr is not BaseBugDetector
                ):
                    detector_plugins.append(attr())

        return detector_plugins

    def analyze_query(self, query: str, parsed_steps: list) -> list:
        detected_bugs = []

        for detector in self.load_all_detectors():
            report = detector.detect(parsed_steps, self.db)

            if report:
                detected_bugs.append(report)

        return detected_bugs
