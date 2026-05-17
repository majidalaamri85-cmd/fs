from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.db.models import Avg, Q
from django.db.utils import DatabaseError, OperationalError, ProgrammingError
from .models import Governorate, Wilayat, Section, Item, Evaluation, Response, ResponseImage
from .activity_options import ACTIVITY_OPTIONS
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Inches, Mm, Pt, RGBColor
from io import BytesIO
from pathlib import Path
import json
from datetime import date

EVALUATION_TEAM_OPTIONS = [
    'م. سالم الحارثي (مدير دائرة تطوير نظم سلامة الغذاء)',
    'م. عامر الحبسي (المدير المساعد لدائرة تطوير نظم سلامة الغذاء)',
    'م. ماجد العامري (رئيس قسم نظم سلامة الغذاء)',
    'م. عياض المعولي (رئيس قسم تطبيق نظم سلامة الغذاء)',
    'م. متعب المعمري (رئيس قسم تأهيل المنشآت الغذائية)',
    'د. يوسف أحمد محمد (طبيب بيطري)',
    'م. أحمد المريكي (مفتش صحي)',
]

HACCP_REQUIREMENTS = [
    'سجل استقبال ومخزن المواد الاولية (غذائية)',
    'سجل استقبال ومخزن المواد الاولية (التغليف)',
    'سجل مراقب الجودة (المراقبة اليومية)',
    'سجل مصائد القوارض والحشرات',
    'سجل مراقبة (CCP)',
    'سجل تتبع الإجراءات التصحيحية',
    'سجل تتبع المنتج',
    'سجل التخزين',
    'سجل الارسالية',
    'سجل النظافة',
    'سجل العمال',
    'سجل التدريب',
    'سجل فحص تحليل المختبر',
    'سجلات أخرى',
]


def parse_haccp_documents(value):
    if not value:
        return {}
    try:
        data = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def build_haccp_documents_from_request(request):
    documents = {}
    for index, requirement in enumerate(HACCP_REQUIREMENTS):
        documents[str(index)] = {
            'requirement': requirement,
            'exists': request.POST.get(f'haccp_exists_{index}', ''),
            'notes': request.POST.get(f'haccp_notes_{index}', ''),
        }
    return json.dumps(documents, ensure_ascii=False)


def build_haccp_rows(evaluation):
    documents = parse_haccp_documents(evaluation.haccp_documents if evaluation else '')
    rows = []
    for index, requirement in enumerate(HACCP_REQUIREMENTS):
        row = documents.get(str(index), {})
        rows.append({
            'index': index,
            'requirement': row.get('requirement') or requirement,
            'exists': row.get('exists', ''),
            'notes': row.get('notes', ''),
        })
    return rows


def get_wilayats_by_governorate(request):
    """API endpoint to get wilayats for a selected governorate"""
    gov_id = request.GET.get('governorate_id')
    if not gov_id:
        return JsonResponse({'wilayats': []})
    
    wilayats = Wilayat.objects.filter(governorate_id=gov_id).values('id', 'name')
    return JsonResponse({'wilayats': list(wilayats)})


def get_governorates(request):
    """API endpoint to get all governorates"""
    governorates = Governorate.objects.values('id', 'name')
    return JsonResponse({'governorates': list(governorates)})


def classify_score(score):
    if score >= 86:
        return 'ممتاز، مستوفي للحصول على شهادة ضبط الجودة'
    if score >= 70:
        return 'جيد، مستوفي للحصول على شهادة ضبط الجودة مع وجود فرص للتحسين'
    if score >= 41:
        return 'مقبول، يحتاج تأهيل ومزيد من التحسين'
    return 'ضعيف، إيقاف الإنتاج'


def calculate_score(evaluation):
    # HACCP documents are a checklist only; they are intentionally excluded from scoring.
    responses = evaluation.responses.all()
    total = responses.exclude(status='na').count()
    compliant = responses.filter(status='compliant').count()

    score = round((compliant / total) * 100, 2) if total else 0

    evaluation.score = score
    evaluation.classification = classify_score(score)
    evaluation.save()


def parse_iso_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def parse_float(value):
    if value in (None, ''):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def apply_evaluation_filters(queryset, filters):
    query = filters.get('q', '').strip()
    license_number = filters.get('license_number', '').strip()
    cr_number = filters.get('cr_number', '').strip()
    governorate_id = filters.get('governorate', '').strip()
    classification = filters.get('classification', '').strip()
    status = filters.get('status', '').strip()
    date_from = parse_iso_date(filters.get('date_from', '').strip())
    date_to = parse_iso_date(filters.get('date_to', '').strip())
    min_score = parse_float(filters.get('min_score', '').strip())
    max_score = parse_float(filters.get('max_score', '').strip())

    if query:
        queryset = queryset.filter(
            Q(facility_name__icontains=query)
            | Q(contact_name__icontains=query)
            | Q(license_number__icontains=query)
            | Q(cr_number__icontains=query)
        )

    if license_number:
        queryset = queryset.filter(license_number__icontains=license_number)

    if cr_number:
        queryset = queryset.filter(cr_number__icontains=cr_number)

    if governorate_id.isdigit():
        queryset = queryset.filter(governorate_id=int(governorate_id))

    if classification:
        queryset = queryset.filter(classification__icontains=classification)

    if status == 'draft':
        queryset = queryset.filter(is_draft=True)
    elif status == 'final':
        queryset = queryset.filter(is_draft=False)

    if date_from:
        queryset = queryset.filter(visit_date__gte=date_from)

    if date_to:
        queryset = queryset.filter(visit_date__lte=date_to)

    if min_score is not None:
        queryset = queryset.filter(score__gte=min_score)

    if max_score is not None:
        queryset = queryset.filter(score__lte=max_score)

    return queryset


def get_evaluation_summary(queryset):
    total = queryset.count()
    avg_score = queryset.aggregate(avg=Avg('score')).get('avg') or 0
    return {
        'total': total,
        'avg_score': round(avg_score, 1),
        'excellent': queryset.filter(score__gte=86).count(),
        'needs_attention': queryset.filter(score__lt=70).count(),
    }


def resolve_location(gov_id, wilayat_id):
    governorate = Governorate.objects.filter(id=gov_id).first() if gov_id else None
    wilayat = Wilayat.objects.filter(id=wilayat_id).first() if wilayat_id else None

    if wilayat and governorate and wilayat.governorate_id != governorate.id:
        wilayat = None
    if wilayat and not governorate:
        governorate = wilayat.governorate

    return governorate, wilayat


def evaluation_list(request):
    filters = {
        'q': request.GET.get('q', '').strip(),
        'license_number': request.GET.get('license_number', '').strip(),
        'cr_number': request.GET.get('cr_number', '').strip(),
        'governorate': request.GET.get('governorate', '').strip(),
        'classification': request.GET.get('classification', '').strip(),
        'status': request.GET.get('status', '').strip(),
        'date_from': request.GET.get('date_from', '').strip(),
        'date_to': request.GET.get('date_to', '').strip(),
        'min_score': request.GET.get('min_score', '').strip(),
        'max_score': request.GET.get('max_score', '').strip(),
    }

    error_message = ''
    try:
        evaluations = apply_evaluation_filters(Evaluation.objects.all(), filters)
        results_count = evaluations.count()
        summary = get_evaluation_summary(evaluations)
        governorates = Governorate.objects.all()
    except (OperationalError, ProgrammingError, DatabaseError):
        evaluations = Evaluation.objects.none()
        results_count = 0
        summary = {'total': 0, 'avg_score': 0, 'excellent': 0, 'needs_attention': 0}
        governorates = Governorate.objects.none()
        error_message = 'تعذر استجلاب التقارير من قاعدة البيانات. تأكد من اتصال DATABASE_URL وتطبيق migrations المطلوبة.'

    return render(request, 'inspections/evaluation_list.html', {
        'evaluations': evaluations,
        'filters': filters,
        'results_count': results_count,
        'summary': summary,
        'governorates': governorates,
        'db_error_message': error_message,
    })


def get_reports(request):
    filters = {
        'q': request.GET.get('q', '').strip(),
        'license_number': request.GET.get('license_number', '').strip(),
        'cr_number': request.GET.get('cr_number', '').strip(),
        'governorate': request.GET.get('governorate', '').strip(),
        'classification': request.GET.get('classification', '').strip(),
        'status': request.GET.get('status', '').strip(),
        'date_from': request.GET.get('date_from', '').strip(),
        'date_to': request.GET.get('date_to', '').strip(),
        'min_score': request.GET.get('min_score', '').strip(),
        'max_score': request.GET.get('max_score', '').strip(),
    }

    try:
        evaluations = apply_evaluation_filters(Evaluation.objects.all(), filters)
    except (OperationalError, ProgrammingError, DatabaseError):
        return JsonResponse({
            'reports': [],
            'count': 0,
            'error': 'Database schema/connection is not ready. Run migrations for the connected database.',
        }, status=503)

    data = [
        {
            'id': evaluation.pk,
            'facility_name': evaluation.facility_name,
            'license_number': evaluation.license_number,
            'cr_number': evaluation.cr_number,
            'visit_date': evaluation.visit_date,
            'score': evaluation.score,
            'classification': evaluation.classification,
            'is_draft': evaluation.is_draft,
        }
        for evaluation in evaluations
    ]
    return JsonResponse({'reports': data, 'count': len(data)})


def save_evaluation_from_request(request, evaluation=None):
    sections = Section.objects.prefetch_related('items').all()
    extra_fields = [
        'shift_count',
        'workers_per_shift',
        'total_factory_workers',
        'supervisors_per_shift',
        'total_supervisors',
        'product_types',
        'distribution_scope',
        'actual_daily_production_rate',
        'permitted_daily_production_rate',
        'water_source',
        'final_product_storage_area',
        'haccp_manual',
        'iso_22000_certificate',
        'haccp_certificate',
        'other_quality_certificate',
    ]
    
    # Resolve location safely even if posted IDs are invalid.
    gov_id = request.POST.get('governorate')
    wilayat_id = request.POST.get('wilayat')
    governorate, wilayat = resolve_location(gov_id, wilayat_id)

    if evaluation is None:
        evaluation = Evaluation.objects.create(
            facility_name=request.POST.get('facility_name', ''),
            activity_type=request.POST.get('activity_type', ''),
            license_number=request.POST.get('license_number', ''),
            cr_number=request.POST.get('cr_number', ''),
            governorate=governorate,
            wilayat=wilayat,
            contact_name=request.POST.get('contact_name', ''),
            contact_phone=request.POST.get('contact_phone', ''),
            visit_date=request.POST.get('visit_date'),
            evaluation_team=request.POST.get('evaluation_team', ''),
            haccp_documents=build_haccp_documents_from_request(request),
            is_draft=False,
            **{field: request.POST.get(field, '') for field in extra_fields},
        )
    else:
        evaluation.facility_name = request.POST.get('facility_name', '')
        evaluation.activity_type = request.POST.get('activity_type', '')
        evaluation.license_number = request.POST.get('license_number', '')
        evaluation.cr_number = request.POST.get('cr_number', '')
        evaluation.governorate = governorate
        evaluation.wilayat = wilayat
        evaluation.contact_name = request.POST.get('contact_name', '')
        evaluation.contact_phone = request.POST.get('contact_phone', '')
        evaluation.visit_date = request.POST.get('visit_date')
        evaluation.evaluation_team = request.POST.get('evaluation_team', '')
        evaluation.haccp_documents = build_haccp_documents_from_request(request)
        evaluation.is_draft = False
        for field in extra_fields:
            setattr(evaluation, field, request.POST.get(field, ''))
        evaluation.save()

    for section in sections:
        for item in section.items.all():
            status = request.POST.get(f'status_{item.id}', '').strip()

            if not status:
                Response.objects.filter(evaluation=evaluation, item=item).delete()
                continue

            response, created = Response.objects.update_or_create(
                evaluation=evaluation,
                item=item,
                defaults={
                    'status': status,
                    'notes': request.POST.get(f'notes_{item.id}', ''),
                    'corrective_action': request.POST.get(f'corrective_{item.id}', ''),
                    'correction_duration': request.POST.get(f'duration_{item.id}', ''),
                }
            )

            for image in request.FILES.getlist(f'images_{item.id}'):
                ResponseImage.objects.create(response=response, image=image)

    calculate_score(evaluation)
    return evaluation


def evaluation_form(request):
    db_error_message = ''
    try:
        # Evaluate querysets eagerly so DB schema errors are caught here.
        sections = list(Section.objects.prefetch_related('items').all())
        governorates = list(Governorate.objects.all())
    except (OperationalError, ProgrammingError, DatabaseError):
        sections = []
        governorates = []
        db_error_message = 'تعذر تحميل أقسام التقييم من قاعدة البيانات. تأكد من تطبيق migrations وتهيئة البيانات.'
    
    if request.method == 'POST':
        evaluation = save_evaluation_from_request(request)
        messages.success(request, 'تم حفظ التقييم وحساب النتيجة بنجاح.')
        return redirect('report_detail', evaluation.pk)

    return render(request, 'inspections/evaluation_form.html', {
        'sections': sections,
        'evaluation': None,
        'responses_map': {},
        'governorates': governorates,
        'wilayats': Wilayat.objects.none(),
        'activity_options': ACTIVITY_OPTIONS,
        'evaluation_team_options': EVALUATION_TEAM_OPTIONS,
        'haccp_rows': build_haccp_rows(None),
        'today': timezone.localdate(),
        'db_error_message': db_error_message,
    })


def evaluation_edit(request, pk):
    evaluation = get_object_or_404(Evaluation, pk=pk)
    db_error_message = ''
    try:
        # Evaluate querysets eagerly so DB schema errors are caught here.
        sections = list(Section.objects.prefetch_related('items').all())
        governorates = list(Governorate.objects.all())
        wilayats = list(evaluation.governorate.wilayats.all()) if evaluation.governorate else []
        responses_map = {r.item_id: r for r in evaluation.responses.all()}
    except (OperationalError, ProgrammingError, DatabaseError):
        sections = []
        governorates = []
        wilayats = []
        responses_map = {}
        db_error_message = 'تعذر تحميل بيانات التقييم من قاعدة البيانات. تأكد من تطبيق migrations وتهيئة البيانات.'

    if request.method == 'POST':
        evaluation = save_evaluation_from_request(request, evaluation)
        messages.success(request, 'تم تعديل التقييم بنجاح.')
        return redirect('report_detail', evaluation.pk)

    return render(request, 'inspections/evaluation_form.html', {
        'sections': sections,
        'evaluation': evaluation,
        'responses_map': responses_map,
        'governorates': governorates,
        'wilayats': wilayats,
        'activity_options': ACTIVITY_OPTIONS,
        'evaluation_team_options': EVALUATION_TEAM_OPTIONS,
        'haccp_rows': build_haccp_rows(evaluation),
        'db_error_message': db_error_message,
    })


def report_detail(request, pk):
    evaluation = get_object_or_404(Evaluation, pk=pk)
    responses = evaluation.responses.select_related('item', 'item__section').prefetch_related('images').all()
    return render(request, 'inspections/report_detail.html', {
        'evaluation': evaluation,
        'responses': responses,
        'haccp_rows': build_haccp_rows(evaluation),
    })


def evaluation_delete(request, pk):
    evaluation = get_object_or_404(Evaluation, pk=pk)
    if request.method == 'POST':
        evaluation.delete()
        messages.success(request, 'تم حذف التقرير بنجاح.')
        return redirect('evaluation_list')
    return render(request, 'inspections/confirm_delete.html', {'evaluation': evaluation})


def shade_cell(cell, fill):
    cell._tc.get_or_add_tcPr().append(parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), fill)))


def set_table_rtl(table):
    table._tbl.tblPr.append(parse_xml(r'<w:bidiVisual {} />'.format(nsdecls('w'))))


def set_cell_text(cell, text, bold=False, color=None):
    cell.text = ''
    paragraph = cell.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run(str(text or ''))
    run.bold = bold
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


def style_table_header(row, fill='0F6B4B'):
    for cell in row.cells:
        shade_cell(cell, fill)
        set_cell_text(cell, cell.text, bold=True, color='FFFFFF')


def add_section_heading(doc, title, fill='0F6B4B'):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.rows[0].cells[0]
    shade_cell(cell, fill)
    set_cell_text(cell, title, bold=True, color='FFFFFF')
    doc.add_paragraph()


def get_report_header_path():
    base_dir = Path(settings.BASE_DIR)
    candidates = [
        base_dir / 'static' / 'images' / 'report_header.png',
        base_dir / 'inspections' / 'static' / 'inspections' / 'report_header.png',
        base_dir.parent.parent / 'final' / 'static' / 'images' / 'report_header.png',
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def add_report_header(doc):
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.left_margin = Mm(10)
    section.right_margin = Mm(10)
    section.top_margin = Mm(8)
    section.bottom_margin = Mm(10)

    header_path = get_report_header_path()
    if not header_path:
        return

    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(6)
    paragraph.add_run().add_picture(str(header_path), width=section.page_width)


def get_report_signature_path():
    base_dir = Path(settings.BASE_DIR)
    candidates = [
        base_dir / 'static' / 'images' / 'report_signature.png',
        base_dir / 'inspections' / 'static' / 'inspections' / 'report_signature.png',
        base_dir.parent.parent / 'final' / 'static' / 'images' / 'report_signature.png',
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def add_report_signature(doc):
    signature_path = get_report_signature_path()
    if not signature_path:
        return

    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragraph.paragraph_format.space_before = Pt(18)
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.add_run().add_picture(str(signature_path), width=Inches(4.6))


def export_word(request, pk):
    evaluation = get_object_or_404(Evaluation, pk=pk)
    non_compliant_responses = (
        evaluation.responses
        .filter(status='non_compliant')
        .select_related('item', 'item__section')
        .prefetch_related('images')
        .order_by('item__section__order', 'item__number')
    )
    doc = Document()
    add_report_header(doc)

    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    title = doc.add_heading('تقرير تقييم منشأة غذائية', level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.color.rgb = RGBColor.from_string('0F6B4B')

    score_fill = '138A4C' if evaluation.score >= 86 else '2F855A' if evaluation.score >= 70 else 'D9A441' if evaluation.score >= 41 else 'B42318'
    score_table = doc.add_table(rows=1, cols=2)
    score_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    score_table.style = 'Table Grid'
    score_cells = score_table.rows[0].cells
    shade_cell(score_cells[0], score_fill)
    shade_cell(score_cells[1], score_fill)
    set_cell_text(score_cells[0], f'{evaluation.score}%', bold=True, color='FFFFFF')
    set_cell_text(score_cells[1], evaluation.classification, bold=True, color='FFFFFF')

    add_section_heading(doc, 'بيانات المنشأة')
    info = [
        ('اسم المنشأة', evaluation.facility_name),
        ('نوع النشاط', evaluation.activity_type),
        ('رقم الرخصة', evaluation.license_number),
        ('رقم السجل التجاري', evaluation.cr_number),
        ('المحافظة', evaluation.governorate.name if evaluation.governorate else ''),
        ('الولاية', evaluation.wilayat.name if evaluation.wilayat else ''),
        ('تاريخ الزيارة', str(evaluation.visit_date)),
        ('فريق التقييم', evaluation.evaluation_team),
        ('عدد الورديات', evaluation.shift_count),
        ('عدد العاملين في الوردية', evaluation.workers_per_shift),
        ('مجموع عدد العاملين المصنع', evaluation.total_factory_workers),
        ('عدد المشرفين في الوردية', evaluation.supervisors_per_shift),
        ('مجموع عدد المشرفين', evaluation.total_supervisors),
        ('أنواع المنتجات', evaluation.product_types),
        ('التوزيع (محلي/تصدير)', evaluation.distribution_scope),
        ('معدل الإنتاج اليومي الفعلي', evaluation.actual_daily_production_rate),
        ('معدل الإنتاج اليومي المسموح', evaluation.permitted_daily_production_rate),
        ('مصدر الماء المستخدم', evaluation.water_source),
        ('إجمالي مساحة مخزن المنتج النهائي', evaluation.final_product_storage_area),
        ('دليل الهاسب للشركة إن وجد', evaluation.haccp_manual),
        ('آيزو 22000', evaluation.iso_22000_certificate),
        ('الهاسب', evaluation.haccp_certificate),
        ('أخرى', evaluation.other_quality_certificate),
        ('النتيجة', f'{evaluation.score}%'),
        ('الوضع العام للمنشأة', evaluation.classification),
    ]

    table = doc.add_table(rows=0, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    for label, value in info:
        row = table.add_row().cells
        shade_cell(row[1], 'E6F4EE')
        set_cell_text(row[0], value)
        set_cell_text(row[1], label, bold=True)

    add_section_heading(doc, 'مستندات الهاسب وشهادات أنظمة الجودة')
    table3 = doc.add_table(rows=1, cols=4)
    table3.alignment = WD_TABLE_ALIGNMENT.CENTER
    table3.style = 'Table Grid'
    hdr = table3.rows[0].cells
    hdr[0].text = 'الملاحظات'
    hdr[1].text = 'لا'
    hdr[2].text = 'نعم'
    hdr[3].text = 'المتطلبات'
    style_table_header(table3.rows[0])

    for haccp_row in build_haccp_rows(evaluation):
        row = table3.add_row().cells
        set_cell_text(row[0], haccp_row['notes'])
        set_cell_text(row[1], 'نعم' if haccp_row['exists'] == 'no' else '')
        set_cell_text(row[2], 'نعم' if haccp_row['exists'] == 'yes' else '')
        set_cell_text(row[3], haccp_row['requirement'])

    add_report_signature(doc)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.read(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename=evaluation_report_{evaluation.pk}.docx'
    return response
