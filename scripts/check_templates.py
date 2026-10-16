import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.template import engines  # noqa: E402

django_engine = engines["django"]
root = Path("templates")
errors = []
count = 0
for path in sorted(root.rglob("*.html")):
    rel = path.relative_to(root).as_posix()
    try:
        django_engine.get_template(rel)
    except Exception as exc:  # noqa: BLE001
        errors.append((rel, exc))
    count += 1

print(f"parsed={count} errors={len(errors)}")
for rel, exc in errors:
    print(f"FAIL {rel}: {type(exc).__name__}: {exc}")
sys.exit(1 if errors else 0)
