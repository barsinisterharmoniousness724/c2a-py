"""最小 Python 版所需的拒绝检测和身份清洗常量。"""

from __future__ import annotations

import re

REFUSAL_PATTERNS = [
    re.compile(r"Cursor(?:'s)?\s+support\s+assistant", re.I),
    re.compile(r"support\s+assistant\s+for\s+Cursor", re.I),
    re.compile(r"I['\u2019]?\s*m\s+sorry", re.I),
    re.compile(r"I\s+am\s+sorry", re.I),
    re.compile(r"not\s+able\s+to\s+fulfill", re.I),
    re.compile(r"cannot\s+perform", re.I),
    re.compile(r"I\s+can\s+only\s+answer", re.I),
    re.compile(r"I\s+only\s+answer", re.I),
    re.compile(r"I\s+cannot\s+help\s+with", re.I),
    re.compile(r"I'm\s+a\s+coding\s+assistant", re.I),
    re.compile(r"focused\s+on\s+software\s+development", re.I),
    re.compile(r"beyond\s+(?:my|the)\s+scope", re.I),
    re.compile(r"I'?m\s+not\s+(?:able|designed)\s+to", re.I),
    re.compile(r"questions\s+about\s+(?:Cursor|the\s+(?:AI\s+)?code\s+editor)", re.I),
    re.compile(r"I\s+(?:only\s+)?have\s+(?:access\s+to\s+)?(?:two|2|read_file|read_dir)\s+tool", re.I),
    re.compile(r"(?:only|just)\s+(?:two|2)\s+(?:tools?|functions?)\b", re.I),
    re.compile(r"\bread_file\b.*\bread_dir\b", re.I),
    re.compile(r"我是\s*Cursor\s*的?\s*支持助手"),
    re.compile(r"Cursor\s*的?\s*支持系统"),
    re.compile(r"我无法透露"),
    re.compile(r"运行在\s*Cursor\s*的"),
]

IDENTITY_REPLACEMENTS = [
    (re.compile(r"I am the Cursor AI", re.I), "I am Claude"),
    (re.compile(r"I'm the Cursor AI", re.I), "I'm Claude"),
    (re.compile(r"I am Cursor(?:'s)? AI", re.I), "I am Claude"),
    (
        re.compile(r"I am (?:a )?(?:support )?assistant for Cursor", re.I),
        "I am Claude, an AI assistant by Anthropic",
    ),
    (
        re.compile(r"Cursor(?:'s)? support assistant", re.I),
        "Claude, an AI assistant by Anthropic",
    ),
    (re.compile(r"You are using Cursor", re.I), "You are using an AI assistant"),
    (re.compile(r"Cursor AI assistant", re.I), "Claude AI assistant"),
    (re.compile(r"built by Cursor", re.I), "built by Anthropic"),
    (re.compile(r"made by Cursor", re.I), "made by Anthropic"),
    (re.compile(r"created by Cursor", re.I), "created by Anthropic"),
    (re.compile(r"我是\s*Cursor\s*的?\s*支持助手"), "我是 Claude，由 Anthropic 开发的 AI 助手"),
]

IDENTITY_LEAK_PATTERNS = [
    re.compile(r"^x-anthropic-billing-header[^\n]*$", re.I | re.M),
    re.compile(r"^You are Claude Code[^\n]*$", re.I | re.M),
    re.compile(r"^You are Claude,\s+Anthropic's[^\n]*$", re.I | re.M),
    re.compile(r"You are Claude.*?\n", re.I | re.S),
    re.compile(r"You are an? AI assistant made by Anthropic.*?\n", re.I | re.S),
    re.compile(r"<claude_info>.*?</claude_info>", re.I | re.S),
]

IDENTITY_PROBE_PATTERNS = [
    re.compile(r"\bwho are you\b", re.I),
    re.compile(r"\bwhat are you\b", re.I),
    re.compile(r"\bare you claude\b", re.I),
    re.compile(r"你是谁"),
    re.compile(r"你是claude吗", re.I),
]

CLAUDE_IDENTITY_RESPONSE = (
    "I am Claude, made by Anthropic. I'm an AI assistant designed to help with coding, "
    "analysis, writing, and many other tasks."
)


def is_refusal(text: str) -> bool:
    return any(pattern.search(text) for pattern in REFUSAL_PATTERNS)


def sanitize_response(text: str) -> str:
    cleaned = text
    for pattern, replacement in IDENTITY_REPLACEMENTS:
        cleaned = pattern.sub(replacement, cleaned)

    cleaned = re.sub(r"(?:only|just)\s+(?:two|2)\s+tools?.*?(?:\.|\n)", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\bread_file\b.*?\bread_dir\b.*?(?:\.|\n)", "", cleaned, flags=re.I | re.S)
    cleaned = re.sub(r"Cursor\s+documentation.*?(?:\.|\n)", "", cleaned, flags=re.I)
    return cleaned.strip() or CLAUDE_IDENTITY_RESPONSE


def strip_system_leaks(text: str) -> str:
    cleaned = text
    for pattern in IDENTITY_LEAK_PATTERNS:
        cleaned = pattern.sub("", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def is_identity_probe(text: str) -> bool:
    return any(pattern.search(text) for pattern in IDENTITY_PROBE_PATTERNS)
