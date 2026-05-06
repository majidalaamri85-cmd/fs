from django.core.management.base import BaseCommand
from inspections.models import Governorate, Wilayat

class Command(BaseCommand):
    help = 'Seed governorates and wilayats data for Oman'

    def handle(self, *args, **options):
        # Oman governorates and wilayats data
        data = {
            'مسقط': ['مسقط', 'بوشر', 'السيب', 'مطرح', 'قريات'],
            'ظفار': ['صلالة', 'ثمريت', 'طاقة', 'رخيوت'],
            'مسندم': ['خصب', 'دبا', 'مدحاء'],
            'الشرقية': ['صور', 'قلهات', 'جعلان بني بوعلي', 'جعلان بني بوحسن', 'البريمي'],
            'الداخلية': ['نزوى', 'إزكي', 'سمائل', 'بدية', 'الحمراء'],
            'الباطنة': ['صحار', 'تقريت', 'شناص', 'لوا', 'الخابورة'],
            'الوسطى': ['الدقم', 'هيماء', 'محضة'],
            'شمال الباطنة': ['صحار', 'عبري', 'ينقل', 'البريمي'],
            'شمال الشرقية': ['إبراء', 'رأس الخيمة', 'دعا', 'قمصير'],
            'جنوب الشرقية': ['صور', 'ضنك', 'رستاق'],
        }

        for gov_name, wilayats_list in data.items():
            # Create governorate
            gov, created = Governorate.objects.get_or_create(name=gov_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created governorate: {gov_name}'))
            
            # Create wilayats
            for wilayat_name in wilayats_list:
                wilayat, created = Wilayat.objects.get_or_create(
                    name=wilayat_name,
                    governorate=gov
                )
                if created:
                    self.stdout.write(f'  Created wilayat: {wilayat_name}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded governorates and wilayats'))
