from django.db import migrations, models


def set_nav_defaults(apps, _schema_editor):
    ContentPage = apps.get_model("fencers", "ContentPage")
    wiki_meta = {
        "glossary": (0, "book-2"),
        "videos": (10, "video"),
        "rules": (20, "file-text"),
        "equipment-assembly": (30, "tool"),
        "historie-klubu": (40, "history"),
        "kronika": (50, "notebook"),
    }
    equip_meta = {
        "tools": (0, "tool"),
        "weapon-diagnosis": (10, "stethoscope"),
        "blade-assembly": (20, "sword"),
        "equipment-maintenance": (30, "brush"),
        "kde-nakoupit": (40, "shopping-cart"),
    }
    for page in ContentPage.objects.all():
        if page.section == "wiki" and page.slug in wiki_meta:
            order, icon = wiki_meta[page.slug]
            page.nav_order = order
            page.nav_icon = icon
            page.show_in_nav = True
            page.save(update_fields=["nav_order", "nav_icon", "show_in_nav"])
        elif page.section == "equipment" and page.slug in equip_meta:
            order, icon = equip_meta[page.slug]
            page.nav_order = order
            page.nav_icon = icon
            page.show_in_nav = True
            page.save(update_fields=["nav_order", "nav_icon", "show_in_nav"])

    ContentPage.objects.get_or_create(
        section="wiki",
        slug="historie-klubu",
        defaults={
            "title": "Historie klubu",
            "is_published": True,
            "show_in_nav": True,
            "nav_order": 40,
            "nav_icon": "history",
        },
    )
    ContentPage.objects.get_or_create(
        section="wiki",
        slug="kronika",
        defaults={
            "title": "Kronika",
            "is_published": True,
            "show_in_nav": True,
            "nav_order": 50,
            "nav_icon": "notebook",
        },
    )
    ContentPage.objects.get_or_create(
        section="equipment",
        slug="kde-nakoupit",
        defaults={
            "title": "Kde nakoupit",
            "is_published": True,
            "show_in_nav": True,
            "nav_order": 40,
            "nav_icon": "shopping-cart",
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("fencers", "0044_eventphoto_remote_image_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="contentpage",
            name="nav_icon",
            field=models.CharField(
                default="file-text",
                help_text='Bez prefixu "ti ti-", např. book-2, video, shopping-cart.',
                max_length=64,
                verbose_name="Ikona (Tabler)",
            ),
        ),
        migrations.AddField(
            model_name="contentpage",
            name="nav_order",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Nižší číslo = dříve v řádku dlaždic.",
                verbose_name="Pořadí dlaždic",
            ),
        ),
        migrations.AddField(
            model_name="contentpage",
            name="show_in_nav",
            field=models.BooleanField(
                default=True,
                help_text="Pokud je zapnuto, stránka se objeví jako dlaždice na Wiki nebo Výbava.",
                verbose_name="Zobrazit dlaždici",
            ),
        ),
        migrations.AlterModelOptions(
            name="contentpage",
            options={
                "ordering": ["section", "nav_order", "title"],
                "verbose_name": "Obsahová stránka",
                "verbose_name_plural": "Obsahové stránky",
            },
        ),
        migrations.RunPython(set_nav_defaults, migrations.RunPython.noop),
    ]
