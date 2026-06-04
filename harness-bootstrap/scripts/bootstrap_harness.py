#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


IGNORED_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".venv",
    "venv",
    "__pycache__",
    ".understand-anything",
}

TEXT_EXTS = {
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".py", ".go", ".rs", ".java", ".kt", ".cs", ".rb", ".php",
    ".sh", ".bash", ".zsh", ".ps1",
    ".json", ".jsonc", ".yaml", ".yml", ".toml", ".xml",
    ".md", ".mdx", ".txt", ".env", ".example", ".properties",
}

ENV_PATTERNS = [
    re.compile(r"process\.env\.([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"os\.environ(?:\.get)?\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),
    re.compile(r"getenv\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),
    re.compile(r"import\.meta\.env\.([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"\$([A-Z][A-Z0-9_]{2,})"),
]

OBS_TERMS = [
    "opentelemetry", "otel", "sentry", "datadog", "newrelic",
    "prometheus", "grafana", "honeycomb", "logrocket", "posthog",
    "segment", "winston", "pino", "loguru", "structlog",
]

DESIGN_TERMS = [
    "tailwind", "shadcn", "radix", "mui", "material-ui", "chakra",
    "antd", "bootstrap", "storybook", "figma", "framer-motion",
]

CLI_FILES = [
    "package.json", "pyproject.toml", "requirements.txt", "go.mod",
    "Cargo.toml", "pom.xml", "build.gradle", "build.gradle.kts",
    "Makefile", "Dockerfile", "docker-compose.yml", "compose.yml",
]

CI_DIRS = [".github/workflows", ".gitlab-ci.yml", ".circleci", "azure-pipelines.yml"]


def run(cmd, cwd):
    try:
        out = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=20)
        return {"cmd": " ".join(cmd), "ok": out.returncode == 0, "stdout": out.stdout.strip(), "stderr": out.stderr.strip()}
    except Exception as exc:
        return {"cmd": " ".join(cmd), "ok": False, "stdout": "", "stderr": str(exc)}


def rel(path, root):
    return str(path.relative_to(root)).replace(os.sep, "/")


def list_files(root, limit=2000):
    files = []
    for current, dirs, names in os.walk(root):
        dirs[:] = [d for d in sorted(dirs) if d not in IGNORED_DIRS]
        for name in sorted(names):
            p = Path(current) / name
            files.append(p)
            if len(files) >= limit:
                return files
    return files


def read_text(path, max_chars=200_000):
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except Exception:
        return ""


def read_json(path):
    try:
        return json.loads(read_text(path))
    except Exception:
        return None


def detect_package(root):
    package = read_json(root / "package.json")
    if not package:
        return None
    pm = "npm"
    if (root / "pnpm-lock.yaml").exists():
        pm = "pnpm"
    elif (root / "yarn.lock").exists():
        pm = "yarn"
    elif (root / "bun.lock").exists() or (root / "bun.lockb").exists():
        pm = "bun"
    return {"package": package, "manager": pm, "scripts": package.get("scripts", {})}


def command_for_script(pm, script):
    if script == "test" and pm == "npm":
        return "npm test"
    if script == "test" and pm in {"pnpm", "bun"}:
        return f"{pm} test"
    if script == "test" and pm == "yarn":
        return "yarn test"
    if pm == "npm":
        return f"npm run {script}"
    if pm == "yarn":
        return f"yarn {script}"
    return f"{pm} run {script}"


def detect_commands(root):
    detected = {"install": [], "start": [], "test": [], "check": [], "build": []}
    pkg = detect_package(root)
    if pkg:
        pm = pkg["manager"]
        detected["install"].append("npm install" if pm == "npm" else f"{pm} install")
        scripts = pkg["scripts"]
        for key in ["dev", "start", "serve"]:
            if key in scripts:
                detected["start"].append(command_for_script(pm, key))
        for key in ["test", "test:unit", "test:e2e"]:
            if key in scripts:
                detected["test"].append(command_for_script(pm, key))
        for key in ["check", "typecheck", "type-check", "lint"]:
            if key in scripts:
                detected["check"].append(command_for_script(pm, key))
        if "build" in scripts:
            detected["build"].append(command_for_script(pm, "build"))
    if (root / "Makefile").exists():
        mk = read_text(root / "Makefile")
        for target, bucket in [("setup", "install"), ("dev", "start"), ("test", "test"), ("check", "check"), ("build", "build")]:
            if re.search(rf"^{target}:", mk, re.M):
                detected[bucket].append(f"make {target}")
    if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
        detected["test"].append("python -m pytest")
        detected["check"].append("python -m compileall .")
    if (root / "go.mod").exists():
        detected["test"].append("go test ./...")
    if (root / "Cargo.toml").exists():
        detected["test"].append("cargo test")
    return {k: sorted(set(v)) for k, v in detected.items()}


def detect_stack(root, files):
    stack = []
    pkg = detect_package(root)
    deps = {}
    if pkg:
        package = pkg["package"]
        deps.update(package.get("dependencies", {}))
        deps.update(package.get("devDependencies", {}))
        stack.append("node")
        for dep, label in [
            ("react", "react"), ("next", "nextjs"), ("vue", "vue"), ("svelte", "svelte"),
            ("vite", "vite"), ("electron", "electron"), ("express", "express"),
            ("fastify", "fastify"), ("typescript", "typescript"),
        ]:
            if dep in deps:
                stack.append(label)
    markers = [
        ("pyproject.toml", "python"), ("requirements.txt", "python"),
        ("go.mod", "go"), ("Cargo.toml", "rust"), ("pom.xml", "java-maven"),
    ]
    for marker, label in markers:
        if (root / marker).exists():
            stack.append(label)
    return sorted(set(stack))


def scan_env(root, files):
    refs = {}
    env_files = []
    for p in files:
        rp = rel(p, root)
        if p.name.startswith(".env") or p.name.endswith(".env") or ".env." in p.name:
            env_files.append(rp)
        if p.suffix.lower() not in TEXT_EXTS and not p.name.startswith(".env"):
            continue
        text = read_text(p, max_chars=60_000)
        if not text:
            continue
        for pattern in ENV_PATTERNS:
            for match in pattern.findall(text):
                if match in {"HOME", "PATH", "PWD", "SHELL", "USER"}:
                    continue
                refs.setdefault(match, set()).add(rp)
    return {"envFiles": sorted(env_files), "references": {k: sorted(v) for k, v in sorted(refs.items())}}


def scan_terms(root, files, terms):
    hits = {}
    pattern = re.compile("|".join(re.escape(t) for t in terms), re.I)
    for p in files:
        if p.suffix.lower() not in TEXT_EXTS:
            continue
        text = read_text(p, max_chars=80_000)
        found = sorted(set(m.group(0).lower() for m in pattern.finditer(text)))
        if found:
            hits[rel(p, root)] = found[:10]
    return hits


def scan_ci(root):
    found = []
    for item in CI_DIRS:
        p = root / item
        if p.is_dir():
            found.extend(rel(f, root) for f in sorted(p.glob("**/*")) if f.is_file())
        elif p.exists():
            found.append(item)
    for name in ["Dockerfile", "docker-compose.yml", "compose.yml", "fly.toml", "vercel.json", "netlify.toml", "render.yaml", "railway.toml"]:
        if (root / name).exists():
            found.append(name)
    return sorted(set(found))


def understand_status(root):
    ua = root / ".understand-anything"
    graph = ua / "knowledge-graph.json"
    if not graph.exists():
        return {"present": False}
    meta = read_json(ua / "meta.json") or {}
    head = run(["git", "rev-parse", "HEAD"], root)
    stale = None
    if head["ok"] and meta.get("gitCommitHash"):
        stale = meta.get("gitCommitHash") != head["stdout"]
    size = graph.stat().st_size
    return {
        "present": True,
        "graph": ".understand-anything/knowledge-graph.json",
        "sizeBytes": size,
        "largeGraph": size > 10 * 1024 * 1024,
        "metaCommit": meta.get("gitCommitHash"),
        "headCommit": head["stdout"] if head["ok"] else None,
        "stale": stale,
    }


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def bullet(items, empty="None detected."):
    if not items:
        return f"- {empty}"
    return "\n".join(f"- {item}" for item in items)


def gate(name, ready, detail, missing=None):
    return {"name": name, "ready": bool(ready), "detail": detail, "missing": missing or []}


def build_report(root, args):
    files = list_files(root)
    stack = detect_stack(root, files)
    commands = detect_commands(root)
    env = scan_env(root, files)
    ci = scan_ci(root)
    obs = scan_terms(root, files, OBS_TERMS)
    design = scan_terms(root, files, DESIGN_TERMS)
    ua = understand_status(root)
    manifests = [name for name in CLI_FILES if (root / name).exists()]
    docs = [rel(p, root) for p in files if p.suffix.lower() in {".md", ".mdx", ".rst"}][:200]

    install_known = bool(commands["install"])
    start_known = bool(commands["start"])
    verify_known = bool(commands["test"] or commands["check"] or commands["build"])
    env_known = bool(env["references"] or env["envFiles"])
    deploy_known = bool(ci)
    obs_known = bool(obs)
    design_known = bool(design) or not any(s in stack for s in ["react", "nextjs", "vue", "svelte", "vite"])
    knowledge_known = bool(ua.get("present")) or bool(files)

    gates = [
        gate("instruction_surface", True, ".harness/INDEX.md generated"),
        gate("environment", install_known and start_known, "Install and startup commands inferred where possible", [] if install_known and start_known else [m for m, ok in [("Install command unknown", install_known), ("Startup command unknown", start_known)] if not ok]),
        gate("verification", verify_known, "Verification commands inferred from manifests/scripts", [] if verify_known else ["No test/check/build command detected"]),
        gate("architecture", bool(stack or manifests), "Stack and repo map inferred", [] if stack or manifests else ["No stack manifest detected"]),
        gate("tooling", bool(manifests), "Tooling manifests detected", [] if manifests else ["No package/build manifests detected"]),
        gate("deployment", deploy_known, "CI/CD or deploy files detected", [] if deploy_known else ["Deployment target/path unknown"]),
        gate("observability", obs_known, "Logging/telemetry clues detected", [] if obs_known else ["Logs/telemetry/error reporting unknown"]),
        gate("design_language", design_known, "Design/UI clues detected or frontend not detected", [] if design_known else ["Frontend design language unknown"]),
        gate("knowledge", knowledge_known, "Repo map generated; Understand Anything status recorded"),
        gate("fresh_session_test", install_known and verify_known and bool(stack or docs), "Fresh-session questions have partial evidence", [] if install_known and verify_known else ["Fresh-session test cannot pass until run/verify path is known"]),
    ]

    ready_count = sum(1 for g in gates if g["ready"])
    critical_questions = []
    if not start_known:
        critical_questions.append("canonical local startup command")
    if not verify_known:
        critical_questions.append("base readiness verification gate")
    if not deploy_known:
        critical_questions.append("deployment target/release path")
    if not obs_known:
        critical_questions.append("logs/telemetry/error source")

    if all(g["ready"] for g in gates) and not critical_questions:
        status = "READY"
    elif ready_count >= 5:
        status = "PARTIALLY READY"
    else:
        status = "NOT READY"

    questions = []
    if not start_known:
        questions.append("What is the canonical local startup command?")
    if not verify_known:
        questions.append("What command is the base readiness verification gate?")
    if not deploy_known:
        questions.append("What deployment target and release path should agents know?")
    if not obs_known:
        questions.append("Where should agents inspect logs, errors, metrics, or traces?")
    if env["references"]:
        questions.append("Which detected env vars are required for local, test, staging, and production?")
    if not ua.get("present"):
        questions.append("Should Understand Anything be enabled for incremental codebase knowledge?")

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "target": str(root),
        "status": status,
        "stack": stack,
        "commands": commands,
        "env": env,
        "ciCdFiles": ci,
        "observabilityHits": obs,
        "designHits": design,
        "manifests": manifests,
        "docs": docs,
        "understandAnything": ua,
        "gates": gates,
        "questions": questions,
    }


def render_files(root, report, with_root_router=False):
    h = root / ".harness"
    write(h / "INDEX.md", f"""# Harness Index

This directory is the agent-readiness surface for this repository.

Status: **{report['status']}**

Start here:
- `READINESS.md` — current readiness status and missing items
- `FRESH_SESSION_TEST.md` — cold-agent questions and answers
- `ENVIRONMENT.md` — runtime, startup, and env vars
- `TESTING.md` — base verification commands
- `TOOLING.md` — CLIs, MCPs, and skills
- `DEPLOYMENT.md` — CI/CD and release path
- `OBSERVABILITY.md` — logs, metrics, traces, errors
- `KNOWLEDGE.md` — repo map and Understand Anything status

Rule: use `.harness/` for readiness facts; do not rely on chat history.
""")

    ready = [g for g in report["gates"] if g["ready"]]
    missing = [g for g in report["gates"] if not g["ready"]]
    write(h / "READINESS.md", f"""# Harness Readiness

Status: **{report['status']}**

Generated: {report['generatedAt']}

## Ready Gates

{bullet([f"{g['name']}: {g['detail']}" for g in ready])}

## Not Ready

{bullet([f"{g['name']}: {', '.join(g['missing']) or g['detail']}" for g in missing], "No missing gates.")}

## Questions

{bullet(report['questions'], "No questions.")}
""")

    commands = report["commands"]
    write(h / "ENVIRONMENT.md", f"""# Environment

## Detected Stack

{bullet(report['stack'], "No stack detected.")}

## Install Commands

{bullet(commands['install'])}

## Start Commands

{bullet(commands['start'])}

## Env Files

{bullet(report['env']['envFiles'], "No env files detected.")}

## Env Vars Referenced

{bullet([f"{name}: {', '.join(paths[:5])}" for name, paths in report['env']['references'].items()], "No env references detected.")}

Secret values are intentionally not captured.
""")

    write(h / "TESTING.md", f"""# Testing And Verification

## Test Commands

{bullet(commands['test'])}

## Check Commands

{bullet(commands['check'])}

## Build Commands

{bullet(commands['build'])}

Readiness requires at least one known verification path. If no command is detected, ask the user for the canonical base gate.
""")

    write(h / "TOOLING.md", f"""# Tooling

## Manifests And Tool Files

{bullet(report['manifests'], "No common tooling manifests detected.")}

## MCP Servers

- Unknown. Ask the user which MCP servers are required.

## Agent Skills

- Unknown. Ask the user which skills are required or recommended.
""")

    write(h / "DEPLOYMENT.md", f"""# Deployment

## CI/CD And Deploy Files

{bullet(report['ciCdFiles'], "No CI/CD or deploy files detected.")}

## Canonical Release Path

- Unknown unless documented above. Ask the user if this remains blank.
""")

    write(h / "OBSERVABILITY.md", f"""# Observability

## Detected Logging / Telemetry Clues

{bullet([f"{path}: {', '.join(terms)}" for path, terms in report['observabilityHits'].items()], "No observability clues detected.")}

Document where agents should inspect local logs, production logs, metrics, traces, errors, and health checks.
""")

    write(h / "DESIGN_LANGUAGE.md", f"""# Design Language

## Detected Design / UI Clues

{bullet([f"{path}: {', '.join(terms)}" for path, terms in report['designHits'].items()], "No design-system clues detected.")}

If this is a frontend repo, document UI libraries, tokens, component conventions, accessibility expectations, and visual QA commands.
""")

    ua = report["understandAnything"]
    ua_lines = ["Understand Anything is not detected."]
    if ua.get("present"):
        ua_lines = [
            f"Graph: `{ua['graph']}`",
            f"Size bytes: {ua['sizeBytes']}",
            f"Stale: {ua.get('stale')}",
            f"Large graph: {ua.get('largeGraph')}",
        ]
        if ua.get("largeGraph"):
            ua_lines.append("Git LFS is acceptable for large `.understand-anything/*.json` artifacts.")
    write(h / "KNOWLEDGE.md", f"""# Codebase Knowledge

## Understand Anything

{bullet(ua_lines)}

## Repo Map

See `generated/repo-map.md`.
""")

    write(h / "FRESH_SESSION_TEST.md", f"""# Fresh Session Test

A cold agent should answer these from repo artifacts only.

| Question | Current Evidence |
|---|---|
| What is this system? | README/docs: {len(report['docs'])} markdown files detected |
| How is it organized? | Stack: {', '.join(report['stack']) or 'unknown'} |
| How do I run it? | {', '.join(commands['start']) or 'unknown'} |
| How do I verify it? | {', '.join(commands['test'] + commands['check'] + commands['build']) or 'unknown'} |
| What env/tools are required? | Env refs: {len(report['env']['references'])}; manifests: {len(report['manifests'])} |
| Where are deploy/observability signals? | Deploy files: {len(report['ciCdFiles'])}; observability hits: {len(report['observabilityHits'])} |

Result: **{report['status']}**
""")

    write(h / "SECURITY.md", "# Security\n\nSecret values are not captured. Document auth boundaries, secret stores, permission rules, data classification, and unsafe operations here.\n")
    write(h / "QUALITY.md", "# Quality\n\nTrack weak modules, flaky tests, stale docs, cleanup debt, and recurring review feedback here.\n")
    write(h / "RUNBOOKS.md", "# Runbooks\n\nAdd local development, debugging, release, and incident-response runbooks here.\n")

    generated = h / "generated"
    write(generated / "repo-map.md", "\n".join([
        "# Generated Repo Map",
        "",
        f"Target: `{report['target']}`",
        "",
        "## Stack",
        "",
        bullet(report["stack"]),
        "",
        "## Markdown Docs",
        "",
        bullet(report["docs"][:100], "No docs detected."),
    ]))
    write(generated / "env-scan.md", read_text(h / "ENVIRONMENT.md"))
    write(generated / "test-scan.md", read_text(h / "TESTING.md"))
    write(generated / "ci-cd-scan.md", read_text(h / "DEPLOYMENT.md"))
    write(generated / "observability-scan.md", read_text(h / "OBSERVABILITY.md"))
    write(generated / "readiness-report.json", json.dumps(report, indent=2))

    state = h / "state"
    write(state / "questions.md", "# Open Questions\n\n" + bullet(report["questions"], "No questions."))
    history = state / "validation-history.md"
    old = read_text(history) if history.exists() else "# Validation History\n"
    write(history, old.rstrip() + f"\n\n## {report['generatedAt']}\n\n- Status: {report['status']}\n")

    if with_root_router:
        router = root / "AGENTS.md"
        if not router.exists():
            write(router, "# AGENTS.md\n\nRead `.harness/INDEX.md` before changing code. Treat `.harness/READINESS.md` as the current agent-readiness status.\n")


def main():
    parser = argparse.ArgumentParser(description="Bootstrap .harness readiness artifacts for a repository.")
    parser.add_argument("--target", default=".", help="Target repository")
    parser.add_argument("--with-root-router", action="store_true", help="Create root AGENTS.md router if missing")
    args = parser.parse_args()

    root = Path(args.target).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Target is not a directory: {root}")

    report = build_report(root, args)
    render_files(root, report, with_root_router=args.with_root_router)

    print(f"Harness status: {report['status']}")
    print(f"Artifacts written: {root / '.harness'}")
    if report["questions"]:
        print("Questions:")
        for q in report["questions"]:
            print(f"- {q}")


if __name__ == "__main__":
    main()
