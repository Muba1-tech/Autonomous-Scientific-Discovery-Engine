"""
AION X 2.0 — Cinematic 16-Agent Neural Swarm HUD & Dynamic Neon Glowing Avatars
Features:
- Ultra-sleek cinematic glowing animations when an agent is active
- Glassmorphic dark cyberpunk card styling with backdrop blur
- Individual active agent highlighting across all 16 simple English agents
"""

import base64
import streamlit as st


def get_agent_svg(agent_id: str, is_active: bool = False, size: int = 70) -> str:
    """Helper alias returning base64 avatar URL for backwards compatibility."""
    return get_agent_avatar_url(agent_id)


def _make_svg_b64(svg_inner: str, size: int = 100) -> str:
    """Encodes an SVG string into a clean base64 data URI."""
    full_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{size}" height="{size}">
    <defs>
        <linearGradient id="cyanG" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#38bdf8" />
            <stop offset="100%" stop-color="#0284c7" />
        </linearGradient>
        <linearGradient id="purpleG" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#c084fc" />
            <stop offset="100%" stop-color="#7c3aed" />
        </linearGradient>
        <linearGradient id="amberG" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#fbbf24" />
            <stop offset="100%" stop-color="#d97706" />
        </linearGradient>
        <linearGradient id="redG" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#f87171" />
            <stop offset="100%" stop-color="#dc2626" />
        </linearGradient>
        <linearGradient id="greenG" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#34d399" />
            <stop offset="100%" stop-color="#059669" />
        </linearGradient>
        <linearGradient id="pinkG" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#f472b6" />
            <stop offset="100%" stop-color="#db2777" />
        </linearGradient>
        <linearGradient id="goldG" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#fde047" />
            <stop offset="100%" stop-color="#ca8a04" />
        </linearGradient>
    </defs>
    {svg_inner}
    </svg>"""
    b64 = base64.b64encode(full_svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"


def get_agent_avatar_url(agent_id: str) -> str:
    """Generates distinct, high-detail AI cartoon character SVG avatars for all 16 agents."""
    
    # 1. Researcher Agent (Literature Mining)
    if agent_id in ["researcher", "elena"]:
        inner = """
        <circle cx="50" cy="50" r="46" fill="#0b1329" stroke="#38bdf8" stroke-width="3"/>
        <path d="M22 46 C22 18, 78 18, 78 46 C78 28, 68 20, 50 20 C32 20, 22 28, 22 46 Z" fill="#38bdf8"/>
        <circle cx="50" cy="52" r="24" fill="#fde68a"/>
        <rect x="30" y="44" width="40" height="13" rx="5" fill="url(#cyanG)"/>
        <line x1="34" y1="50" x2="66" y2="50" stroke="#ffffff" stroke-width="2" stroke-dasharray="3,2"/>
        <circle cx="50" cy="50" r="2.5" fill="#ffffff"/>
        <path d="M44 65 Q50 69 56 65" stroke="#b45309" stroke-width="2" fill="none"/>
        <polygon points="32,74 50,86 68,74 50,96" fill="#ffffff"/>
        <polygon points="40,74 50,90 60,74" fill="url(#cyanG)"/>
        """
        return _make_svg_b64(inner)

    # 2. Analyst Agent (Evidence Analysis)
    elif agent_id in ["analyst", "quantis"]:
        inner = """
        <circle cx="50" cy="50" r="46" fill="#0b1329" stroke="#a855f7" stroke-width="3"/>
        <polygon points="30,22 40,38 26,40" fill="url(#purpleG)"/>
        <polygon points="70,22 60,38 74,40" fill="url(#purpleG)"/>
        <circle cx="50" cy="52" r="25" fill="#1e1b4b"/>
        <circle cx="39" cy="48" r="11" fill="#030712" stroke="#c084fc" stroke-width="2.5"/>
        <circle cx="61" cy="48" r="11" fill="#030712" stroke="#c084fc" stroke-width="2.5"/>
        <circle cx="39" cy="48" r="5.5" fill="#38bdf8"/>
        <circle cx="61" cy="48" r="5.5" fill="#38bdf8"/>
        <circle cx="41" cy="46" r="2" fill="#ffffff"/>
        <circle cx="63" cy="46" r="2" fill="#ffffff"/>
        <polygon points="50,56 45,63 55,63" fill="#fbbf24"/>
        """
        return _make_svg_b64(inner)

    # 3. Citation Agent (Citation Verifier & Firewall)
    elif agent_id in ["citation", "aegis"]:
        inner = """
        <circle cx="50" cy="50" r="46" fill="#0b1329" stroke="#0ea5e9" stroke-width="3"/>
        <path d="M50 18 L78 30 L74 70 L50 88 L26 70 L22 30 Z" fill="url(#cyanG)"/>
        <path d="M50 25 L71 35 L67 65 L50 79 L33 65 L29 35 Z" fill="#0f172a"/>
        <line x1="50" y1="34" x2="50" y2="62" stroke="#38bdf8" stroke-width="4"/>
        <line x1="36" y1="46" x2="64" y2="46" stroke="#38bdf8" stroke-width="4"/>
        <circle cx="50" cy="46" r="5" fill="#ffffff"/>
        """
        return _make_svg_b64(inner)

    # 4. Innovator Agent (Lead Hypothesis Generator)
    elif agent_id in ["innovator", "prometheus"]:
        inner = """
        <circle cx="50" cy="50" r="46" fill="#0b1329" stroke="#f59e0b" stroke-width="3"/>
        <path d="M18 48 Q12 20 35 18 Q50 8 65 18 Q88 20 82 48 Z" fill="#f1f5f9"/>
        <circle cx="50" cy="54" r="23" fill="#fde047"/>
        <circle cx="39" cy="48" r="10" fill="#0f172a" stroke="url(#amberG)" stroke-width="3"/>
        <circle cx="61" cy="48" r="10" fill="#0f172a" stroke="url(#amberG)" stroke-width="3"/>
        <line x1="49" y1="48" x2="51" y2="48" stroke="#f59e0b" stroke-width="3"/>
        <circle cx="39" cy="48" r="5" fill="#38bdf8"/>
        <circle cx="61" cy="48" r="5" fill="#38bdf8"/>
        <circle cx="41" cy="46" r="2" fill="#ffffff"/>
        <circle cx="63" cy="46" r="2" fill="#ffffff"/>
        <path d="M36 65 Q50 70 64 65" stroke="#ffffff" stroke-width="3.5" fill="none"/>
        <polygon points="45,76 55,76 53,95 47,95" fill="url(#redG)"/>
        """
        return _make_svg_b64(inner)

    # 5. Gap Agent (Research Gap Detector)
    elif agent_id in ["gap", "atlas"]:
        inner = """
        <circle cx="50" cy="50" r="46" fill="#0b1329" stroke="#818cf8" stroke-width="3"/>
        <line x1="50" y1="14" x2="50" y2="28" stroke="#818cf8" stroke-width="4"/>
        <circle cx="50" cy="14" r="6" fill="#fbbf24"/>
        <rect x="24" y="28" width="52" height="42" rx="12" fill="url(#purpleG)"/>
        <rect x="30" y="34" width="40" height="30" rx="8" fill="#030712"/>
        <circle cx="42" cy="49" r="7" fill="#38bdf8"/>
        <circle cx="58" cy="49" r="7" fill="#38bdf8"/>
        <circle cx="44" cy="47" r="2.5" fill="#ffffff"/>
        <circle cx="60" cy="47" r="2.5" fill="#ffffff"/>
        <rect x="34" y="72" width="32" height="18" rx="5" fill="#475569"/>
        <circle cx="50" cy="80" r="3.5" fill="#34d399"/>
        """
        return _make_svg_b64(inner)

    # 6. Cross-Domain Agent (Knowledge Bridge)
    elif agent_id in ["cross_domain", "nexus"]:
        inner = """
        <circle cx="50" cy="50" r="46" fill="#0b1329" stroke="#06b6d4" stroke-width="3"/>
        <polygon points="50,18 78,34 78,66 50,82 22,66 22,34" fill="none" stroke="url(#cyanG)" stroke-width="3"/>
        <circle cx="50" cy="50" r="16" fill="url(#purpleG)"/>
        <circle cx="50" cy="50" r="6" fill="#ffffff"/>
        <circle cx="50" cy="18" r="4" fill="#38bdf8"/>
        <circle cx="78" cy="34" r="4" fill="#a855f7"/>
        <circle cx="78" cy="66" r="4" fill="#ec4899"/>
        <circle cx="50" cy="82" r="4" fill="#34d399"/>
        <circle cx="22" cy="66" r="4" fill="#fbbf24"/>
        <circle cx="22" cy="34" r="4" fill="#f87171"/>
        """
        return _make_svg_b64(inner)

    # 7. Critic Agent (Adversarial Skeptic)
    elif agent_id in ["critic", "skeptic"]:
        inner = """
        <circle cx="50" cy="50" r="46" fill="#0b1329" stroke="#ef4444" stroke-width="3"/>
        <polygon points="50,16 80,34 74,76 50,88 26,76 20,34" fill="url(#redG)"/>
        <polygon points="50,28 70,40 66,70 50,80 34,70 30,40" fill="#0f172a"/>
        <polygon points="36,49 50,43 64,49 50,55" fill="#f43f5e"/>
        <circle cx="50" cy="49" r="4" fill="#ffffff"/>
        <line x1="36" y1="62" x2="64" y2="62" stroke="#fca5a5" stroke-width="2"/>
        """
        return _make_svg_b64(inner)

    # 8. Validator Agent (Debate Referee & Judge)
    elif agent_id in ["validator"]:
        inner = """
        <circle cx="50" cy="50" r="46" fill="#0b1329" stroke="#fbbf24" stroke-width="3"/>
        <ellipse cx="50" cy="20" rx="22" ry="7" fill="none" stroke="url(#amberG)" stroke-width="3"/>
        <path d="M24 48 C24 22, 76 22, 76 48 L72 84 L28 84 Z" fill="#1e293b"/>
        <ellipse cx="50" cy="52" rx="19" ry="16" fill="url(#cyanG)"/>
        <line x1="41" y1="48" x2="59" y2="48" stroke="#ffffff" stroke-width="2.5"/>
        <line x1="50" y1="43" x2="50" y2="57" stroke="#ffffff" stroke-width="2.5"/>
        <circle cx="41" cy="55" r="3.5" fill="#fbbf24"/>
        <circle cx="59" cy="55" r="3.5" fill="#fbbf24"/>
        """
        return _make_svg_b64(inner)

    # 9. Ethicist Agent (Safety & Research Red Team)
    elif agent_id in ["ethicist", "vigil"]:
        inner = """
        <circle cx="50" cy="50" r="46" fill="#0b1329" stroke="#b91c1c" stroke-width="3"/>
        <path d="M50 16 L82 32 L78 72 L50 88 L22 72 L18 32 Z" fill="#450a0a"/>
        <circle cx="50" cy="50" r="18" fill="#7f1d1d" stroke="#f87171" stroke-width="2"/>
        <circle cx="50" cy="50" r="8" fill="#ef4444"/>
        <circle cx="50" cy="50" r="3" fill="#ffffff"/>
        <line x1="28" y1="50" x2="42" y2="50" stroke="#fca5a5" stroke-width="2"/>
        <line x1="58" y1="50" x2="72" y2="50" stroke="#fca5a5" stroke-width="2"/>
        """
        return _make_svg_b64(inner)

    # 10. Self-Correction Agent (Iterative Refiner)
    elif agent_id in ["self_correction", "synapse"]:
        inner = """
        <circle cx="50" cy="50" r="46" fill="#0b1329" stroke="#14b8a6" stroke-width="3"/>
        <circle cx="50" cy="50" r="22" fill="#042f2e" stroke="#2dd4bf" stroke-width="2"/>
        <circle cx="50" cy="35" r="5" fill="#2dd4bf"/>
        <circle cx="36" cy="58" r="5" fill="#2dd4bf"/>
        <circle cx="64" cy="58" r="5" fill="#2dd4bf"/>
        <line x1="50" y1="35" x2="36" y2="58" stroke="#5eead4" stroke-width="2.5"/>
        <line x1="50" y1="35" x2="64" y2="58" stroke="#5eead4" stroke-width="2.5"/>
        <line x1="36" y1="58" x2="64" y2="58" stroke="#5eead4" stroke-width="2.5"/>
        <circle cx="50" cy="48" r="4" fill="#fbbf24"/>
        """
        return _make_svg_b64(inner)

    # 11. Experiment Agent (AST Sandbox Simulator)
    elif agent_id in ["experiment", "labcore"]:
        inner = """
        <circle cx="50" cy="50" r="46" fill="#0b1329" stroke="#10b981" stroke-width="3"/>
        <rect x="43" y="14" width="14" height="12" rx="2" fill="#34d399"/>
        <circle cx="50" cy="12" r="4" fill="#a7f3d0"/>
        <circle cx="50" cy="46" r="23" fill="url(#greenG)"/>
        <rect x="33" y="40" width="34" height="13" rx="4" fill="#022c22"/>
        <circle cx="41" cy="46" r="3.5" fill="#6ee7b7"/>
        <circle cx="59" cy="46" r="3.5" fill="#6ee7b7"/>
        <path d="M45 64 L34 85 Q50 90 66 85 L55 64 Z" fill="#047857"/>
        <circle cx="45" cy="77" r="2.5" fill="#ffffff" opacity="0.9"/>
        <circle cx="55" cy="79" r="3.5" fill="#ffffff" opacity="0.9"/>
        """
        return _make_svg_b64(inner)

    # 12. Novelty Agent (Evolutionary Genome Engine)
    elif agent_id in ["novelty", "helix"]:
        inner = """
        <circle cx="50" cy="50" r="46" fill="#0b1329" stroke="#ec4899" stroke-width="3"/>
        <path d="M26 30 Q50 50 74 30 Q50 50 26 70 Q50 50 74 70" fill="none" stroke="url(#pinkG)" stroke-width="4"/>
        <circle cx="26" cy="30" r="5" fill="#38bdf8"/>
        <circle cx="74" cy="30" r="5" fill="#c084fc"/>
        <circle cx="26" cy="70" r="5" fill="#c084fc"/>
        <circle cx="74" cy="70" r="5" fill="#38bdf8"/>
        <circle cx="50" cy="50" r="17" fill="#1e1b4b" stroke="#ec4899" stroke-width="2.5"/>
        <circle cx="44" cy="48" r="3.5" fill="#ec4899"/>
        <circle cx="56" cy="48" r="3.5" fill="#ec4899"/>
        <line x1="44" y1="56" x2="56" y2="56" stroke="#38bdf8" stroke-width="2"/>
        """
        return _make_svg_b64(inner)

    # 13. Explainability Agent (Counterfactual Lab)
    elif agent_id in ["explainability", "chronos"]:
        inner = """
        <circle cx="50" cy="50" r="46" fill="#0b1329" stroke="#d97706" stroke-width="3"/>
        <circle cx="50" cy="50" r="30" fill="none" stroke="url(#amberG)" stroke-width="3.5" stroke-dasharray="5,4"/>
        <circle cx="50" cy="50" r="21" fill="#1c1917"/>
        <circle cx="43" cy="46" r="3.5" fill="#f59e0b"/>
        <circle cx="57" cy="46" r="3.5" fill="#f59e0b"/>
        <line x1="50" y1="50" x2="50" y2="33" stroke="#38bdf8" stroke-width="2.5"/>
        <line x1="50" y1="50" x2="63" y2="50" stroke="#fbbf24" stroke-width="2.5"/>
        """
        return _make_svg_b64(inner)

    # 14. Writer Agent (Academic Publisher)
    elif agent_id in ["writer", "scribe"]:
        inner = """
        <circle cx="50" cy="50" r="46" fill="#0b1329" stroke="#ec4899" stroke-width="3"/>
        <polygon points="50,16 84,27 50,38 16,27" fill="#831843"/>
        <polygon points="46,34 54,34 52,43 48,43" fill="#fbbf24"/>
        <circle cx="50" cy="55" r="21" fill="url(#pinkG)"/>
        <rect x="33" y="49" width="13" height="9" rx="2" fill="#0f172a" stroke="#ffffff" stroke-width="1.8"/>
        <rect x="54" y="49" width="13" height="9" rx="2" fill="#0f172a" stroke="#ffffff" stroke-width="1.8"/>
        <line x1="46" y1="53" x2="54" y2="53" stroke="#ffffff" stroke-width="1.8"/>
        <path d="M45 67 Q50 72 55 67" stroke="#ffffff" stroke-width="2" fill="none"/>
        """
        return _make_svg_b64(inner)

    # 15. Memory Agent (Failure Vault & Database)
    elif agent_id in ["memory", "thanatos"]:
        inner = """
        <circle cx="50" cy="50" r="46" fill="#0b1329" stroke="#7c3aed" stroke-width="3"/>
        <path d="M24 50 C24 18, 76 18, 76 50 L72 84 L28 84 Z" fill="#2e1065"/>
        <circle cx="50" cy="53" r="17" fill="#030712"/>
        <circle cx="43" cy="48" r="4.5" fill="#c084fc"/>
        <circle cx="57" cy="48" r="4.5" fill="#c084fc"/>
        <line x1="43" y1="61" x2="57" y2="61" stroke="#e9d5ff" stroke-width="2.5"/>
        <line x1="47" y1="59" x2="47" y2="63" stroke="#e9d5ff" stroke-width="2"/>
        <line x1="53" y1="59" x2="53" y2="63" stroke="#e9d5ff" stroke-width="2"/>
        """
        return _make_svg_b64(inner)

    # 16. Report Agent (Reproducibility Capsule & Package)
    elif agent_id in ["report", "archon"]:
        inner = """
        <circle cx="50" cy="50" r="46" fill="#0b1329" stroke="#eab308" stroke-width="3"/>
        <polygon points="50,14 62,32 82,32 66,46 72,66 50,54 28,66 34,46 18,32 38,32" fill="url(#goldG)"/>
        <circle cx="50" cy="54" r="18" fill="#1e1b4b" stroke="#fde047" stroke-width="2"/>
        <circle cx="44" cy="52" r="4" fill="#38bdf8"/>
        <circle cx="56" cy="52" r="4" fill="#38bdf8"/>
        <circle cx="45" cy="50" r="1.5" fill="#ffffff"/>
        <circle cx="57" cy="50" r="1.5" fill="#ffffff"/>
        <line x1="43" y1="62" x2="57" y2="62" stroke="#fde047" stroke-width="2"/>
        """
        return _make_svg_b64(inner)

    # Default fallback
    return _make_svg_b64('<circle cx="50" cy="50" r="46" fill="#0b1329" stroke="#38bdf8" stroke-width="3"/><circle cx="50" cy="50" r="20" fill="#38bdf8"/>')


def render_cinematic_swarm_bar(active_agent_id: str = "all"):
    """
    Renders the 16-agent swarm HUD organized into 6 clear functional categories,
    with dynamic glowing neon animations for whichever agent is currently active.
    """
    st.markdown("""
        <style>
        @keyframes active-neon-pulse {
            0% {
                transform: translateY(-2px) scale(1.04);
                box-shadow: 0 0 20px #00f5ff, 0 0 40px rgba(56, 189, 248, 0.9), inset 0 0 15px rgba(0, 245, 255, 0.6);
                border-color: #00f5ff;
            }
            50% {
                transform: translateY(-5px) scale(1.08);
                box-shadow: 0 0 35px #38bdf8, 0 0 70px rgba(129, 140, 248, 0.95), inset 0 0 22px rgba(56, 189, 248, 0.8);
                border-color: #38bdf8;
            }
            100% {
                transform: translateY(-2px) scale(1.04);
                box-shadow: 0 0 20px #00f5ff, 0 0 40px rgba(56, 189, 248, 0.9), inset 0 0 15px rgba(0, 245, 255, 0.6);
                border-color: #00f5ff;
            }
        }
        @keyframes avatar-bob {
            0% { transform: translateY(0px) scale(1.0); filter: drop-shadow(0 0 8px #00f5ff); }
            50% { transform: translateY(-5px) scale(1.10); filter: drop-shadow(0 0 22px #38bdf8) drop-shadow(0 0 14px #818cf8); }
            100% { transform: translateY(0px) scale(1.0); filter: drop-shadow(0 0 8px #00f5ff); }
        }
        .card-active-glow {
            background: linear-gradient(135deg, rgba(14, 165, 233, 0.5) 0%, rgba(99, 102, 241, 0.45) 100%) !important;
            border: 2.5px solid #00f5ff !important;
            border-radius: 14px !important;
            padding: 7px 3px !important;
            text-align: center !important;
            animation: active-neon-pulse 1.6s infinite ease-in-out !important;
            position: relative !important;
            z-index: 10 !important;
        }
        .card-active-glow img {
            animation: avatar-bob 1.5s infinite ease-in-out !important;
        }
        .card-idle-sleek {
            background: rgba(15, 23, 42, 0.7) !important;
            border: 1px solid rgba(99, 102, 241, 0.22) !important;
            border-radius: 14px !important;
            padding: 7px 3px !important;
            text-align: center !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        .card-idle-sleek:hover {
            border-color: rgba(56, 189, 248, 0.6) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    all_16_agents = [
        # 1. RESEARCH & DATA
        {"id": "researcher", "name": "Researcher Agent", "category": "RESEARCH & DATA", "desc": "Literature Mining", "tag": "RETRIEVING"},
        {"id": "analyst", "name": "Analyst Agent", "category": "RESEARCH & DATA", "desc": "Evidence Analysis", "tag": "ANALYZING"},
        {"id": "citation", "name": "Citation Agent", "category": "RESEARCH & DATA", "desc": "Lineage & Firewall", "tag": "VERIFYING"},
        # 2. BRAINSTORMING
        {"id": "innovator", "name": "Innovator Agent", "category": "BRAINSTORMING", "desc": "First Principles", "tag": "SYNTHESIZING"},
        {"id": "gap", "name": "Gap Agent", "category": "BRAINSTORMING", "desc": "Frontiers Mapped", "tag": "MAPPING"},
        {"id": "cross_domain", "name": "Cross-Domain Agent", "category": "BRAINSTORMING", "desc": "Knowledge Bridge", "tag": "BRIDGING"},
        # 3. CRITIQUE & SAFETY
        {"id": "critic", "name": "Critic Agent", "category": "CRITIQUE & SAFETY", "desc": "Adversarial Skeptic", "tag": "ATTACKING"},
        {"id": "validator", "name": "Validator Agent", "category": "CRITIQUE & SAFETY", "desc": "Impartial Referee", "tag": "JUDGING"},
        # Row 2
        {"id": "ethicist", "name": "Ethicist Agent", "category": "CRITIQUE & SAFETY", "desc": "Red Team & Safety", "tag": "AUDITING"},
        {"id": "self_correction", "name": "Self-Correction", "category": "CRITIQUE & SAFETY", "desc": "Iterative Refiner", "tag": "REFINING"},
        # 4. LAB SIMULATION
        {"id": "experiment", "name": "Experiment Agent", "category": "LAB SIMULATION", "desc": "Sandbox Simulator", "tag": "SIMULATING"},
        # 5. EXPLANATION
        {"id": "novelty", "name": "Novelty Agent", "category": "EXPLANATION", "desc": "Evolution Genome", "tag": "EVOLVING"},
        {"id": "explainability", "name": "Explainability", "category": "EXPLANATION", "desc": "Counterfactual Lab", "tag": "STRESS-TEST"},
        # 6. REPORTING & MEMORY
        {"id": "writer", "name": "Writer Agent", "category": "REPORTING & MEMORY", "desc": "LaTeX & Report", "tag": "WRITING"},
        {"id": "memory", "name": "Memory Agent", "category": "REPORTING & MEMORY", "desc": "Failure Vault (DB)", "tag": "SAVING"},
        {"id": "report", "name": "Report Agent", "category": "REPORTING & MEMORY", "desc": "Capsule (PDF/ZIP)", "tag": "PACKAGING"}
    ]

    # Render in 2 rows of 8 cleanly
    row1 = all_16_agents[:8]
    row2 = all_16_agents[8:]

    for r_agents in [row1, row2]:
        cols = st.columns(8)
        for idx, ag in enumerate(r_agents):
            is_active = bool(active_agent_id and (active_agent_id == "all" or active_agent_id == ag["id"] or ag["id"] in str(active_agent_id).split(",")))
            card_class = "card-active-glow" if is_active else "card-idle-sleek"
            status_color = "#00f5ff" if is_active else "#94a3b8"
            status_text = f"⚡ {ag['tag']}" if is_active else ag["desc"]
            img_url = get_agent_avatar_url(ag["id"])

            with cols[idx]:
                st.markdown(f"""
                    <div class="{card_class}">
                        <div style='display:flex; justify-content:center; margin-bottom:3px;'>
                            <img src="{img_url}" width="54" height="54" style="border-radius:50%;" />
                        </div>
                        <div style='font-weight:800; font-size:0.75rem; color:#ffffff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{ag['name']}</div>
                        <div style='font-size:0.64rem; color:#38bdf8; font-weight:600; white-space:nowrap; overflow:hidden;'>{ag['category']}</div>
                        <div style='font-size:0.6rem; color:{status_color}; background:rgba(0,0,0,0.45); padding:2px 2px; border-radius:4px; margin-top:3px; font-weight:800; white-space:nowrap; overflow:hidden;'>
                            {status_text}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)
