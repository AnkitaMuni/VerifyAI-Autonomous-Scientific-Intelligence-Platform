import requests
import re

# Nuanced status labels based on what the repo actually provides
_STATUS_LABELS = {
    "inference_only":  "Inference-Focused Repository",
    "research_artifact": "Research Artifact Release",
    "partial_open":    "Partial Open-Source Availability",
    "training_ready":  "Training-Ready Repository",
    "full_stack":      "Full-Stack Research Repository",
    "bare":            "Minimal Repository — Limited Artifacts",
}

class RepositoryService:
    def __init__(self, github_token=None):
        self.base_url = "https://api.github.com"
        self.github_token = github_token

    def _get_headers(self):
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        return headers

    def _parse_github_url(self, url):
        if not url:
            return None, None
        match = re.search(r'github\.com/([^/]+)/([^/]+)', url)
        if match:
            owner, repo = match.groups()
            repo = repo.replace('.git', '')
            return owner, repo
        return None, None

    def extract_repo_info(self, url):
        owner, repo = self._parse_github_url(url)
        if not owner or not repo:
            return {"error": "Invalid or missing GitHub URL"}
        try:
            r = requests.get(f"{self.base_url}/repos/{owner}/{repo}", headers=self._get_headers(), timeout=10)
            return r.json() if r.status_code == 200 else {"error": f"API Error: {r.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def fetch_community_signals(self, url):
        """Fetch real community trust metrics from GitHub API."""
        owner, repo = self._parse_github_url(url)
        if not owner or not repo:
            return {}
        info = self.extract_repo_info(url)
        if "error" in info:
            return {}
        signals = {
            "stars": info.get("stargazers_count", 0),
            "forks": info.get("forks_count", 0),
            "open_issues": info.get("open_issues_count", 0),
            "watchers": info.get("watchers_count", 0),
            "license": info.get("license", {}).get("spdx_id", "None") if info.get("license") else "None",
            "last_updated": info.get("updated_at", "")[:10] if info.get("updated_at") else "Unknown",
            "default_branch": info.get("default_branch", "main"),
            "language": info.get("language", "Unknown"),
            "description": info.get("description", ""),
        }
        # Fetch contributor count
        try:
            cr = requests.get(f"{self.base_url}/repos/{owner}/{repo}/contributors?per_page=1&anon=false",
                              headers=self._get_headers(), timeout=8)
            if cr.status_code == 200:
                # GitHub returns Link header with last page = contributor count (approx)
                link = cr.headers.get("Link", "")
                import re as _re
                m = _re.search(r'page=(\d+)>; rel="last"', link)
                signals["contributors"] = int(m.group(1)) if m else len(cr.json())
            else:
                signals["contributors"] = 0
        except Exception:
            signals["contributors"] = 0
        return signals

    def fetch_repo_tree(self, url):
        repo_info = self.extract_repo_info(url)
        if "error" in repo_info:
            return repo_info
        owner, repo = self._parse_github_url(url)
        default_branch = repo_info.get("default_branch", "main")
        try:
            r = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1",
                headers=self._get_headers(), timeout=10
            )
            return r.json().get("tree", []) if r.status_code == 200 else {"error": f"API Error: {r.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def detect_reproducibility_artifacts(self, tree):
        if isinstance(tree, dict) and "error" in tree:
            return tree
        artifacts = {
            "requirements.txt": False, "environment.yml": False, "Dockerfile": False, "setup.py": False,
            "train.py": False, "main.py": False, "run.py": False,
            "eval.py": False, "test.py": False, "validate.py": False,
            "inference.py": False, "predict.py": False, "serve.py": False,
            "configs/": False, "parameters/": False, "hparams/": False,
            "scripts/": False, "tools/": False, "utils/": False,
            "checkpoints": False, "weights": False, "models/": False,
            "notebooks": False, "examples/": False,
            "CI/CD files": False, ".github/workflows": False,
            "README.md": False, "LICENSE": False, "CONTRIBUTING.md": False
        }
        for item in tree:
            path = item.get("path", "")
            lp = path.lower()
            # Environment
            if lp == "requirements.txt" or lp.endswith("/requirements.txt"): artifacts["requirements.txt"] = True
            elif lp == "environment.yml" or lp.endswith("/environment.yml"): artifacts["environment.yml"] = True
            elif lp == "dockerfile" or lp.endswith("/dockerfile"): artifacts["Dockerfile"] = True
            elif lp == "setup.py" or lp.endswith("/setup.py"): artifacts["setup.py"] = True
            # Training
            elif any(x in lp for x in ["train.py", "training.py", "main.py", "run.py"]): artifacts["train.py"] = True
            # Evaluation
            elif any(x in lp for x in ["eval.py", "evaluate.py", "test.py", "validation.py"]): artifacts["eval.py"] = True
            # Inference
            elif any(x in lp for x in ["inference.py", "predict.py", "serve.py"]): artifacts["inference.py"] = True
            # Configs
            elif "config" in lp or "params" in lp or "hparams" in lp: artifacts["configs/"] = True
            # Scripts/Utils
            elif "script" in lp or "tool" in lp or "util" in lp: artifacts["scripts/"] = True
            # Weights/Checkpoints
            elif any(x in lp for x in ["checkpoint", "weight", "model_weights"]): artifacts["checkpoints"] = True
            elif lp.startswith("models/") or "/models/" in lp: artifacts["models/"] = True
            # Notebooks
            elif lp.endswith(".ipynb") or "notebook" in lp: artifacts["notebooks"] = True
            # CI/CD
            elif ".github/workflows" in lp or ".gitlab-ci.yml" in lp: artifacts["CI/CD files"] = True
            # Documentation
            elif lp == "readme.md": artifacts["README.md"] = True
            elif lp == "license": artifacts["LICENSE"] = True
            elif "contributing" in lp: artifacts["CONTRIBUTING.md"] = True
        return artifacts


    def _classify_status(self, artifacts: dict) -> str:
        has_train = artifacts.get("train.py")
        has_eval = artifacts.get("eval.py")
        has_inference = artifacts.get("inference.py")
        has_env = artifacts.get("requirements.txt") or artifacts.get("environment.yml") or artifacts.get("Dockerfile")
        has_config = artifacts.get("configs/")
        has_readme = artifacts.get("README.md")
        has_ckpt = artifacts.get("checkpoints")
        score = sum(1 for v in artifacts.values() if v)

        if score >= 7 and has_train and has_eval:
            return _STATUS_LABELS["full_stack"]
        if has_train and has_env:
            return _STATUS_LABELS["training_ready"]
        if has_inference and not has_train:
            return _STATUS_LABELS["inference_only"]
        if has_readme and has_ckpt and not has_train:
            return _STATUS_LABELS["research_artifact"]
        if score >= 3:
            return _STATUS_LABELS["partial_open"]
        return _STATUS_LABELS["bare"]

    def extract_repository_summary(self, url):
        info = self.extract_repo_info(url)
        if "error" in info:
            return {"status": "No Repository", "error": info["error"], "evidence_matrix": {}, "artifacts": {}, "tree_structure": [], "community_signals": {}}

        tree = self.fetch_repo_tree(url)
        artifacts = self.detect_reproducibility_artifacts(tree)
        if isinstance(artifacts, dict) and "error" in artifacts:
            return {"status": "Repository Analysis Failed", "error": artifacts["error"], "evidence_matrix": {}, "artifacts": {}, "tree_structure": [], "community_signals": {}}

        status = self._classify_status(artifacts)
        community_signals = self.fetch_community_signals(url)

        tree_paths = [item["path"] for item in (tree if isinstance(tree, list) else []) if item.get("type") in ["blob", "tree"]]
        clean_tree = sorted([p for p in tree_paths if len(p.split('/')) <= 2])[:30]

        evidence_matrix = {
            "Environment Config": "✅ Present" if (artifacts.get("requirements.txt") or artifacts.get("environment.yml") or artifacts.get("Dockerfile") or artifacts.get("setup.py")) else "⚠️ Not detected",
            "Training Pipeline": "✅ Present" if artifacts.get("train.py") else "⚠️ Not detected",
            "Evaluation Logic": "✅ Present" if artifacts.get("eval.py") else "⚠️ Not detected",
            "Inference Script": "✅ Present" if artifacts.get("inference.py") else "⚠️ Not detected",
            "Configurations": "✅ Present" if artifacts.get("configs/") else "⚠️ Not detected",
            "Pre-trained Checkpoints": "✅ Present" if artifacts.get("checkpoints") else "⚠️ Not detected",
            "Documentation (README)": "✅ Present" if artifacts.get("README.md") else "⚠️ Not detected",
            "CI/CD Pipeline": "✅ Present" if artifacts.get("CI/CD files") else "⚠️ Not detected",
            "Open Source License": "✅ Present" if artifacts.get("LICENSE") else "⚠️ Not detected",
            "Contributing Guide": "✅ Present" if artifacts.get("CONTRIBUTING.md") else "⚠️ Not detected",
        }

        return {
            "status": status,
            "evidence_matrix": evidence_matrix,
            "artifacts": artifacts,
            "tree_structure": clean_tree,
            "community_signals": community_signals,
            "branch": info.get("default_branch", "main"),
            "owner": info.get("owner", {}).get("login", "Unknown"),
            "name": info.get("name", "Unknown"),
        }

