from django.core.management.base import BaseCommand
from inspections.models import Governorate, Wilayat

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


class Command(BaseCommand):
    help = 'Seed governorates and wilayats data for Oman'

    def handle(self, *args, **options):
        for gov_name, wilayats_list in OMAN_GOVERNORATES.items():
            gov, created = Governorate.objects.get_or_create(name=gov_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created governorate: {gov_name}'))
            
            for wilayat_name in wilayats_list:
                wilayat, created = Wilayat.objects.get_or_create(
                    name=wilayat_name,
                    governorate=gov
                )
                if created:
                    self.stdout.write(f'  Created wilayat: {wilayat_name}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded governorates and wilayats'))
