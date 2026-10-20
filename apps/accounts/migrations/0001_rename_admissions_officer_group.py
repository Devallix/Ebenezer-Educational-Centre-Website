"""Rename the "Admissions Officers" group to "Enquiries Officers".

The admission enquiry pipeline has been removed, so the role that used to look
after it now only handles website contact messages. Renaming the group keeps
existing user memberships (and their permissions) intact.
"""

from django.db import migrations

OLD_GROUP = "Admissions Officers"
NEW_GROUP = "Enquiries Officers"


def rename_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    old = Group.objects.filter(name=OLD_GROUP).first()
    if old is None:
        return
    new = Group.objects.filter(name=NEW_GROUP).first()
    if new is None:
        old.name = NEW_GROUP
        old.save(update_fields=["name"])
        return
    # The new group already exists: merge the memberships and drop the old one.
    for user in old.user_set.all():
        user.groups.add(new)
    old.delete()


def revert_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    old = Group.objects.filter(name=OLD_GROUP).first()
    if old is None:
        return
    new = Group.objects.filter(name=NEW_GROUP).first()
    if new is None:
        new = Group.objects.create(name=NEW_GROUP)
    for user in new.user_set.all():
        user.groups.add(old)
    new.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(rename_group, revert_group),
    ]
