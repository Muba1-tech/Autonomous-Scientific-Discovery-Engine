import os
import json
import zipfile
import io
import base64
import markdown
from xhtml2pdf import pisa
from typing import Dict, Any, Optional
from config import Config

def generate_pdf_from_markdown(report_md: str) -> bytes:
    safe_md = report_md.encode('ascii', 'ignore').decode('ascii')
    html_content = markdown.markdown(safe_md, extensions=['tables', 'fenced_code'])
    styled_html = f"""
    <html>
        <head>
            <style>
                @page {{ size: letter portrait; margin: 2cm; }}
                body {{ font-family: Helvetica, Arial, sans-serif; font-size: 11pt; line-height: 1.6; color: #1e293b; }}
                h1 {{ color: #0f172a; border-bottom: 2px solid #0284c7; padding-bottom: 6px; font-size: 18pt; }}
                h2 {{ color: #0369a1; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; font-size: 13pt; margin-top: 16px; }}
                h3 {{ color: #0f172a; font-size: 11pt; }}
                table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
                td, th {{ border: 1px solid #cbd5e1; padding: 6px 8px; font-size: 9pt; text-align: left; }}
                th {{ background-color: #f1f5f9; color: #0f172a; font-weight: bold; }}
                blockquote {{ border-left: 3px solid #0284c7; padding-left: 10px; color: #475569; margin: 10px 0; font-style: italic; }}
            </style>
        </head>
        <body>{html_content}</body>
    </html>
    """
    pdf_buffer = io.BytesIO()
    pisa.CreatePDF(styled_html, dest=pdf_buffer)
    return pdf_buffer.getvalue()

class ResearchPackageGenerator:
    """
    End-to-End Complete Research Package Generator for PROJECT AION.
    Compiles reports, metadata, data artifacts, code snippets, citations, and graphs 
    into a structured directory and downloadable ZIP file.
    """
    def __init__(self):
        Config.ensure_directories()

    def generate_package(self, research_id: str, data_package: Dict[str, Any]) -> str:
        """
        Creates research_output/<research_id>/ directory structure and compiles ZIP package.
        Returns the absolute path to the generated ZIP archive.
        """
        base_dir = os.path.join(Config.OUTPUT_DIR, research_id)
        report_dir = os.path.join(base_dir, "report")
        data_dir = os.path.join(base_dir, "data")
        exp_dir = os.path.join(base_dir, "experiments")
        graph_dir = os.path.join(base_dir, "graphs")
        citation_dir = os.path.join(base_dir, "citations")
        code_dir = os.path.join(base_dir, "code")
        doc_dir = os.path.join(base_dir, "documentation")

        for d in [report_dir, data_dir, exp_dir, graph_dir, citation_dir, code_dir, doc_dir]:
            os.makedirs(d, exist_ok=True)

        # 1. Report Generation (Markdown + PDF)
        report_md = data_package.get("report_markdown", "# Autonomous Research Report\nNo content provided.")
        md_path = os.path.join(report_dir, "research_report.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(report_md)

        pdf_path = os.path.join(report_dir, "research_report.pdf")
        try:
            pdf_bytes = generate_pdf_from_markdown(report_md)
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
        except Exception as e:
            print(f"[PackageGenerator] PDF creation fallback: {e}")

        # 2. Metadata & Documentation JSON
        metadata = {
            "research_id": research_id,
            "domain_goal": data_package.get("domain", "Omni-Domain"),
            "research_goal": data_package.get("question", "General Discovery"),
            "scores": data_package.get("scores", {}),
            "generated_at": data_package.get("timestamp", ""),
            "aion_version": "AION X Sovereign Autonomous Engine"
        }
        with open(os.path.join(doc_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        explainability = data_package.get("explainability", {})
        with open(os.path.join(doc_dir, "explainability_rationale.json"), "w", encoding="utf-8") as f:
            json.dump(explainability, f, indent=2)

        gaps = data_package.get("gaps", [])
        with open(os.path.join(doc_dir, "research_gaps.json"), "w", encoding="utf-8") as f:
            json.dump(gaps, f, indent=2)

        # 3. Data & Citations (Literature + Synthetic Dataset)
        papers = data_package.get("papers", [])
        with open(os.path.join(data_dir, "literature_papers.json"), "w", encoding="utf-8") as f:
            json.dump(papers, f, indent=2)

        verifications = data_package.get("verifications", [])
        with open(os.path.join(citation_dir, "citation_verifications.json"), "w", encoding="utf-8") as f:
            json.dump(verifications, f, indent=2)

        # Write Synthetic Dataset CSV if available
        exp_data = data_package.get("experiment", {})
        csv_content = exp_data.get("csv_data") or data_package.get("dataset_csv", "")
        if csv_content:
            with open(os.path.join(data_dir, "synthetic_dataset.csv"), "w", encoding="utf-8") as f:
                f.write(csv_content)

        # 4. Code & Experiments
        with open(os.path.join(exp_dir, "experiment_results.json"), "w", encoding="utf-8") as f:
            json.dump(exp_data, f, indent=2)

        sim_code = exp_data.get("python_code") or data_package.get("simulation_code", "# Autonomous Python Simulation\nprint('Simulation Execution Complete')")
        with open(os.path.join(code_dir, "experiment_model.py"), "w", encoding="utf-8") as f:
            f.write(sim_code)

        # 5. Graphs & Visualizations
        kg_html = data_package.get("kg_html", "")
        if kg_html:
            with open(os.path.join(graph_dir, "knowledge_graph.html"), "w", encoding="utf-8") as f:
                f.write(kg_html)

        plots_b64 = exp_data.get("plots_base64", [])
        if plots_b64 and len(plots_b64) > 0:
            try:
                img_data = base64.b64decode(plots_b64[0])
                with open(os.path.join(graph_dir, "simulation_distribution.png"), "wb") as f:
                    f.write(img_data)
            except Exception as e:
                print(f"[PackageGenerator] Plot write error: {e}")

        # 6. Build ZIP Package
        zip_filename = f"{research_id}_Complete_Package.zip"
        zip_path = os.path.join(Config.OUTPUT_DIR, zip_filename)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, Config.OUTPUT_DIR)
                    zipf.write(full_path, rel_path)

        print(f"[ResearchPackageGenerator] [OK] Successfully generated complete research package ZIP: {zip_path}")
        return zip_path
