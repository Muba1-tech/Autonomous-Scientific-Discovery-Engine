import os
import datetime

class ReportGenerator:
    def save_report(self, content, filename=None):
        filename = filename or f"formal_discovery_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        os.makedirs("output_files", exist_ok=True)
        path = os.path.join("output_files", filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path
