import json
from services.repository_service import RepositoryService

class RepositoryAgent:
    def __init__(self, llm_generate_func):
        self.generate = llm_generate_func

    def _build_confidence_impact(self, artifacts: dict) -> dict:
        boosters, reducers = [], []
        # Track what we add so later agents don't repeat
        limitation_keys = []

        if artifacts.get("requirements.txt") or artifacts.get("environment.yml"):
            boosters.append("Dependency file present — environment setup is reproducible")
        elif artifacts.get("Dockerfile"):
            boosters.append("Dockerfile present — containerized environment defined")
        else:
            reducers.append("No dependency file — environment replication requires manual setup")
            limitation_keys.append("missing_env")

        if artifacts.get("train.py"):
            boosters.append("Training script detected — training pipeline is structurally verifiable")
        else:
            reducers.append("Training script absent — training process not directly inspectable")
            limitation_keys.append("missing_train")

        if artifacts.get("eval.py"):
            boosters.append("Evaluation script detected — reported metrics can be independently traced")
        else:
            reducers.append("Evaluation script absent — metric verification relies on paper description")
            limitation_keys.append("missing_eval")

        if artifacts.get("configs/"):
            boosters.append("Configuration directory present — hyperparameters are externalized")
        else:
            limitation_keys.append("missing_configs")

        if artifacts.get("CI/CD files"):
            boosters.append("CI/CD pipeline detected — automated quality validation present")

        if artifacts.get("README.md"):
            boosters.append("README present — repository documentation available")
        else:
            reducers.append("README absent — onboarding and usage guidance unavailable")
            limitation_keys.append("missing_readme")

        if artifacts.get("notebooks"):
            boosters.append("Jupyter notebooks present — exploratory analysis is visible")

        if artifacts.get("checkpoints"):
            boosters.append("Checkpoint references found — pre-trained weights may be accessible")
        else:
            limitation_keys.append("missing_checkpoints")

        if artifacts.get("inference.py"):
            boosters.append("Inference script present — model deployment path is provided")

        return {"boosters": boosters, "reducers": reducers, "limitation_keys": limitation_keys}

    def run(self, state: dict) -> dict:
        self.repo_service = RepositoryService(github_token=state.get('github_api_key'))
        state['logs'].append("💻 Repository Intelligence Agent Activated")
        repo_url = state.get('repo_url')

        if not repo_url and state.get('repositories_detected'):
            repo_url = state['repositories_detected'][0]
            state['logs'].append(f"Auto-detected repository from paper: {repo_url}")

        if not repo_url:
            state['logs'].append("No repository URL found — skipping repository analysis.")
            return {
                "repo_analysis": {
                    "status": "No Repository Provided",
                    "evidence_matrix": {}, "artifacts": {}, "tree_structure": [],
                    "confidence_impact": {"boosters": [], "reducers": [], "limitation_keys": []},
                    "community_signals": {}
                },
                "reproducibility_evidence_analysis": {}
            }

        state['logs'].append("Inspecting repository structure...")
        state['logs'].append(f"Querying GitHub API for: {repo_url}")
        summary = self.repo_service.extract_repository_summary(repo_url)

        if "error" in summary:
            state['logs'].append(f"Repository access error: {summary.get('error')}")
            return {
                "repo_analysis": {
                    "status": "Repository Unreachable",
                    "error": summary.get('error'), "evidence_matrix": {}, "artifacts": {},
                    "tree_structure": [], "confidence_impact": {}, "community_signals": {}
                },
                "reproducibility_evidence_analysis": {}
            }

        artifacts = summary.get("artifacts", {})
        state['logs'].append("Detecting reproducibility artifacts...")

        detected = [k for k, v in artifacts.items() if v]
        missing = [k for k, v in artifacts.items() if not v]
        state['logs'].append(f"Confirmed: {len(detected)} artifacts | Absent: {len(missing)} artifacts")
        state['logs'].append("Analyzing engineering completeness...")
        state['logs'].append("Computing reproducibility confidence signals...")

        confidence_impact = self._build_confidence_impact(artifacts)
        community_signals = summary.get("community_signals", {})

        prompt = f"""
You are the Repository Intelligence Agent for VerifyAI.
ONLY reason from the REAL detected repository evidence below. DO NOT hallucinate.

Research Domain: {state.get('research_domain')}
Repository URL: {repo_url}
Repository Classification: {summary['status']}

REAL DETECTED ARTIFACTS (True = present, False = absent):
{json.dumps(artifacts, indent=2)}

Confirmed Present: {detected}
Confirmed Absent: {missing}

Repository Tree (actual):
{json.dumps(summary['tree_structure'], indent=2)}

Community Signals:
Stars: {community_signals.get('stars', 'N/A')} | Forks: {community_signals.get('forks', 'N/A')} | Contributors: {community_signals.get('contributors', 'N/A')}

TASK: Write a balanced, specific, evidence-grounded assessment.
- Cite actual detected/absent artifacts.
- Avoid repeating the same limitation more than once.
- Use constructive academic tone.

Respond ONLY in JSON:
{{
    "reproducibility_evidence_analysis": {{
        "structural_reproducibility_assessment": "2-3 sentence balanced assessment citing specific detected artifacts and noting key gaps without being repetitive.",
        "reasoning_traces": [
            "Unique observation 1 — grounded in specific detected/absent artifact",
            "Unique observation 2 — different dimension from #1",
            "Unique observation 3 — different dimension from #1 and #2"
        ],
        "reproducibility_confidence": "High | Moderate | Low",
        "reproducibility_confidence_reason": "One concise sentence citing specific evidence."
    }}
}}
"""

        state['logs'].append("Mapping repository evidence to paper claims...")
        data = self.generate(prompt)

        if "repo_analysis" not in data:
            data["repo_analysis"] = {}

        data["repo_analysis"]["status"] = summary["status"]
        data["repo_analysis"]["evidence_matrix"] = summary["evidence_matrix"]
        data["repo_analysis"]["artifacts"] = artifacts
        data["repo_analysis"]["tree_structure"] = summary["tree_structure"]
        data["repo_analysis"]["confidence_impact"] = confidence_impact
        data["repo_analysis"]["community_signals"] = community_signals
        data["repo_analysis"]["detected_list"] = detected
        data["repo_analysis"]["missing_list"] = missing
        data["repo_url"] = repo_url

        state['logs'].append(f"Repository intelligence complete — {summary['status']}")
        return data
