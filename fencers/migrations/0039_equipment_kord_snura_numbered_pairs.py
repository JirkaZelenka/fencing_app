# Rename Kord / Kord (záložní) -> Kord 1 / Kord 2; Šňůra -> Šňůra 1 + add Šňůra 2

from django.db import migrations


def _copy_equipment_fields(source):
    data = {
        'category': source.category,
        'description': source.description or '',
        'approximate_price': source.approximate_price,
        'purchase_link': source.purchase_link or '',
    }
    for field in (
        'shop_5mfencing_link',
        'shop_rubyfencing_link',
        'shop_5mfencing_price',
        'shop_rubyfencing_price',
    ):
        if hasattr(source, field):
            val = getattr(source, field)
            data[field] = val if val is not None else ('' if 'link' in field else None)
    return data


def forwards(apps, schema_editor):
    EquipmentItem = apps.get_model('fencers', 'EquipmentItem')

    if EquipmentItem.objects.filter(name='Kord').exists():
        EquipmentItem.objects.filter(name='Kord').update(name='Kord 1')
    if EquipmentItem.objects.filter(name='Kord (záložní)').exists():
        EquipmentItem.objects.filter(name='Kord (záložní)').update(name='Kord 2')
    elif not EquipmentItem.objects.filter(name='Kord 2').exists():
        k1 = EquipmentItem.objects.filter(name='Kord 1').first()
        if k1:
            EquipmentItem.objects.get_or_create(
                name='Kord 2',
                defaults=_copy_equipment_fields(k1),
            )

    cord = EquipmentItem.objects.filter(name='Šňůra').first()
    if cord:
        EquipmentItem.objects.get_or_create(
            name='Šňůra 2',
            defaults=_copy_equipment_fields(cord),
        )
        cord.name = 'Šňůra 1'
        cord.save()
    else:
        s1 = EquipmentItem.objects.filter(name='Šňůra 1').first()
        if s1 and not EquipmentItem.objects.filter(name='Šňůra 2').exists():
            EquipmentItem.objects.get_or_create(
                name='Šňůra 2',
                defaults=_copy_equipment_fields(s1),
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fencers', '0038_alter_event_event_type_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]
