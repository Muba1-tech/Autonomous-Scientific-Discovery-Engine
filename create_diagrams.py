"""
Ultra-aesthetic high-resolution architecture and workflow diagrams for AION X 2.0.
Background: #0A0E1A (Deep Midnight Space), crisp typography, clean badges, 300 DPI.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_system_design_diagram(output_path="system_architecture_diagram.png"):
    fig, ax = plt.subplots(figsize=(9, 6.2), dpi=300)
    fig.patch.set_facecolor('#0a0e1a')
    ax.set_facecolor('#0a0e1a')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Header
    ax.text(50, 96, "SYSTEM ARCHITECTURE (5-TIER MODULAR DESIGN)", fontsize=12, fontweight='bold', color='#38bdf8', ha='center')
    ax.text(50, 92, "High-Level Architecture of AION X 2.0 Discovery Engine", fontsize=8.5, color='#94a3b8', ha='center')

    # 5 Tiers
    layers = [
        ("LAYER 1: USER INTERFACE", "Streamlit Web Dashboard  •  File Uploads (PDF, DOCX, CSV)  •  Voice Query", 80, '#0284c7', 'UI'),
        ("LAYER 2: 16-AGENT SWARM", "Researcher, Gap Detector, Innovator, Critic, Ethicist & Sandbox Agents", 63, '#818cf8', 'AGENTS'),
        ("LAYER 3: KNOWLEDGE & RETRIEVAL", "Live ArXiv & PubMed Search APIs  •  FAISS Vector Index  •  Citation Firewall", 46, '#10b981', 'DATA'),
        ("LAYER 4: DEBATE & KILL CHAIN", "10-Stage Popperian Falsification Gauntlet  •  Scientific Failure Vault", 29, '#f43f5e', 'TEST'),
        ("LAYER 5: SANDBOX & EXPORT", "AST-Secured Process Sandbox  •  Multi-Format Capsule Generator (PPT, PDF, ZIP)", 12, '#f59e0b', 'CORE')
    ]

    for title, subtitle, y_pos, border_col, badge_text in layers:
        # Card background
        rect = patches.FancyBboxPatch((6, y_pos - 4.5), 88, 10.8,
                                     boxstyle="round,pad=0.8,rounding_size=2.0",
                                     linewidth=1.4, edgecolor=border_col, facecolor='#121829')
        ax.add_patch(rect)

        # Badge pill
        badge = patches.FancyBboxPatch((9, y_pos - 1.5), 14, 5.2,
                                      boxstyle="round,pad=0.4,rounding_size=1.2",
                                      linewidth=1, edgecolor=border_col, facecolor=border_col)
        ax.add_patch(badge)
        ax.text(16, y_pos + 1.1, badge_text, fontsize=8, fontweight='bold', color='#ffffff', ha='center', va='center')

        # Text labels
        ax.text(26, y_pos + 2.4, title, fontsize=9.8, fontweight='bold', color='#f8fafc', va='center')
        ax.text(26, y_pos - 1.4, subtitle, fontsize=7.8, color='#94a3b8', va='center')

        # Connecting downward arrow
        if y_pos > 15:
            ax.annotate('', xy=(50, y_pos - 4.8), xytext=(50, y_pos - 6.2),
                        arrowprops=dict(facecolor='#38bdf8', edgecolor='#38bdf8', width=1.8, headwidth=5, headlength=5))

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Generated {output_path}")

def generate_implementation_workflow(output_path="implementation_workflow_diagram.png"):
    fig, ax = plt.subplots(figsize=(9, 6.2), dpi=300)
    fig.patch.set_facecolor('#0a0e1a')
    ax.set_facecolor('#0a0e1a')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Header
    ax.text(50, 96, "DISCOVERY LIFECYCLE & EXECUTION WORKFLOW", fontsize=12, fontweight='bold', color='#38bdf8', ha='center')
    ax.text(50, 92, "Autonomous 6-Step Research Pipeline from Query to Verified Capsule", fontsize=8.5, color='#94a3b8', ha='center')

    # 6 Steps arranged in 2 rows of 3 columns
    steps = [
        ("Step 1: Input Ingestion", "User enters topic or paper.\nSystem defines research goal.", 18, 70, "#38bdf8", "01"),
        ("Step 2: Paper Mining", "Queries ArXiv & PubMed.\nCitation Firewall blocks fakes.", 50, 70, "#818cf8", "02"),
        ("Step 3: Gap Detection", "Isolates research limitations.\nInnovator writes causal ideas.", 82, 70, "#34d399", "03"),
        ("Step 4: Debate Arena", "Critic attacks hypotheses.\nWeak ideas sent to Failure Vault.", 82, 30, "#f43f5e", "04"),
        ("Step 5: Code Sandbox", "Experiment Agent writes code.\nAST Sandbox tests safely.", 50, 30, "#fbbf24", "05"),
        ("Step 6: Capsule Export", "Compiles verified discoveries.\nExports PPTX, DOCX, & PDF.", 18, 30, "#10b981", "06")
    ]

    for title, desc, cx, cy, col, num in steps:
        # Card
        rect = patches.FancyBboxPatch((cx - 13.5, cy - 14.5), 27, 24.5,
                                     boxstyle="round,pad=0.8,rounding_size=2.0",
                                     linewidth=1.4, edgecolor=col, facecolor='#121829')
        ax.add_patch(rect)

        # Number circle badge
        circle = patches.Circle((cx, cy + 5.5), 3.2, facecolor=col, edgecolor='white', linewidth=1)
        ax.add_patch(circle)
        ax.text(cx, cy + 5.5, num, fontsize=9.5, fontweight='bold', color='#0a0e1a', ha='center', va='center')

        # Title
        ax.text(cx, cy - 0.5, title, fontsize=9.2, fontweight='bold', color='#f8fafc', ha='center', va='center')

        # Description
        ax.text(cx, cy - 7.5, desc, fontsize=7.2, color='#94a3b8', ha='center', va='center', multialignment='center')

    # Connecting arrows
    ax.annotate('', xy=(36.5, 70), xytext=(31.5, 70),
                arrowprops=dict(facecolor='#38bdf8', edgecolor='#38bdf8', width=1.8, headwidth=5, headlength=5))
    ax.annotate('', xy=(68.5, 70), xytext=(63.5, 70),
                arrowprops=dict(facecolor='#38bdf8', edgecolor='#38bdf8', width=1.8, headwidth=5, headlength=5))
    ax.annotate('', xy=(82, 42.5), xytext=(82, 55.5),
                arrowprops=dict(facecolor='#f43f5e', edgecolor='#f43f5e', width=1.8, headwidth=5, headlength=5))
    ax.annotate('', xy=(63.5, 30), xytext=(68.5, 30),
                arrowprops=dict(facecolor='#fbbf24', edgecolor='#fbbf24', width=1.8, headwidth=5, headlength=5))
    ax.annotate('', xy=(31.5, 30), xytext=(36.5, 30),
                arrowprops=dict(facecolor='#10b981', edgecolor='#10b981', width=1.8, headwidth=5, headlength=5))

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_system_design_diagram()
    generate_implementation_workflow()
