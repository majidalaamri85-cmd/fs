from django.contrib import admin
from .models import Governorate, Wilayat, Section, Item, Evaluation, Response, ResponseImage

@admin.register(Governorate)
class GovernorateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Wilayat)
class WilayatAdmin(admin.ModelAdmin):
    list_display = ('name', 'governorate')
    search_fields = ('name', 'governorate__name')
    list_filter = ('governorate',)

class ItemInline(admin.TabularInline):
    model = Item
    extra = 0

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    inlines = [ItemInline]

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('number', 'section', 'text')
    search_fields = ('text',)
    list_filter = ('section',)

class ResponseImageInline(admin.TabularInline):
    model = ResponseImage
    extra = 0

class ResponseInline(admin.TabularInline):
    model = Response
    extra = 0

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('facility_name', 'visit_date', 'score', 'classification', 'is_draft')
    search_fields = ('facility_name', 'license_number', 'cr_number')
    list_filter = ('classification', 'is_draft', 'governorate')
    inlines = [ResponseInline]

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('evaluation', 'item', 'status')
    list_filter = ('status',)
    inlines = [ResponseImageInline]
