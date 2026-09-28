import unittest
import os
from reports.package_generator import ResearchPackageGenerator

class TestHistoryAndPackage(unittest.TestCase):
    def setUp(self):
        self.generator = ResearchPackageGenerator()

    def test_generate_package(self):
        data = {
            "domain": "Education",
            "question": "Dropout prediction",
            "report_markdown": "# Test Report\nContent",
            "papers": [],
            "gaps": [],
            "scores": {"priority_score": 85.0},
            "experiment": {},
            "verifications": []
        }
        zip_path = self.generator.generate_package("TEST_PKG_001", data)
        self.assertTrue(os.path.exists(zip_path))

if __name__ == '__main__':
    unittest.main()
