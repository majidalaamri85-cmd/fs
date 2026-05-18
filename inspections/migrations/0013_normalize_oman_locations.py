from django.db import migrations


OMAN_GOVERNORATES = {
    'مسقط': ['مسقط', 'مطرح', 'بوشر', 'السيب', 'العامرات', 'قريات'],
    'ظفار': ['صلالة', 'طاقة', 'مرباط', 'ثمريت', 'سدح', 'رخيوت', 'ضلكوت', 'مقشن', 'شليم وجزر الحلانيات', 'المزيونة'],
    'مسندم': ['خصب', 'بخا', 'دبا', 'مدحاء'],
    'البريمي': ['البريمي', 'محضة', 'السنينة'],
    'الداخلية': ['نزوى', 'بهلاء', 'منح', 'الحمراء', 'أدم', 'إزكي', 'سمائل', 'بدبد', 'الجبل الأخضر'],
    'شمال الباطنة': ['صحار', 'شناص', 'لوى', 'صحم', 'الخابورة', 'السويق'],
    'جنوب الباطنة': ['الرستاق', 'العوابي', 'نخل', 'وادي المعاول', 'بركاء', 'المصنعة'],
    'الظاهرة': ['عبري', 'ينقل', 'ضنك'],
    'الوسطى': ['هيما', 'محوت', 'الدقم', 'الجازر'],
    'شمال الشرقية': ['إبراء', 'المضيبي', 'بدية', 'القابل', 'وادي بني خالد', 'دماء والطائيين', 'سناو'],
    'جنوب الشرقية': ['صور', 'الكامل والوافي', 'جعلان بني بو حسن', 'جعلان بني بو علي', 'مصيرة'],
}

WILAYAT_ALIASES = {
    'لوا': 'لوى',
    'هيماء': 'هيما',
    'رستاق': 'الرستاق',
    'جعلان بني بوحسن': 'جعلان بني بو حسن',
    'جعلان بني بوعلي': 'جعلان بني بو علي',
}

GOVERNORATE_ALIASES = {
    'الباطنة': 'شمال الباطنة',
    'الشرقية': 'جنوب الشرقية',
}


def normalize_locations(apps, schema_editor):
    Governorate = apps.get_model('inspections', 'Governorate')
    Wilayat = apps.get_model('inspections', 'Wilayat')
    Evaluation = apps.get_model('inspections', 'Evaluation')

    governorates = {}
    wilayats = {}

    for gov_name, wilayat_names in OMAN_GOVERNORATES.items():
        governorate, _ = Governorate.objects.get_or_create(name=gov_name)
        governorates[gov_name] = governorate
        for wilayat_name in wilayat_names:
            wilayat, _ = Wilayat.objects.get_or_create(name=wilayat_name, governorate=governorate)
            wilayats[wilayat_name] = wilayat

    canonical_by_wilayat = {}
    for gov_name, wilayat_names in OMAN_GOVERNORATES.items():
        for wilayat_name in wilayat_names:
            canonical_by_wilayat[wilayat_name] = (governorates[gov_name], wilayats[wilayat_name])

    for old_name, canonical_name in WILAYAT_ALIASES.items():
        canonical_by_wilayat[old_name] = canonical_by_wilayat[canonical_name]

    for evaluation in Evaluation.objects.select_related('governorate', 'wilayat').all():
        if evaluation.wilayat:
            target = canonical_by_wilayat.get(evaluation.wilayat.name)
            if target:
                governorate, wilayat = target
                Evaluation.objects.filter(pk=evaluation.pk).update(governorate=governorate, wilayat=wilayat)
                continue

        if evaluation.governorate:
            target_gov_name = GOVERNORATE_ALIASES.get(evaluation.governorate.name, evaluation.governorate.name)
            target_governorate = governorates.get(target_gov_name)
            if target_governorate:
                Evaluation.objects.filter(pk=evaluation.pk).update(governorate=target_governorate)

    canonical_pairs = {
        (gov_name, wilayat_name)
        for gov_name, wilayat_names in OMAN_GOVERNORATES.items()
        for wilayat_name in wilayat_names
    }
    for wilayat in Wilayat.objects.select_related('governorate').all():
        if (wilayat.governorate.name, wilayat.name) not in canonical_pairs:
            if not Evaluation.objects.filter(wilayat=wilayat).exists():
                wilayat.delete()

    for governorate in Governorate.objects.all():
        if governorate.name not in OMAN_GOVERNORATES and not Evaluation.objects.filter(governorate=governorate).exists():
            governorate.delete()


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('inspections', '0012_fix_bidiya_governorate'),
    ]

    operations = [
        migrations.RunPython(normalize_locations, reverse_noop),
    ]
