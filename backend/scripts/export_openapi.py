"""Экспорт OpenAPI-спецификации FastAPI в JSON.

Использование:
    python -m scripts.export_openapi                    # → openapi.json
    python -m scripts.export_openapi /path/to/file.json # → указанный путь

Из Docker:
    docker compose exec backend python -m scripts.export_openapi /tmp/openapi.json
    docker compose cp backend:/tmp/openapi.json ./openapi.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from app.main import app


def main(out_path: str | Path = "openapi.json") -> None:
    spec = app.openapi()
    target = Path(out_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(spec, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"OpenAPI spec written to {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "openapi.json"
    main(path)