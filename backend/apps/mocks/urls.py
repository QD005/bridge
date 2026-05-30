from django.urls import path
from . import views

urlpatterns = [
    # NIRA
    path('nira/verify/', views.nira_verify_identity, name='mock-nira-verify'),
    path('nira/citizen/', views.nira_fetch_citizen, name='mock-nira-citizen'),

    # URA
    path('ura/tax/compliance/', views.ura_tax_compliance, name='mock-ura-compliance'),
    path('ura/tin/validate/', views.ura_validate_tin, name='mock-ura-tin'),

    # URSB
    path('ursb/business/verify/', views.ursb_business_verify, name='mock-ursb-verify'),
    path('ursb/company/search/', views.ursb_company_search, name='mock-ursb-search'),

    # Police
    path('police/clearance/', views.police_clearance, name='mock-police-clearance'),

    # KCCA
    path('kcca/license/approve/', views.kcca_license_approve, name='mock-kcca-license'),
    path('kcca/health/inspect/', views.kcca_health_inspection, name='mock-kcca-health'),

    # Health check
    path('health/<str:agency_code>/', views.agency_health, name='mock-health'),
]