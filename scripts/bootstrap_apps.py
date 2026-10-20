"""Write correct AppConfig files for each project app (overwrites apps.py)."""
import pathlib

VERBOSE = {
    "core": "Core",
    "accounts": "Accounts",
    "school": "School",
    "academics": "Academics",
    "admissions": "Enquiries",
    "gallery": "Gallery",
    "dashboard": "Dashboard",
    "analytics": "Analytics",
    "seo": "SEO",
}

ROOT = pathlib.Path(__file__).resolve().parent.parent / "apps"

for name, verbose in VERBOSE.items():
    d = ROOT / name
    d.mkdir(parents=True, exist_ok=True)
    class_name = name.title() + "Config"
    if name == "seo":
        class_name = "SeoConfig"
    content = (
        "from django.apps import AppConfig\n\n\n"
        f"class {class_name}(AppConfig):\n"
        "    default_auto_field = 'django.db.models.BigAutoField'\n"
        f"    name = 'apps.{name}'\n"
        f"    label = '{name}'\n"
        f"    verbose_name = '{verbose}'\n"
    )
    (d / "apps.py").write_text(content, encoding="utf-8")
    (d / "migrations").mkdir(exist_ok=True)
    (d / "migrations" / "__init__.py").touch()

(ROOT / "__init__.py").touch()
print("apps.py files written")
