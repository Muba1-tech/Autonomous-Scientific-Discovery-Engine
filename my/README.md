# 🌌 Autonomous Self-Evolving Multi-Agent for Omni-Domain Discovery with Neuro-Symbolic Reasoning and Causal Intelligence

[![Data Sovereignty](https://img.shields.io/badge/Data%20Sovereignty-100%25%20Air--Gapped-brightgreen)](#)
[![Execution](https://img.shields.io/badge/Execution-Local%20Edge%20Compute-blue)](#)
[![Zero Hallucination](https://img.shields.io/badge/Validation-Neuro--Symbolic-purple)](#)

An advanced, high-security autonomous scientific discovery engine. This project moves beyond standard LLM wrappers by utilizing a **Decentralized Multi-Agent System** bounded by **Deterministic Neuro-Symbolic Logic** to autonomously research, debate, and mathematically prove novel scientific hypotheses.

Designed for national labs and high-security enterprise environments, the system runs 100% locally via open-source LLMs (e.g., LLaMA 3, DeepSeek), ensuring zero API costs and zero intellectual property leakage.

## 🎯 Motivation
The motivation behind this project is to solve two massive problems in AI-driven scientific research: **Hallucinations** and **Data Sovereignty**. Standard cloud-based LLMs often hallucinate facts and cannot be trusted with highly classified or proprietary enterprise IP due to data leakage risks. By forcing the AI to derive answers from foundational axioms, validating logic through deterministic neuro-symbolic engines, and running the entire pipeline completely offline (air-gapped), researchers can innovate securely and trust the output.

## 🏁 Objectives
* To create a system that doesn't just "answer questions," but actively forges ideas through rigorous, simulated peer review.
* To translate theoretical scientific concepts into executable, real-world tech stacks (code, circuits, robotics).
* To provide an interactive, highly visual "Command Center" dashboard that allows human scientists to observe, steer, and collaborate with the AI swarm in real-time.

## 💻 Tech Stack
* **Programming Language:** Python
* **Frontend / UI:** Streamlit (with highly customized CSS/HTML/JS for a sci-fi "High-Tech Biolab" theme).
* **Local LLM Infrastructure:** Ollama.
* **Models:** `llama3` (for creative writing and hypothesis generation), `deepseek-coder:6.7b` (optimized for logic, math, and coding tasks), `llava` (Visual Language Model for processing images).
* **Retrieval-Augmented Generation (RAG):** FAISS for vector embeddings and document retrieval.
* **Data Processing & Extraction:** PyPDF2 (PDFs), pytesseract / Tesseract OCR (images), speech_recognition (voice input).
* **Database / Evolutionary Memory:** SQLite and FAISS (for semantic search of past discoveries).
* **Visualizations:** Plotly (Explainable AI Radar), PyVis / NetworkX (interactive Causal Knowledge Graphs).
* **Document Generation:** markdown, xhtml2pdf (PDFs), python-pptx (Presentations), custom LaTeX strings.

## 📥 Inputs & 📤 Outputs
**Multimodal Data Ingestion (Inputs):**
*   **Text Parameters:** Target Domain (e.g., Quantum Computing) and specific Research Goal.
*   **File Uploads:** Context documents via `.pdf`, `.txt`, `.csv`, and images (`.png`, `.jpg`).
*   **Voice Input:** Dictate research instructions via audio input.
*   **Human-in-the-Loop (HITL):** Real-time text feedback injected during the debate to dynamically pivot AI research.

**Complete IP Archive (Outputs):**
*   **Formal Scientific Discovery Report:** Comprehensive document containing gaps, hypotheses, and simulated peer review.
*   **Visualizations:** 3D Causal Knowledge Graphs and Explainable AI (XAI) Radar matrices.
*   **Academic & Business Assets:** Grant Proposal (PDF), Pitch Deck (PPTX), IEEE-formatted Research Paper (.tex), Provisional Patent Draft (.txt).
*   **Omni-Dimensional Deep-Tech Code:** Quantum Circuits (.qasm), Deep Learning Architectures (.py), Robotics Wet-Lab Scripts, Smart Contracts (.sol), Synthetic Digital Twin Data (.csv), Docker configurations.

## ✨ Key Novelties & Features

*   **🧠 Dynamic Polymath Swarm & First-Principles:** Autonomously spawns 3 specialized expert personas based on the input domain and derives solutions from fundamental mathematical/logical axioms to eliminate hallucination.
*   **🤺 Multi-Agent Adversarial Debate (Red-Teaming):** 
    Ideas are not simply generated; they are forged. An `[Innovator]` agent proposes hypotheses, a `[Critic]` stress-tests them for flaws, and a `[Validator]` agent checks the logical and causal soundness over multi-turn debates.
*   **💻 Executable AI Sandbox (Self-Healing Code):** 
    The AI writes its own Python simulation to test its hypothesis, executes it in a secure sandbox, and autonomously debugs its own tracebacks if it crashes.
*   **🌌 Omni-Dimensional Translation Matrix:** Translates theoretical ideas into executable deep-tech formats:
    *   **⚛️ Quantum:** Translates logic into OpenQASM quantum circuits for QPU hardware.
    *   **🧠 Neural Net:** Designs custom PyTorch deep learning architectures.
    *   **🤖 Robotics:** Writes Opentrons OT-2 liquid-handling scripts for wet-lab execution.
    *   **🏗️ Tech Stack:** Acts as a CTO to architect a real-world software/hardware implementation plan.
    *   **🌐 Web3 DeSci:** Writes Solidity smart contracts to tokenize the Intellectual Property.
    *   **🧬 DNA Storage:** Encodes IP into synthetic FASTA DNA sequences.
    *   **⚡ Neuromorphic:** Designs extreme edge-compute Spiking Neural Networks (SNNs) in snnTorch.
    *   **📐 Theorem Formulation:** Derives universal mathematical laws in LaTeX.
    *   **🎬 GenAI Media:** Synthesizes optimized prompts for Midjourney v6 and OpenAI Sora.
    *   **🌍 Game Theory:** Simulates global economic disruption and calculates Nash Equilibriums.
    *   **🥽 VR Metaverse:** Builds WebXR A-Frame interactive 3D environments.
    *   **🐳 Autonomous DevOps:** Containerizes the discovery into deployable Docker microservices.
*   **📝 Hostile Peer Review Simulator:** Autonomously generates brutal Reviewer #2 critiques and formal rebuttal letters.
*   **🛡️ Cryptographic Proof of Discovery (PoD):** Seals generated hypotheses with immutable SHA-256 hashing and UTC timestamps.
*   **📊 Synthetic Digital Twin Engine:** Generates a synthetic CSV dataset simulating expected physical results and plots them interactively via Plotly.
*   **🌱 Evolutionary Memory (Cross-Pollination):** 
    Utilizing a local FAISS vector database, the system remembers past hypotheses and failures. It autonomously mutates and evolves ideas across generations, applying discoveries from one domain (e.g., Quantum Physics) to another (e.g., Material Science).
*   **🔒 Frugal Innovation & Data Sovereignty:** 
    Runs entirely air-gapped on local edge compute. No sensitive data or classified discoveries are ever sent to cloud providers like OpenAI or Google.
*   **☁️ Cloud API Fallback (Optional):** Toggle to bypass local Ollama and use the Google Gemini API for all tasks, or enable "Turbo Mode" for instant mock execution.
*   **👁️ Visual Language Model (VLM) Lab Sight:** 
    Uses local LLaVA vision models to physically "look" at uploaded diagrams, handwritten formulas, or charts to extract scientific data for context.
*   **🔀 Smart LLM Routing:** Dynamically routes prompts to either LLaMA 3 or DeepSeek-Coder based on the calculated "cognitive entropy" (creative vs. logical tasks) of the prompt.
*   **⚛️ Interactive Holographic Cyber-Dashboard:** 
    Features a live hacker-style execution terminal, an Explainable AI (XAI) Radar Matrix, interactive physics-based Knowledge Graphs, 3D Latent Space navigation tracking the AI's thoughts, and live 3D Molecular structure rendering (`3Dmol.js`).
*   **📦 One-Click Complete IP Archive:** Zips all generated assets (PDF, PPTX, Python, LaTeX, Dockerfile, QASM, etc.) into a single deployable payload.

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/research-command-center.git
   cd research-command-center
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Local LLM Infrastructure (Ollama):**
   This project relies on local inference for data privacy.
   - Download and install Ollama.
   - Pull the required local models:
     ```bash
     ollama run llama3
     ollama run deepseek-coder:6.7b
     ollama run llava
     ```

4. **Optional: Install Tesseract for OCR:**
   If you plan to upload images (`.png`, `.jpg`) for the AI to read, install Tesseract OCR on your system and ensure it is added to your system's PATH.

## 💻 Usage

Ensure your local Ollama engine is running in the background, then launch the Streamlit Command Center:

```bash
streamlit run main.py -- --ui
```
*This will start a local server and open the dashboard in your default browser.*

### The Lab (Dashboard Configuration)
From within the Streamlit interface, you can quickly get started using the **Quick Load Demos** (e.g., Bioinformatics, Agentic Swarm, Neuromorphic ML, Superconductors). You can also toggle the following configurations:
*   **🚀 Turbo Mode:** Mocks LLM generation for instant execution and UI demonstrations (`TURBO_MODE=1`).
*   **☁️ Force Gemini API:** Bypasses local Ollama to use Google Gemini for all tasks (`FORCE_GEMINI=1`).

### Command Line Interface (CLI)
To run a headless discovery pipeline directly from your terminal:
```bash
python main.py --domain_goal "AgriTech" --research_goal "Drought-resistant organic farming"
```

---

## 📂 Project Structure

```text
CTSD/
│── core/               # Core pipeline logic integrating agents and engines
│── apis/               # External fetchers (ArXiv, PubMed, Semantic Scholar)
│── rag_engine/         # Vector embeddings and FAISS retrieval
│── cognitive_twin/     # Interactive Knowledge, Thought, and Causal Graphs
│── llm_engine/         # Subprocess wrappers for local Ollama models
│── neuro_symbolic/     # Dynamic rule engines and symbolic logic reasoners
│── causal_engine/      # Causal modeling and path inference validation
│── agents/             # The specialized AI personas
│── debate/             # Message passing and consensus resolution
│── simulation/         # Rule-based feasibility simulation
│── evaluation/         # Deep scoring metrics (Innovation, Feasibility, Risk)
│── outputs/            # PDF and PPTX report generation
│── ui/                 # Streamlit dashboard and PPTX templates
│── database/           # SQLite memory manager for evolutionary learning
│── main.py             # Application entry point
│── requirements.txt    # Project dependencies
```

---

## 🧑‍🔬 Human-in-the-Loop (HITL)
While Our Project operates autonomously, it features a crucial **Human-in-the-Loop** checkpoint in the UI. Users can review the AI's internal logic trace, edit the generated hypothesis, and manually approve or reject it. Approved hypotheses are committed to the system's Evolutionary Memory, guiding the AI's future discoveries.

---

## 🚀 Future Enhancements
* **Direct Hardware Integration:** Moving beyond generating scripts to directly connecting network APIs of laboratory equipment to physically execute wet-lab experiments.
* **Swarm Scaling:** Scaling the multi-agent system from 3 personas to massive swarms of hundreds of micro-specialized agents.
* **Advanced Physics Engines:** Enhancing the internal Python sandbox to utilize robust simulation libraries (like MuJoCo or GROMACS) to run highly complex, physics-accurate validations.
* **Decentralized Federated Memory:** Allowing disparate air-gapped instances to securely sync "Evolutionary Memory" databases via cryptographic protocols (like Web3 DeSci).

---

## 📜 License
This project is licensed under the MIT License. See the LICENSE file for details.
