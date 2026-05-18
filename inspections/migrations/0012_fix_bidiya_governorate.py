from django.db import migrations


def fix_bidiya_governorate(apps, schema_editor):
    Governorate = apps.get_model('inspections', 'Governorate')
    Wilayat = apps.get_model('inspections', 'Wilayat')
    Evaluation = apps.get_model('inspections', 'Evaluation')

    north_sharqiyah = Governorate.objects.filter(name='شمال الشرقية').first()
    dakhiliyah = Governorate.objects.filter(name='الداخلية').first()
    if not north_sharqiyah or not dakhiliyah:
        return

    correct_bidiya, _ = Wilayat.objects.get_or_create(
        name='بدية',
        governorate=north_sharqiyah,
    )
    wrong_bidiya = Wilayat.objects.filter(name='بدية', governorate=dakhiliyah).first()
    if not wrong_bidiya:
        return

    Evaluation.objects.filter(wilayat=wrong_bidiya).update(
        wilayat=correct_bidiya,
        governorate=north_sharqiyah,
    )
    wrong_bidiya.delete()


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('inspections', '0011_statisticalrecord'),
    ]

    operations = [
        migrations.RunPython(fix_bidiya_governorate, reverse_noop),
    ]
