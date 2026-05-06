from django.urls import path
from . import views

urlpatterns = [
    path('', views.evaluation_list, name='evaluation_list'),
    path('new/', views.evaluation_form, name='evaluation_form'),
    path('report/<int:pk>/', views.report_detail, name='report_detail'),
    path('report/<int:pk>/edit/', views.evaluation_edit, name='evaluation_edit'),
    path('report/<int:pk>/delete/', views.evaluation_delete, name='evaluation_delete'),
    path('report/<int:pk>/word/', views.export_word, name='export_word'),
    # API endpoints
    path('api/governorates/', views.get_governorates, name='get_governorates'),
    path('api/wilayats/', views.get_wilayats_by_governorate, name='get_wilayats'),
]
