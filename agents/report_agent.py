from typing import Dict, Any
from reports.package_generator import ResearchPackageGenerator

class ReportAgent:
    """
    Agent responsible for compiling the final research report and packaging full ZIP artifacts.
    """
    def __init__(self):
        self.generator = ResearchPackageGenerator()

    def run(self, research_id: str, data_package: Dict[str, Any]) -> str:
        print(f"[ReportAgent] Compiling complete end-to-end research package for {research_id}...")
        return self.generator.generate_package(research_id, data_package)
