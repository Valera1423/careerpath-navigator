"""Граф зависимостей навыков для react-flow."""
from __future__ import annotations

from app.services.skills import dependencies_for, detect_role_family


def build_graph(user_skills: list[str], missing: list[str], position: str) -> dict:
    family = detect_role_family(position)
    deps_map = dependencies_for(family)

    all_skills = set(user_skills) | set(missing)
    nodes = []
    edges = []

    for skill in all_skills:
        nodes.append(
            {
                "id": skill,
                "data": {
                    "label": skill.replace("_", " "),
                    "status": "done" if skill in user_skills else "missing",
                },
                "position": {"x": 0, "y": 0},
            }
        )

    for skill, deps in deps_map.items():
        if skill not in all_skills:
            continue
        for dep in deps:
            if dep in all_skills:
                edges.append(
                    {
                        "id": f"{dep}->{skill}",
                        "source": dep,
                        "target": skill,
                        "animated": skill in missing,
                    }
                )

    return {"nodes": nodes, "edges": edges}