from django.db import models

class Governorate(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='المحافظة')
    
    class Meta:
        verbose_name = 'محافظة'
        verbose_name_plural = 'المحافظات'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Wilayat(models.Model):
    name = models.CharField(max_length=255, verbose_name='الولاية')
    governorate = models.ForeignKey(Governorate, on_delete=models.CASCADE, related_name='wilayats', verbose_name='المحافظة')
    
    class Meta:
        verbose_name = 'ولاية'
        verbose_name_plural = 'الولايات'
        ordering = ['governorate', 'name']
        unique_together = ('name', 'governorate')
    
    def __str__(self):
        return f"{self.name} - {self.governorate.name}"


class Section(models.Model):
    title = models.CharField(max_length=255, verbose_name='القسم')
    order = models.PositiveIntegerField(default=1, verbose_name='الترتيب')

    class Meta:
        ordering = ['order']
        verbose_name = 'قسم'
        verbose_name_plural = 'الأقسام'

    def __str__(self):
        return self.title


class Item(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='items', verbose_name='القسم')
    number = models.PositiveIntegerField(verbose_name='رقم البند')
    text = models.TextField(verbose_name='وصف البند')
    corrective_action = models.TextField(blank=True, verbose_name='الإجراء التصحيحي المقترح')
    priority = models.CharField(max_length=50, blank=True, verbose_name='الأولوية')

    class Meta:
        ordering = ['number']
        verbose_name = 'بند'
        verbose_name_plural = 'البنود'

    def __str__(self):
        return f'{self.number} - {self.text[:60]}'


class Evaluation(models.Model):
    facility_name = models.CharField(max_length=255, verbose_name='اسم المنشأة')
    activity_type = models.CharField(max_length=255, blank=True, verbose_name='نوع النشاط')
    license_number = models.CharField(max_length=100, blank=True, verbose_name='رقم الرخصة')
    cr_number = models.CharField(max_length=100, blank=True, verbose_name='رقم السجل التجاري')
    governorate = models.ForeignKey(Governorate, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='المحافظة')
    wilayat = models.ForeignKey(Wilayat, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='الولاية')
    contact_name = models.CharField(max_length=255, blank=True, verbose_name='اسم المسؤول')
    contact_phone = models.CharField(max_length=50, blank=True, verbose_name='رقم التواصل')
    visit_date = models.DateField(verbose_name='تاريخ الزيارة')
    evaluation_team = models.TextField(blank=True, verbose_name='فريق التقييم')
    shift_count = models.CharField(max_length=50, blank=True, verbose_name='عدد الورديات')
    workers_per_shift = models.CharField(max_length=50, blank=True, verbose_name='عدد العاملين في الوردية')
    total_factory_workers = models.CharField(max_length=50, blank=True, verbose_name='مجموع عدد العاملين المصنع')
    supervisors_per_shift = models.CharField(max_length=50, blank=True, verbose_name='عدد المشرفين في الوردية')
    total_supervisors = models.CharField(max_length=50, blank=True, verbose_name='مجموع عدد المشرفين')
    product_types = models.TextField(blank=True, verbose_name='أنواع المنتجات')
    distribution_scope = models.CharField(max_length=255, blank=True, verbose_name='التوزيع محلي/تصدير')
    actual_daily_production_rate = models.CharField(max_length=255, blank=True, verbose_name='معدل الإنتاج اليومي الفعلي')
    permitted_daily_production_rate = models.CharField(max_length=255, blank=True, verbose_name='معدل الإنتاج اليومي المسموح')
    water_source = models.CharField(max_length=255, blank=True, verbose_name='مصدر الماء المستخدم')
    final_product_storage_area = models.CharField(max_length=255, blank=True, verbose_name='إجمالي مساحة مخزن المنتج النهائي')
    haccp_manual = models.TextField(blank=True, verbose_name='دليل الهاسب للشركة')
    iso_22000_certificate = models.TextField(blank=True, verbose_name='شهادة آيزو 22000')
    haccp_certificate = models.TextField(blank=True, verbose_name='شهادة الهاسب')
    other_quality_certificate = models.TextField(blank=True, verbose_name='شهادات أخرى')
    haccp_documents = models.TextField(blank=True, verbose_name='مستندات الهاسب')
    score = models.FloatField(default=0, verbose_name='النتيجة')
    classification = models.CharField(max_length=255, blank=True, verbose_name='الوضع العام للمنشأة')
    is_draft = models.BooleanField(default=True, verbose_name='مسودة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'تقييم'
        verbose_name_plural = 'التقييمات'

    def __str__(self):
        return self.facility_name


class StatisticalRecord(models.Model):
    source_sheet = models.CharField(max_length=255, verbose_name='ورقة المصدر')
    source_row = models.PositiveIntegerField(verbose_name='رقم الصف')
    category = models.CharField(max_length=255, blank=True, verbose_name='نوع البيان')
    facility_name = models.CharField(max_length=255, blank=True, db_index=True, verbose_name='اسم المنشأة')
    activity_type = models.CharField(max_length=255, blank=True, verbose_name='نوع النشاط')
    activity_category = models.CharField(max_length=255, blank=True, verbose_name='فئة النشاط')
    governorate = models.CharField(max_length=255, blank=True, verbose_name='المحافظة')
    visit_date = models.DateField(null=True, blank=True, db_index=True, verbose_name='تاريخ الزيارة')
    action_taken = models.TextField(blank=True, verbose_name='الإجراء المتخذ')
    contact_info = models.TextField(blank=True, verbose_name='بيانات التواصل')
    quality_systems = models.TextField(blank=True, verbose_name='نظم سلامة الغذاء')
    report = models.ForeignKey(
        Evaluation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='statistical_records',
        verbose_name='التقرير المرتبط',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإدخال')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        ordering = ['-visit_date', 'facility_name']
        unique_together = ('source_sheet', 'source_row')
        verbose_name = 'سجل إحصائي'
        verbose_name_plural = 'السجلات الإحصائية'

    def __str__(self):
        return self.facility_name or f'{self.source_sheet} #{self.source_row}'


class Response(models.Model):
    STATUS_CHOICES = [
        ('compliant', 'مستوفي'),
        ('non_compliant', 'غير مستوفي'),
        ('na', 'لا ينطبق'),
    ]

    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='responses')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='compliant')
    notes = models.TextField(blank=True)
    corrective_action = models.TextField(blank=True)
    correction_duration = models.CharField(max_length=255, blank=True, verbose_name='مدة التصحيح')

    class Meta:
        unique_together = ('evaluation', 'item')


class ResponseImage(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='evaluation_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
