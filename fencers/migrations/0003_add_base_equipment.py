from decimal import Decimal
from django.db import migrations


def create_base_equipment(apps, schema_editor):
    EquipmentItem = apps.get_model('fencers', 'EquipmentItem')
    base_items = [
        {
            'name': 'Maska na kord',
            'category': 'Ochranné vybavení',
            'description': 'Maska 1600N s průhledným bibem a odolnou mřížkou pro elektrický kord.',
            'approximate_price': Decimal('3500.00'),
        },
        {
            'name': 'Bunda na kord',
            'category': 'Ochranné vybavení',
            'description': '800N šermířská bunda s vyztuženou hrudní částí a průchodkou pro tělový kabel.',
            'approximate_price': Decimal('4200.00'),
        },
        {
            'name': 'Plastron',
            'category': 'Ochranné vybavení',
            'description': 'Vnitřní chránič paže a trupu pro praváky i leváky, povinný na soutěžích.',
            'approximate_price': Decimal('1800.00'),
        },
        {
            'name': 'Rukavice na kord',
            'category': 'Ochranné vybavení',
            'description': 'Rukavice s prodlouženou manžetou a protiskluzovou dlaní.',
            'approximate_price': Decimal('900.00'),
        },
        {
            'name': 'Kalhoty (breeches)',
            'category': 'Oblečení',
            'description': 'Kalhoty pod kolena s vysokou odolností proti průrazu, standard 800N.',
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
            'description': 'Vyvážený závodní kord s elektrickým hrotem a pistolovou rukojetí.',
            'approximate_price': Decimal('4500.00'),
        },
        {
            'name': 'Body cord',
            'category': 'Elektronika',
            'description': 'Třívodičový tělový kabel s rychloupínáním, kompatibilní s kordem.',
            'approximate_price': Decimal('800.00'),
        },
        {
            'name': 'Chránič hrudi',
            'category': 'Ochranné vybavení',
            'description': 'Plastový chránič hrudi, povinný pro ženy, doporučený pro muže.',
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
        'Maska na kord',
        'Bunda na kord',
        'Plastron',
        'Rukavice na kord',
        'Kalhoty (breeches)',
        'Ponožky a boty',
        'Kord',
        'Body cord',
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

