"""Point homepage slides that linked to /admission/ at the contact page.

The admission page has been removed, so any slide button that used to link
there now points to /contact/.
"""

from django.db import migrations

OLD_URL = "/admission/"
NEW_URL = "/contact/"


def update_slide_links(apps, schema_editor):
    HeroSlide = apps.get_model("school", "HeroSlide")
    HeroSlide.objects.filter(primary_button_url=OLD_URL).update(
        primary_button_url=NEW_URL
    )
    HeroSlide.objects.filter(secondary_button_url=OLD_URL).update(
        secondary_button_url=NEW_URL
    )


def revert_slide_links(apps, schema_editor):
    HeroSlide = apps.get_model("school", "HeroSlide")
    HeroSlide.objects.filter(primary_button_url=NEW_URL).update(
        primary_button_url=OLD_URL
    )
    HeroSlide.objects.filter(secondary_button_url=NEW_URL).update(
        secondary_button_url=OLD_URL
    )


class Migration(migrations.Migration):

    dependencies = [
        ("school", "0003_alter_pagehero_key"),
    ]

    operations = [
        migrations.RunPython(update_slide_links, revert_slide_links),
    ]
