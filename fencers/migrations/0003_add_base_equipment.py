from decimal import Decimal
from django.db import migrations


def create_base_equipment(apps, schema_editor):
    EquipmentItem = apps.get_model('fencers', 'EquipmentItem')
    base_items = [
        {
            'name': 'Maska',
            'category': 'Ochranné vybavení',
            'description': 'Maska musí splňovat X-N a další ochranné parametry.',
            'approximate_price': Decimal('3500.00'),
        },
        {
            'name': 'Vesta',
            'category': 'Ochranné vybavení',
            'description': 'Standardní X-N vesta pro kordisty.',
            'approximate_price': Decimal('4200.00'),
        },
        {
            'name': 'Podvesta',
            'category': 'Ochranné vybavení',
            'description': 'Vnitřní ochrana paže a trupu, povinná na soutěžích.',
            'approximate_price': Decimal('1800.00'),
        },
        {
            'name': 'Rukavice',
            'category': 'Ochranné vybavení',
            'description': 'Rukavice s prodlouženou manžetou pro kord.',
            'approximate_price': Decimal('900.00'),
        },
        {
            'name': 'Kalhoty',
            'category': 'Oblečení',
            'description': 'Kalhoty pod kolena s vysokou odolností proti průrazu, standard X-N.',
            'approximate_price': Decimal('3600.00'),
        },
        {
            'name': 'Ponožky a boty',
            'category': 'Oblečení',
            'description': 'Vysoké podkolenky a šermířské boty s boční výztuží pro výpady.',
            'approximate_price': Decimal('3100.00'),
        },
        {
            'name': 'Kord',
            'category': 'Zbraně',
            'description': 'Vyvážený závodní kord s elektrickým hrotem.',
            'approximate_price': Decimal('4500.00'),
        },
        {
            'name': 'Šňůra',
            'category': 'Elektronika',
            'description': 'Třívodičový kabel spojující zbraň s aparátem.',
            'approximate_price': Decimal('800.00'),
        },
        {
            'name': 'Chránič hrudi',
            'category': 'Ochranné vybavení',
            'description': 'Plastový chránič hrudi, povinný pro ženy, volitelný pro muže.',
            'approximate_price': Decimal('1200.00'),
        },
    ]
    for item in base_items:
        defaults = item.copy()
        defaults.pop('name')
        EquipmentItem.objects.update_or_create(name=item['name'], defaults=defaults)


def remove_base_equipment(apps, schema_editor):
    EquipmentItem = apps.get_model('fencers', 'EquipmentItem')
    names = [
        'Maska',
        'Vesta',
        'Podvesta',
        'Rukavice',
        'Kalhoty',
        'Ponožky a boty',
        'Kord',
        'Šňůra',
        'Chránič hrudi',
    ]
    EquipmentItem.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('fencers', '0002_alter_circuitsong_options_and_more'),
    ]

    operations = [
        migrations.RunPython(create_base_equipment, remove_base_equipment),
    ]

