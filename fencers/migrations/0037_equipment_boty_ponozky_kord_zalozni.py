# Generated manually for equipment loadout / catalog changes

from decimal import Decimal

from django.db import migrations


def split_footwear_and_add_spare_kord(apps, schema_editor):
    EquipmentItem = apps.get_model('fencers', 'EquipmentItem')
    UserEquipment = apps.get_model('fencers', 'UserEquipment')

    old = EquipmentItem.objects.filter(name='Ponožky a boty').first()
    if old:
        common = {
            'category': old.category,
            'purchase_link': old.purchase_link or '',
        }
        for field in (
            'shop_5mfencing_link',
            'shop_rubyfencing_link',
            'shop_5mfencing_price',
            'shop_rubyfencing_price',
        ):
            if hasattr(old, field):
                common[field] = getattr(old, field) or ('' if 'link' in field else None)

        total = old.approximate_price
        if total is not None:
            boty_price = (total * Decimal('2500') / Decimal('3100')).quantize(Decimal('0.01'))
            pon_price = (total * Decimal('600') / Decimal('3100')).quantize(Decimal('0.01'))
        else:
            boty_price = Decimal('2500.00')
            pon_price = Decimal('600.00')

        boty, _ = EquipmentItem.objects.update_or_create(
            name='Boty',
            defaults={
                **common,
                'description': 'Šermířské boty s boční výztuží pro výpady.',
                'approximate_price': boty_price,
            },
        )
        ponožky, _ = EquipmentItem.objects.update_or_create(
            name='Ponožky',
            defaults={
                **common,
                'description': 'Vysoké podkolenky pro šerm.',
                'approximate_price': pon_price,
            },
        )

        for ue in UserEquipment.objects.filter(equipment=old):
            UserEquipment.objects.update_or_create(
                fencer_id=ue.fencer_id,
                equipment_id=boty.id,
                defaults={
                    'is_owned': ue.is_owned,
                    'purchase_date': ue.purchase_date,
                },
            )
            UserEquipment.objects.update_or_create(
                fencer_id=ue.fencer_id,
                equipment_id=ponožky.id,
                defaults={
                    'is_owned': ue.is_owned,
                    'purchase_date': ue.purchase_date,
                },
            )

        UserEquipment.objects.filter(equipment=old).delete()
        old.delete()

    kord = EquipmentItem.objects.filter(name='Kord').first()
    spare_defaults = {
        'category': 'Zbraně',
        'description': 'Záložní nebo druhý kord pro turnaj a trénink.',
        'approximate_price': Decimal('4500.00'),
        'purchase_link': '',
    }
    if kord:
        spare_defaults['category'] = kord.category
        spare_defaults['purchase_link'] = kord.purchase_link or ''
        for field in (
            'shop_5mfencing_link',
            'shop_rubyfencing_link',
            'shop_5mfencing_price',
            'shop_rubyfencing_price',
        ):
            if hasattr(kord, field):
                spare_defaults[field] = getattr(kord, field) or ('' if 'link' in field else None)
        if kord.approximate_price is not None:
            spare_defaults['approximate_price'] = kord.approximate_price

    EquipmentItem.objects.get_or_create(
        name='Kord (záložní)',
        defaults=spare_defaults,
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fencers', '0036_eventparticipation_is_hall_of_fame'),
    ]

    operations = [
        migrations.RunPython(split_footwear_and_add_spare_kord, noop_reverse),
    ]
