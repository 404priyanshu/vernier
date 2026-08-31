from __future__ import annotations

import re
from dataclasses import dataclass

from app.services.diff import Hunk

SEVERITY_RANK = {
    "critical": 10,
    "high": 20,
    "medium": 40,
    "low": 60,
    "info": 80,
}


@dataclass
class HeuristicHit:
    detector_id: str
    category: str
    severity: str
    title: str
    description: str
    file_path: str
    start_line: int | None
    end_line: int | None
    snippet: str
    confidence: float = 0.78


@dataclass(frozen=True)
class Detector:
    detector_id: str
    category: str
    severity: str
    title: str
    description: str
    pattern: re.Pattern[str]
    languages: tuple[str, ...] = ()
    confidence: float = 0.78


def _ext(path: str) -> str:
    if "." not in path:
        return ""
    return path.rsplit(".", 1)[-1].lower()


DETECTORS: list[Detector] = [
    Detector(
        detector_id="sql_fstring",
        category="security",
        severity="critical",
        title="SQL query built with a formatted string",
        description="User-controlled values interpolated into SQL can become injection. Use bound parameters.",
        pattern=re.compile(
            r"""(?:execute\s*\(\s*f["'])|(?:query\s*=\s*f["'][^;\n]*\bSELECT\b)|(?:f["']\s*SELECT\b)""",
            re.IGNORECASE,
        ),
        languages=("py", "pyi"),
        confidence=0.9,
    ),
    Detector(
        detector_id="sql_concat",
        category="security",
        severity="critical",
        title="SQL string concatenation",
        description="Concatenating SQL fragments with user input is a classic injection sink.",
        pattern=re.compile(r"""(["']\s*SELECT\s+.*["']\s*\+)|(\+\s*["']\s*(WHERE|AND|OR)\b)""", re.IGNORECASE),
        confidence=0.86,
    ),
    Detector(
        detector_id="pickle_loads",
        category="security",
        severity="critical",
        title="Unsafe pickle deserialization",
        description="pickle.loads on untrusted bytes can execute arbitrary Python. Prefer JSON or a signed serializer.",
        pattern=re.compile(r"\bpickle\.loads\s*\("),
        languages=("py", "pyi"),
        confidence=0.95,
    ),
    Detector(
        detector_id="yaml_unsafe_load",
        category="security",
        severity="high",
        title="Unsafe YAML load",
        description="yaml.load without a SafeLoader can construct arbitrary objects. Use yaml.safe_load.",
        pattern=re.compile(r"\byaml\.load\s*\("),
        languages=("py", "pyi"),
        confidence=0.88,
    ),
    Detector(
        detector_id="shell_true",
        category="security",
        severity="high",
        title="subprocess invoked with shell=True",
        description="shell=True sends the command through a shell, which turns untrusted input into command injection.",
        pattern=re.compile(r"\bsubprocess\.\w+\s*\([^)]*shell\s*=\s*True"),
        languages=("py", "pyi"),
        confidence=0.92,
    ),
    Detector(
        detector_id="os_system",
        category="security",
        severity="high",
        title="os.system or os.popen call",
        description="These helpers always use a shell. Prefer subprocess with a list of arguments.",
        pattern=re.compile(r"\bos\.(system|popen)\s*\("),
        languages=("py", "pyi"),
        confidence=0.9,
    ),
    Detector(
        detector_id="eval_exec",
        category="security",
        severity="critical",
        title="Dynamic code execution",
        description="eval/exec/Function compile and run strings as code. Treat any untrusted argument as RCE.",
        pattern=re.compile(r"\b(eval|exec)\s*\(|new\s+Function\s*\("),
        confidence=0.9,
    ),
    Detector(
        detector_id="innerhtml",
        category="security",
        severity="high",
        title="HTML injected via innerHTML",
        description="Assigning untrusted strings to innerHTML or dangerouslySetInnerHTML is an XSS sink.",
        pattern=re.compile(r"\.(innerHTML|outerHTML)\s*=|dangerouslySetInnerHTML"),
        languages=("js", "jsx", "ts", "tsx", "vue", "html"),
        confidence=0.84,
    ),
    Detector(
        detector_id="hardcoded_secret",
        category="security",
        severity="high",
        title="Hardcoded credential",
        description="A secret appears to be committed in source. Move it to an environment variable or a secret manager.",
        pattern=re.compile(
            r"""(?i)\b(api[_-]?key|secret[_-]?key|password|token|aws_secret_access_key)\b\s*=\s*['"][^'"]{8,}['"]"""
        ),
        confidence=0.8,
    ),
    Detector(
        detector_id="md5_password",
        category="security",
        severity="high",
        title="Weak hash used for a secret",
        description="MD5 and SHA1 are not password hashes. Use a slow KDF such as argon2 or bcrypt.",
        pattern=re.compile(r"hashlib\.(md5|sha1)\s*\(|createHash\(\s*['\"]md5['\"]"),
        confidence=0.74,
    ),
    Detector(
        detector_id="insecure_random",
        category="security",
        severity="medium",
        title="Non-crypto RNG used for a token",
        description="random.random / Math.random are predictable. Use secrets.token_urlsafe or crypto.getRandomValues.",
        pattern=re.compile(r"""(random\.(random|randint|choice)\s*\(.*(?:token|secret|password)|Math\.random\s*\(\s*\).*token)""", re.IGNORECASE),
        confidence=0.7,
    ),
    Detector(
        detector_id="debug_true",
        category="security",
        severity="medium",
        title="Debug mode enabled",
        description="Debug flags leak stack traces and sometimes an interactive console. Keep them off outside local dev.",
        pattern=re.compile(r"\b(DEBUG|debug)\s*=\s*True\b|app\.debug\s*=\s*True"),
        confidence=0.72,
    ),
    Detector(
        detector_id="cors_star",
        category="security",
        severity="medium",
        title="CORS allows any origin",
        description="allow_origins=['*'] or Access-Control-Allow-Origin: * lets any site read authenticated responses.",
        pattern=re.compile(r"""allow_origins\s*=\s*\[[^\]]*(['"]\*['"])|Access-Control-Allow-Origin['\"]?\s*[:=]\s*['"]\*['"]"""),
        confidence=0.76,
    ),
    Detector(
        detector_id="jwt_skip_verify",
        category="security",
        severity="critical",
        title="JWT signature verification skipped",
        description="decode(..., verify=False) or algorithms=['none'] accepts forged tokens.",
        pattern=re.compile(r"verify\s*=\s*False|algorithms\s*=\s*\[[^\]]*none", re.IGNORECASE),
        confidence=0.9,
    ),
    Detector(
        detector_id="n_plus_one",
        category="performance",
        severity="medium",
        title="Query inside a loop",
        description="A database or HTTP call inside a loop is a common N+1. Batch the lookup or join instead.",
        pattern=re.compile(
            r"for\s+\w+\s+in\s+\w+.+:\n(?:[ \t].+\n)*?[ \t].*(?:\.query\(|\.filter\(|\.get\(|\.execute\(|fetch\(|requests\.(get|post))",
            re.IGNORECASE,
        ),
        confidence=0.66,
    ),
    Detector(
        detector_id="blocking_in_async",
        category="performance",
        severity="medium",
        title="Blocking call inside async code",
        description="time.sleep and synchronous HTTP clients stall the event loop. Use asyncio.sleep or an async client.",
        pattern=re.compile(r"\b(time\.sleep\s*\(|requests\.(get|post|put|delete)\s*\()"),
        languages=("py", "pyi"),
        confidence=0.68,
    ),
    Detector(
        detector_id="nested_loops",
        category="performance",
        severity="low",
        title="Nested iteration over collections",
        description="Nested loops over request-sized lists often become quadratic. Consider a dict index or a set.",
        pattern=re.compile(r"for\s+\w+\s+in\s+\w+.+:\n(?:[ \t].+\n)*?[ \t]+for\s+\w+\s+in\s+\w+"),
        confidence=0.55,
    ),
    Detector(
        detector_id="mutable_default",
        category="bug",
        severity="medium",
        title="Mutable default argument",
        description="A list or dict default is shared across calls, which leaks state between requests.",
        pattern=re.compile(r"def\s+\w+\s*\([^)]*=\s*(\[\]|\{\})"),
        languages=("py", "pyi"),
        confidence=0.88,
    ),
    Detector(
        detector_id="bare_except",
        category="bug",
        severity="low",
        title="Bare except clause",
        description="except: swallows SystemExit and KeyboardInterrupt. Catch a concrete exception instead.",
        pattern=re.compile(r"except\s*:"),
        languages=("py", "pyi"),
        confidence=0.8,
    ),
    Detector(
        detector_id="is_none_eq",
        category="bug",
        severity="low",
        title="Identity check written as equality",
        description="Comparisons to None should use `is` / `is not`. `== None` breaks when __eq__ is overloaded.",
        pattern=re.compile(r"==\s*None|!=\s*None"),
        languages=("py", "pyi"),
        confidence=0.7,
    ),
    Detector(
        detector_id="todo_fixme",
        category="bug",
        severity="info",
        title="FIXME or XXX left in new code",
        description="The author marked this path as unfinished. Confirm it should ship.",
        pattern=re.compile(r"\b(FIXME|XXX)\b"),
        confidence=0.5,
    ),
]


def _line_for_match(hunk: Hunk, match_text: str) -> tuple[int | None, str]:
    needle = match_text.strip().splitlines()[0][:80]
    for line in hunk.lines:
        if line.kind != "add":
            continue
        if needle[:40] in line.text or line.text.strip()[:40] in needle:
            return line.new_line, line.text
    added = [line for line in hunk.lines if line.kind == "add"]
    if added:
        return added[0].new_line, added[0].text
    start, _ = hunk.new_line_span
    return start, hunk.added_text[:200]


def scan_hunk(hunk: Hunk) -> list[HeuristicHit]:
    added = hunk.added_text
    if not added.strip():
        return []
    ext = _ext(hunk.file_path)
    hits: list[HeuristicHit] = []
    seen: set[str] = set()
    for detector in DETECTORS:
        if detector.languages and ext and ext not in detector.languages:
            continue
        match = detector.pattern.search(added)
        if not match:
            continue
        key = detector.detector_id
        if key in seen:
            continue
        seen.add(key)
        line_no, snippet = _line_for_match(hunk, match.group(0))
        hits.append(
            HeuristicHit(
                detector_id=detector.detector_id,
                category=detector.category,
                severity=detector.severity,
                title=detector.title,
                description=detector.description,
                file_path=hunk.file_path,
                start_line=line_no,
                end_line=line_no,
                snippet=snippet.strip(),
                confidence=detector.confidence,
            )
        )
    return hits


def scan_hunks(hunks: list[Hunk]) -> list[HeuristicHit]:
    hits: list[HeuristicHit] = []
    for hunk in hunks:
        hits.extend(scan_hunk(hunk))
    return hits
