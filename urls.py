from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),             # Homepage
    path('reports/', views.reports, name='reports'),  # View all reports
    path('report/', views.report_form, name='report_form'),  # Submit new report
    path('update_status/<int:report_id>/', views.update_status, name='update_status'),
]


