import os
import json
import re
from typing import TypedDict
import google.generativeai as genai
from google.generativeai import GenerativeModel, GenerationConfig
from langgraph.graph import StateGraph, END
from pypdf import PdfReader
from agents.repository_agent import RepositoryAgent

class AgentState(TypedDict):
    pdf_path: str
    repo_url: str
    github_api_key: str
    paper_text: str
    claims: dict
    methodology_matrix: dict
    datasets_detected: list
    repositories_detected: list
    repo_analysis: dict
    reproducibility_evidence_analysis: dict
    transparency_score: float
    methodology_score: float
    credibility_score: float
    research_strengths: dict
    architecture_details: dict
    claim_plausibility_analysis: list
    evidence_verification: list
    reviewer_consensus: dict
    trust_timeline: list
    reviewer_questions: list
    research_personality: str
    final_reviewer_perspective: str
    executive_summary: str
    research_domain: str
    paper_positioning: str
    limitation_keys: list
    logs: list


class VerifyAIMultiAgentSystem:
    def __init__(self, model_name="gemini-2.5-flash", api_key=None):
        if api_key:
            genai.configure(api_key=api_key)
        self.llm = GenerativeModel(model_name)

    def _generate(self, prompt: str) -> dict:
        config = GenerationConfig(temperature=0.2)
        response = self.llm.generate_content(prompt, generation_config=config)
        content = response.text.strip()
        if content.startswith("```json"): content = content[7:-3]
        elif content.startswith("```"): content = content[3:-3]
        try:
            return json.loads(content)
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return {}

    def paper_analysis_agent(self, state: AgentState) -> dict:
        state['logs'].append("📄 Paper Analysis Agent Activated")
        state['logs'].append("Ingesting PDF — extracting architecture names, benchmarks, datasets...")
        state['logs'].append("Scanning for repository references and parameter counts...")
        reader = PdfReader(state['pdf_path'])
        text = "".join(page.extract_text() + "\n" for page in reader.pages[:10])

        regex_repos = re.findall(r'https?://(?:www\.)?(?:github\.com|gitlab\.com)/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+', text)
        regex_repos = list(set(regex_repos))

        prompt = f"""You are the Paper Analysis Agent for VerifyAI — an AI Scientific Transparency & Credibility Auditor.

Extract deeply paper-grounded information. Be SPECIFIC. Extract EXACT names, numbers, and values from the text.
Do NOT produce generic placeholders. Every field must reference actual content from the paper.

Respond ONLY in JSON:
{{
    "research_domain": "Exact domain (e.g. Vision-Language Models, Protein Structure Prediction)",
    "paper_positioning": "Category (e.g. PEFT Fine-tuning, Zero-Shot Reasoning, Architecture Design)",
    "claims": {{
        "Exact benchmark name (e.g. MMLU, HumanEval, SWE-bench)": "exact claimed score/value",
        "Architecture claim": "exact claim from paper"
    }},
    "methodology_matrix": {{
        "Dataset Availability": "Present|Partially Specified|Not Specified",
        "Hyperparameters": "Present|Partially Specified|Not Specified",
        "Hardware Specs": "Present|Partially Specified|Not Specified",
        "Training Details": "Present|Partially Specified|Not Specified",
        "Evaluation Protocol": "Present|Partially Specified|Not Specified",
        "Statistical Significance": "Present|Partially Specified|Not Specified"
    }},
    "datasets_detected": ["Exact dataset names from paper e.g. ImageNet-1K, C4, The Pile"],
    "repositories_detected": ["github/gitlab URLs found"],
    "research_strengths": {{
        "strongest_innovation": "Specific novel contribution with exact architecture/method name",
        "strongest_transparency_signal": "Specific transparency indicator (e.g. 'releases model weights at HF hub')",
        "strongest_engineering_signal": "Specific engineering detail (e.g. 'trained on 512 A100s for 3 weeks')",
        "strongest_scientific_contribution": "Specific contribution with exact metric improvement"
    }},
    "architecture_details": {{
        "model_name": "Exact model name if mentioned",
        "parameter_count": "Exact parameter count e.g. 7B, 70B, 175B",
        "base_model": "Base model if fine-tuned e.g. LLaMA-3, GPT-4",
        "training_compute": "Training compute if mentioned",
        "key_technique": "Key algorithmic technique e.g. LoRA, Flash Attention, RLHF"
    }}
}}
Paper text:
{text[:32000]}"""
        data = self._generate(prompt)

        repositories_detected = data.get("repositories_detected", [])
        if isinstance(repositories_detected, list):
            for r in regex_repos:
                if r not in repositories_detected:
                    repositories_detected.append(r)
        else:
            repositories_detected = regex_repos

        state['logs'].append(f"Paper grounding complete — domain: {data.get('research_domain','?')}, {len(data.get('claims',{}))} claims extracted.")
        return {
            "paper_text": text,
            "research_domain": data.get("research_domain", "Unknown Domain"),
            "paper_positioning": data.get("paper_positioning", "Unknown Category"),
            "claims": data.get("claims", {}),
            "methodology_matrix": data.get("methodology_matrix", {}),
            "datasets_detected": data.get("datasets_detected", []),
            "repositories_detected": repositories_detected,
            "research_strengths": data.get("research_strengths", {}),
            "architecture_details": data.get("architecture_details", {}),
        }


    def repository_intelligence_agent(self, state: AgentState) -> dict:
        agent = RepositoryAgent(self._generate)
        return agent.run(state)

    def scientific_plausibility_agent(self, state: AgentState) -> dict:
        state['logs'].append("📊 Plausibility Verification Agent Activated")
        state['logs'].append("Cross-referencing architecture details with benchmark claims...")
        state['logs'].append(f"Analyzing {len(state.get('claims', {}))} primary claims against domain knowledge...")

        # Shared context from repo intelligence
        repo_analysis = state.get('repo_analysis', {})
        artifacts = repo_analysis.get('artifacts', {})
        detected = repo_analysis.get('detected_list', [])
        missing = repo_analysis.get('missing_list', [])
        repo_status = repo_analysis.get('status', 'No Repository Provided')
        limitation_keys = repo_analysis.get('confidence_impact', {}).get('limitation_keys', [])
        arch = state.get('architecture_details', {})

        prompt = f"""You are the Scientific Plausibility Agent for VerifyAI — a professional scientific auditor.
Your goal is to evaluate the logical consistency and scientific plausibility of research claims.

Use the REAL architecture and repository evidence below to ground your reasoning.
Be SPECIFIC. Reference exact model names, parameter counts, and benchmark values.

Shared Context:
- Domain: {state.get('research_domain')}
- Architecture: {json.dumps(arch)}
- Primary Claims: {json.dumps(state.get('claims', {}))}
- Repository Status: {repo_status}
- Confirmed Artifacts: {detected}
- Recorded Limitations: {limitation_keys}

TASK: Evaluate the feasibility of the reported results given the described methodology and infrastructure.
Use calibrated academic language: "Strong benchmark claim", "Consistent with stated compute", "Ambitious claim — requires validation".

Respond ONLY in JSON:
{{
    "claim_plausibility_analysis": [
        {{
            "check": "Architecture & Parameter Consistency",
            "status": "Consistent|Plausible|Requires Independent Validation",
            "reason": "Reason specifically about the {arch.get('parameter_count','stated')} parameters and {arch.get('key_technique','methodology')}.",
            "certainty_level": "High|Moderate|Low"
        }},
        {{
            "check": "Benchmark Realism Assessment",
            "status": "Consistent|Competitive with SOTA|Ambitious — Requires Validation",
            "reason": "Analyze specific benchmark values vs domain baselines.",
            "certainty_level": "High|Moderate|Low"
        }},
        {{
            "check": "Compute & Training Feasibility",
            "status": "Plausible|Evidence Partially Available|Requires Independent Validation",
            "reason": "Analyze if the training infrastructure matches the model scale.",
            "certainty_level": "High|Moderate|Low"
        }}
    ],
    "evidence_verification": [
        {{
            "dimension": "Repository Completeness",
            "status": "Fully Supported|Partially Supported|Limited Evidence Available",
            "detail": "What was structurally verified via static repository analysis."
        }},
        {{
            "dimension": "Documentation Quality",
            "status": "Fully Supported|Partially Supported|Limited Evidence Available",
            "detail": "Quality of README, paper, and inline documentation."
        }},
        {{
            "dimension": "Benchmark Transparency",
            "status": "Fully Supported|Partially Supported|Limited Evidence Available",
            "detail": "Whether benchmark details, datasets, and evaluation protocols are clearly specified."
        }},
        {{
            "dimension": "Reproducibility Support",
            "status": "Fully Supported|Partially Supported|Limited Evidence Available",
            "detail": "Artifact-based assessment of whether the paper can be reproduced."
        }},
        {{
            "dimension": "Methodological Clarity",
            "status": "Fully Supported|Partially Supported|Limited Evidence Available",
            "detail": "Clarity of training, evaluation, and experimental procedures."
        }}
    ]
}}
"""
        data = self._generate(prompt)
        state['logs'].append("Benchmark plausibility and evidence verification complete.")
        return data


    def reproducibility_auditor_agent(self, state: AgentState) -> dict:
        state['logs'].append("🔬 Reproducibility Auditor Agent Activated")
        state['logs'].append("Computing structural transparency and credibility scores...")
        state['logs'].append("Weighing repository evidence, documentation, and engineering signals...")

        repo_analysis = state.get('repo_analysis', {})
        repo_artifacts = repo_analysis.get('artifacts', {})
        repo_status = repo_analysis.get('status', 'Unknown')
        detected = repo_analysis.get('detected_list', [])
        missing = repo_analysis.get('missing_list', [])
        community = repo_analysis.get('community_signals', {})
        limitation_keys = repo_analysis.get('confidence_impact', {}).get('limitation_keys', [])
        arch = state.get('architecture_details', {})

        prompt = f"""You are the Reproducibility Auditor Agent for VerifyAI.
Generate a high-fidelity transparency audit based on the provided evidence.

SCORING RULES:
- Weigh: repo structure, documentation, benchmark transparency, configs, checkpoints, citations, engineering maturity, community signals.
- Reference specific architecture details: {json.dumps(arch)}
- Credibility Score: 65-90 for solid papers; only below 50 for severe issues.

Context:
- Architecture: {json.dumps(arch)}
- Methodology Matrix: {json.dumps(state.get('methodology_matrix', {}))}
- Repository Status: {repo_status}
- Confirmed Artifacts: {detected}
- Absent Artifacts: {missing}
- Community Signals: Stars: {community.get('stars',0)}, Forks: {community.get('forks',0)}

Respond ONLY in JSON:
{{
    "transparency_score": <float 0-100>,
    "methodology_score": <float 0-100>,
    "credibility_score": <float 0-100>,
    "trust_timeline": [
        {{"event": "Specific trust signal from repo or paper", "impact": "positive|negative", "score_change": <int>}}
    ]
}}
"""
        data = self._generate(prompt)
        state['logs'].append("Credibility and transparency scores computed from evidence.")
        return data

    def reviewer_simulation_agent(self, state: AgentState) -> dict:
        state['logs'].append("👨‍⚖️ Reviewer Simulation Agent Activated")
        state['logs'].append("Assembling 5-panel peer review board...")
        state['logs'].append("Synthesizing balanced, constructive scientific perspectives...")

        repo_analysis = state.get('repo_analysis', {})
        repo_status = repo_analysis.get('status', 'Unknown')
        detected = repo_analysis.get('detected_list', [])
        missing = repo_analysis.get('missing_list', [])
        community = repo_analysis.get('community_signals', {})
        limitation_keys = repo_analysis.get('confidence_impact', {}).get('limitation_keys', [])
        research_strengths = state.get('research_strengths', {})
        repro_assessment = state.get('reproducibility_evidence_analysis', {}).get('structural_reproducibility_assessment', '')
        arch = state.get('architecture_details', {})

        prompt = f"""You are the Reviewer Simulation Agent for VerifyAI. Generate a 5-panel peer review board.
This is a balanced scientific transparency audit — NOT a forensic fraud detector.

Use exact details:
- Model/Architecture: {json.dumps(arch)}
- Repository Evidence: {detected}
- Research Strengths: {json.dumps(research_strengths)}

Respond ONLY in JSON:
{{
    "executive_summary": "Balanced 2-3 sentence summary acknowledging specific contributions (e.g. {arch.get('model_name','the model')}) and repository evidence.",
    "research_personality": "E.g., Empirically Grounded Systems Research",
    "reviewer_consensus": {{
        "Academic Reviewer": {{
            "perspective": "Scientific novelty and rigor of {arch.get('key_technique','the method')}.",
            "strengths": "Specific academic strengths...",
            "limitations": "Calibrated limitations...",
            "constructive_concerns": "Professional concerns...",
            "actionable_improvements": "Actionable steps...",
            "confidence_level": "High|Moderate|Low"
        }},
        "Industry Engineering Lead": {{
            "perspective": "Engineering maturity and deployability based on {detected}.",
            "strengths": "...", "limitations": "...", "constructive_concerns": "...",
            "actionable_improvements": "...", "confidence_level": "High|Moderate|Low"
        }},
        "Reproducibility Reviewer": {{
            "perspective": "Artifact-based validation summary.",
            "strengths": "...", "limitations": "...", "constructive_concerns": "...",
            "actionable_improvements": "...", "confidence_level": "High|Moderate|Low"
        }},
        "Open Source Maintainer": {{
            "perspective": "Community usability and documentation quality.",
            "strengths": "...", "limitations": "...", "constructive_concerns": "...",
            "actionable_improvements": "...", "confidence_level": "High|Moderate|Low"
        }},
        "Ethics & Bias Reviewer": {{
            "perspective": "Scientific integrity and fairness of evaluation.",
            "strengths": "...", "limitations": "...", "constructive_concerns": "...",
            "actionable_improvements": "...", "confidence_level": "High|Moderate|Low"
        }}
    }},
    "reviewer_questions": [
        "Constructive expert question 1...",
        "Constructive expert question 2...",
        "Constructive expert question 3..."
    ],
    "final_reviewer_perspective": "Balanced, fair, definitive concluding statement referencing {arch.get('model_name','the paper')}."
}}
"""
        data = self._generate(prompt)
        state['logs'].append("5-panel peer review simulation complete.")
        return data


def build_graph(model_name="gemini-2.5-flash", api_key=None):
    agent = VerifyAIMultiAgentSystem(model_name, api_key)
    workflow = StateGraph(AgentState)

    workflow.add_node("paper_analysis", agent.paper_analysis_agent)
    workflow.add_node("repository_intelligence", agent.repository_intelligence_agent)
    workflow.add_node("scientific_plausibility", agent.scientific_plausibility_agent)
    workflow.add_node("reproducibility_auditor", agent.reproducibility_auditor_agent)
    workflow.add_node("reviewer_simulation", agent.reviewer_simulation_agent)

    workflow.set_entry_point("paper_analysis")
    workflow.add_edge("paper_analysis", "repository_intelligence")
    workflow.add_edge("repository_intelligence", "scientific_plausibility")
    workflow.add_edge("scientific_plausibility", "reproducibility_auditor")
    workflow.add_edge("reproducibility_auditor", "reviewer_simulation")
    workflow.add_edge("reviewer_simulation", END)

    return workflow.compile()

def run_verification(pdf_path: str, repo_url: str = "", model_name="gemini-2.5-flash", api_key=None, github_api_key=None, update_log_callback=None):
    graph = build_graph(model_name, api_key)
    state = {
        "pdf_path": pdf_path, "repo_url": repo_url, "github_api_key": github_api_key,
        "paper_text": "", "claims": {}, "methodology_matrix": {},
        "datasets_detected": [], "repositories_detected": [],
        "repo_analysis": {}, "reproducibility_evidence_analysis": {},
        "transparency_score": 0.0, "methodology_score": 0.0, "credibility_score": 0.0,
        "research_strengths": {}, "architecture_details": {},
        "claim_plausibility_analysis": [], "evidence_verification": [],
        "reviewer_consensus": {}, "trust_timeline": [], "reviewer_questions": [],
        "research_personality": "Unknown", "final_reviewer_perspective": "",
        "executive_summary": "Pending...", "research_domain": "Unknown",
        "paper_positioning": "Unknown", "limitation_keys": [], "logs": []
    }

    for output in graph.stream(state):
        for key, value in output.items():
            if update_log_callback and 'logs' in value:
                if len(value['logs']) > len(state['logs']):
                    for log in value['logs'][len(state['logs']):]:
                        update_log_callback(log)
            for k, v in value.items():
                if k == 'logs': state['logs'] = list(v)
                else: state[k] = v
    return state
