"""Загрузка навыков и ролей из YAML. Отделено от кода для лёгкого пополнения."""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml

DATA_DIR = Path(__file__).parent.parent / "data"
_WORD_RE = re.compile(r"[a-zA-Zа-яА-Я0-9#+/]+", re.IGNORECASE)


@lru_cache(maxsize=1)
def _load_skills() -> dict[str, tuple[str, ...]]:
    raw = yaml.safe_load((DATA_DIR / "skills.yaml").read_text(encoding="utf-8"))
    return {k: tuple(v) for k, v in raw.items()}


@lru_cache(maxsize=1)
def _load_roles() -> dict[str, dict]:
    return yaml.safe_load((DATA_DIR / "roles.yaml").read_text(encoding="utf-8"))


def normalize_skill(raw: str) -> str:
    return raw.strip().lower().replace("ё", "е")


def detect_role_family(position: str) -> str:
    text = normalize_skill(position)
    roles = _load_roles()
    for family, cfg in roles.items():
        if family == "generic":
            continue
        if any(kw in text for kw in cfg.get("keywords", [])):
            return family
    return "generic"


def core_skills_for(position: str) -> list[str]:
    roles = _load_roles()
    family = detect_role_family(position)
    return list(roles.get(family, roles["generic"]).get("core", []))


def dependencies_for(family: str) -> dict[str, list[str]]:
    return dict(_load_roles().get(family, {}).get("dependencies", {}))


def extract_skills(text: str) -> set[str]:
    if not text:
        return set()
    haystack = " " + normalize_skill(text) + " "
    found: set[str] = set()
    for skill, patterns in _load_skills().items():
        for pattern in patterns:
            if pattern in haystack:
                found.add(skill)
                break
    return found


def all_skills() -> list[str]:
    return sorted(_load_skills().keys())