"""Сервис карьерного симулятора дня."""
from __future__ import annotations

import json
from pathlib import Path

from app.models import SimulatorSession

SCENARIOS_DIR = Path(__file__).parent.parent / "data" / "scenarios"
_scenarios_cache: dict[str, dict] = {}


def load_scenario(scenario_id: str) -> dict:
    if scenario_id in _scenarios_cache:
        return _scenarios_cache[scenario_id]

    path = SCENARIOS_DIR / f"{scenario_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Сценарий {scenario_id} не найден")

    data = json.loads(path.read_text(encoding="utf-8"))
    _scenarios_cache[scenario_id] = data
    return data


def list_scenarios() -> list[dict]:
    result = []
    for p in SCENARIOS_DIR.glob("*.json"):
        data = json.loads(p.read_text(encoding="utf-8"))
        result.append({
            "id": p.stem,
            "role": data["role"],
            "duration_minutes": data["duration_minutes"],
            "intro": data.get("intro", ""),
        })
    return result


def get_node(session: SimulatorSession) -> dict:
    scenario = load_scenario(session.scenario_id)
    node = scenario["nodes"][session.current_node]
    return {
        "node_id": session.current_node,
        "type": node["type"],
        "text": node["text"],
        "choices": [
            {"id": c["id"], "text": c["text"]}
            for c in node.get("choices", [])
        ],
        "outcome": node.get("outcome"),
        "summary": node.get("summary"),
    }


def _apply_effects(session: SimulatorSession, effects: dict) -> None:
    """Универсально применяет эффекты выбора к сессии.

    Поддерживает add_skill, add_skill_2, add_skill_3, ... и gap_skill.
    """
    for key, value in effects.items():
        if not isinstance(value, str):
            continue
        if key.startswith("add_skill"):
            session.skills_gained = [*session.skills_gained, value]
        elif key == "gap_skill":
            session.gaps_found = [*session.gaps_found, value]

    session.xp_earned += int(effects.get("xp", 0) or 0)


def apply_choice(session: SimulatorSession, choice_id: str) -> dict:
    scenario = load_scenario(session.scenario_id)
    node = scenario["nodes"][session.current_node]

    choice = next(
        (c for c in node.get("choices", []) if c["id"] == choice_id), None
    )
    if not choice:
        raise ValueError("Неверный выбор")

    effects = choice.get("effects", {}) or {}

    session.path_taken = [*session.path_taken, choice_id]
    _apply_effects(session, effects)

    session.current_node = choice["next"]
    next_node = scenario["nodes"][session.current_node]
    if next_node["type"] == "end":
        session.is_finished = True

    return {
        "feedback": choice.get("feedback", ""),
        "effects": effects,
        "next": get_node(session),
        "is_finished": session.is_finished,
    }