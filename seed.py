"""
Bridge Uganda - Complete Database Seeding Script
Seeds: Agencies, ServiceEndpoints, and ServiceFields
Run via: docker compose exec backend python manage.py shell
Then: exec(open('/app/seed.py').read())
"""

import json
from apps.agencies.models import Agency
from apps.services.models import ServiceEndpoint, ServiceField


def seed_agencies():
    """Seed all government agencies."""
    agencies_data = [
        {
            "name": "Uganda Registration Services Bureau",
            "code": "URSB",
            "description": "Business registration, company incorporation, intellectual property, and civil registration services.",
            "agency_type": "Registration Authority",
            "contact_email": "info@ursb.go.ug",
            "contact_phone": "+256414233219",
            "website": "https://www.ursb.go.ug",
            "base_url": "https://api.ursb.go.ug",
            "authentication_type": "API_KEY",
            "auth_config": {"header_name": "X-API-KEY", "key_rotation_days": 90},
            "status": "ACTIVE"
        },
        {
            "name": "National Identification and Registration Authority",
            "code": "NIRA",
            "description": "National identity card registration, verification, and citizen records management.",
            "agency_type": "Identity Authority",
            "contact_email": "info@nira.go.ug",
            "contact_phone": "+256312264951",
            "website": "https://www.nira.go.ug",
            "base_url": "https://api.nira.go.ug",
            "authentication_type": "JWT",
            "auth_config": {"token_url": "https://api.nira.go.ug/auth/token", "client_id": "govbridge_client"},
            "status": "ACTIVE"
        },
        {
            "name": "Uganda Revenue Authority",
            "code": "URA",
            "description": "Tax administration, customs management, and revenue collection services.",
            "agency_type": "Revenue Authority",
            "contact_email": "info@ura.go.ug",
            "contact_phone": "+256414435000",
            "website": "https://www.ura.go.ug",
            "base_url": "https://api.ura.go.ug",
            "authentication_type": "JWT",
            "auth_config": {"token_url": "https://api.ura.go.ug/auth/token", "client_id": "govbridge_client"},
            "status": "ACTIVE"
        },
        {
            "name": "Uganda National Bureau of Standards",
            "code": "UNBS",
            "description": "Standards certification, product verification, and quality assurance services.",
            "agency_type": "Standards Authority",
            "contact_email": "info@unbs.go.ug",
            "contact_phone": "+256417333250",
            "website": "https://www.unbs.go.ug",
            "base_url": "https://api.unbs.go.ug",
            "authentication_type": "OAUTH2",
            "auth_config": {
                "authorization_url": "https://api.unbs.go.ug/oauth/authorize",
                "token_url": "https://api.unbs.go.ug/oauth/token",
                "scopes": ["certificates.read", "products.verify"]
            },
            "status": "ACTIVE"
        },
        {
            "name": "Uganda National Roads Authority",
            "code": "UNRA",
            "description": "Road infrastructure management, permits, and transport corridor services.",
            "agency_type": "Infrastructure Authority",
            "contact_email": "info@unra.go.ug",
            "contact_phone": "+256312233100",
            "website": "https://www.unra.go.ug",
            "base_url": "https://api.unra.go.ug",
            "authentication_type": "JWT",
            "auth_config": {"token_url": "https://api.unra.go.ug/auth/token", "client_id": "govbridge_client"},
            "status": "ACTIVE"
        },
        {
            "name": "Kampala Capital City Authority",
            "code": "KCCA",
            "description": "Urban administration, business licensing, property rates, and city services.",
            "agency_type": "City Authority",
            "contact_email": "info@kcca.go.ug",
            "contact_phone": "+256414342000",
            "website": "https://www.kcca.go.ug",
            "base_url": "https://api.kcca.go.ug",
            "authentication_type": "API_KEY",
            "auth_config": {"header_name": "X-API-KEY", "rate_limit_per_minute": 120},
            "status": "ACTIVE"
        },
        {
            "name": "Ministry of Internal Affairs",
            "code": "MIA",
            "description": "Citizenship, immigration, passports, and national security administration.",
            "agency_type": "Government Ministry",
            "contact_email": "info@mia.go.ug",
            "contact_phone": "+256414595945",
            "website": "https://www.mia.go.ug",
            "base_url": "https://api.mia.go.ug",
            "authentication_type": "OAUTH2",
            "auth_config": {
                "authorization_url": "https://api.mia.go.ug/oauth/authorize",
                "token_url": "https://api.mia.go.ug/oauth/token",
                "scopes": ["passport.read", "visa.read", "citizenship.verify"]
            },
            "status": "ACTIVE"
        },
        {
            "name": "Directorate of Citizenship and Immigration Control",
            "code": "DCIC",
            "description": "Passport issuance, visa processing, work permits, and immigration services.",
            "agency_type": "Immigration Authority",
            "contact_email": "info@immigration.go.ug",
            "contact_phone": "+256414595945",
            "website": "https://www.immigration.go.ug",
            "base_url": "https://api.immigration.go.ug",
            "authentication_type": "JWT",
            "auth_config": {"token_url": "https://api.immigration.go.ug/auth/token", "client_id": "govbridge_client"},
            "status": "ACTIVE"
        },
        {
            "name": "National Social Security Fund",
            "code": "NSSF",
            "description": "Employee social security contributions and benefits management.",
            "agency_type": "Social Security Fund",
            "contact_email": "info@nssfug.org",
            "contact_phone": "+256312224600",
            "website": "https://www.nssfug.org",
            "base_url": "https://api.nssfug.org",
            "authentication_type": "API_KEY",
            "auth_config": {"header_name": "Authorization", "prefix": "Bearer"},
            "status": "ACTIVE"
        },
        {
            "name": "Uganda National Examinations Board",
            "code": "UNEB",
            "description": "Management of national examinations and academic records verification.",
            "agency_type": "Education Authority",
            "contact_email": "info@uneb.ac.ug",
            "contact_phone": "+256414289397",
            "website": "https://www.uneb.ac.ug",
            "base_url": "https://api.uneb.ac.ug",
            "authentication_type": "JWT",
            "auth_config": {"token_url": "https://api.uneb.ac.ug/auth/token", "client_id": "govbridge_client"},
            "status": "ACTIVE"
        }
    ]

    created_count = 0
    for data in agencies_data:
        agency, created = Agency.objects.get_or_create(
            code=data["code"],
            defaults=data
        )
        if created:
            created_count += 1
            print(f"  Created agency: {agency.name} (ID: {agency.id})")
        else:
            print(f"  Agency exists: {agency.name} (ID: {agency.id})")

    print(f"\n  Total agencies created: {created_count}")
    return Agency.objects.all()


def seed_services():
    """Seed all service endpoints (matching actual ServiceEndpoint model fields)."""

    agency_map = {a.code: a.id for a in Agency.objects.all()}

    services_data = [
        {
            "agency_code": "NIRA",
            "name": "Verify Citizen Identity",
            "description": "Verify a Ugandan citizen's national identity using NIN or registration number.",
            "endpoint_url": "/api/v1/identity/verify",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json", "Accept": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "verified": {"type": "boolean"},
                    "full_name": {"type": "string"},
                    "date_of_birth": {"type": "string"},
                    "gender": {"type": "string"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 15,
            "retry_count": 2,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 120, "burst": 20},
            "field_definitions": [
                {"name": "nin", "label": "National ID Number", "type": "string", "required": True, "placeholder": "CM1234567890AB", "location": "body"},
                {"name": "surname", "label": "Surname", "type": "string", "required": False, "placeholder": "Mukasa", "location": "body"}
            ]
        },
        {
            "agency_code": "NIRA",
            "name": "Verify National ID Card Status",
            "description": "Check if a national ID card is ready for collection.",
            "endpoint_url": "/api/v1/identity/card-status",
            "http_method": "GET",
            "headers": {"Accept": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "collection_center": {"type": "string"},
                    "expected_date": {"type": "string"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 10,
            "retry_count": 2,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 200, "burst": 30},
            "field_definitions": [
                {"name": "application_ref", "label": "Application Reference", "type": "string", "required": True, "placeholder": "NIRA-2024-001234", "location": "query"}
            ]
        },
        {
            "agency_code": "URSB",
            "name": "Verify Business Registration",
            "description": "Verify if a business is registered with URSB.",
            "endpoint_url": "/api/v1/business/verify",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "exists": {"type": "boolean"},
                    "business_name": {"type": "string"},
                    "status": {"type": "string"},
                    "registration_date": {"type": "string"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 20,
            "retry_count": 3,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 100, "burst": 15},
            "field_definitions": [
                {"name": "registration_number", "label": "Registration Number", "type": "string", "required": True, "placeholder": "8001000123456", "location": "body"},
                {"name": "business_name", "label": "Business Name", "type": "string", "required": False, "placeholder": "Acme Enterprises Ltd", "location": "body"}
            ]
        },
        {
            "agency_code": "URSB",
            "name": "Search Company Directors",
            "description": "Retrieve company directors and shareholders information.",
            "endpoint_url": "/api/v1/company/directors",
            "http_method": "GET",
            "headers": {"Accept": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string"},
                    "directors": {"type": "array"},
                    "shareholders": {"type": "array"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 25,
            "retry_count": 2,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 60, "burst": 10},
            "field_definitions": [
                {"name": "registration_number", "label": "Company Registration Number", "type": "string", "required": True, "placeholder": "8001000123456", "location": "query"}
            ]
        },
        {
            "agency_code": "URSB",
            "name": "Register New Business",
            "description": "Submit a new business registration application.",
            "endpoint_url": "/api/v1/business/register",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string"},
                    "status": {"type": "string"},
                    "registration_number": {"type": "string"},
                    "expected_completion": {"type": "string"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 30,
            "retry_count": 1,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 30, "burst": 5},
            "field_definitions": [
                {"name": "business_name", "label": "Business Name", "type": "string", "required": True, "placeholder": "Acme Enterprises Ltd", "location": "body"},
                {"name": "business_type", "label": "Business Type", "type": "string", "required": True, "placeholder": "Private Limited Company", "location": "body"},
                {"name": "directors", "label": "Directors", "type": "json", "required": True, "placeholder": "[{\"name\": \"John Doe\", \"nin\": \"CM1234567890AB\"}]", "location": "body"},
                {"name": "share_capital", "label": "Share Capital (UGX)", "type": "number", "required": False, "placeholder": "10000000", "location": "body"},
                {"name": "registered_address", "label": "Registered Address", "type": "string", "required": False, "placeholder": "Plot 1, Kampala Road", "location": "body"}
            ]
        },
        {
            "agency_code": "URA",
            "name": "Check Tax Compliance",
            "description": "Check whether a business or individual is tax compliant.",
            "endpoint_url": "/api/v1/tax/compliance",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "compliant": {"type": "boolean"},
                    "taxpayer_name": {"type": "string"},
                    "compliance_status": {"type": "string"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 15,
            "retry_count": 3,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 150, "burst": 25},
            "field_definitions": [
                {"name": "tin", "label": "Tax Identification Number", "type": "string", "required": True, "placeholder": "1000123456", "location": "body"}
            ]
        },
        {
            "agency_code": "URA",
            "name": "Validate TIN",
            "description": "Validate Tax Identification Number details.",
            "endpoint_url": "/api/v1/tin/validate",
            "http_method": "GET",
            "headers": {"Accept": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "valid": {"type": "boolean"},
                    "taxpayer_name": {"type": "string"},
                    "registration_status": {"type": "string"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 10,
            "retry_count": 2,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 200, "burst": 30},
            "field_definitions": [
                {"name": "tin", "label": "TIN", "type": "string", "required": True, "placeholder": "1000123456", "location": "query"}
            ]
        },
        {
            "agency_code": "URA",
            "name": "File Tax Return",
            "description": "Submit a tax return for a registered taxpayer.",
            "endpoint_url": "/api/v1/tax/returns/file",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "return_id": {"type": "string"},
                    "status": {"type": "string"},
                    "tax_payable": {"type": "number"},
                    "due_date": {"type": "string"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 20,
            "retry_count": 2,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 50, "burst": 10},
            "field_definitions": [
                {"name": "tin", "label": "TIN", "type": "string", "required": True, "placeholder": "1000123456", "location": "body"},
                {"name": "tax_period", "label": "Tax Period", "type": "string", "required": True, "placeholder": "2024-Q1", "location": "body"},
                {"name": "gross_income", "label": "Gross Income (UGX)", "type": "number", "required": True, "placeholder": "50000000", "location": "body"},
                {"name": "tax_deducted", "label": "Tax Deducted (UGX)", "type": "number", "required": False, "placeholder": "15000000", "location": "body"}
            ]
        },
        {
            "agency_code": "NSSF",
            "name": "Check NSSF Employer Compliance",
            "description": "Check whether an employer is compliant with NSSF contributions.",
            "endpoint_url": "/api/v1/employers/compliance",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "compliant": {"type": "boolean"},
                    "last_submission_date": {"type": "string"},
                    "outstanding_balance": {"type": "number"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 20,
            "retry_count": 3,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 80, "burst": 10},
            "field_definitions": [
                {"name": "employer_number", "label": "Employer Number", "type": "string", "required": True, "placeholder": "NSSF-EMP-001234", "location": "body"}
            ]
        },
        {
            "agency_code": "NSSF",
            "name": "Verify Employee Contributions",
            "description": "Check an employee's NSSF contribution history and balance.",
            "endpoint_url": "/api/v1/employees/contributions",
            "http_method": "GET",
            "headers": {"Accept": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "employee_name": {"type": "string"},
                    "total_contributions": {"type": "number"},
                    "employer_contributions": {"type": "number"},
                    "employee_contributions": {"type": "number"},
                    "eligibility_date": {"type": "string"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 15,
            "retry_count": 2,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 100, "burst": 15},
            "field_definitions": [
                {"name": "nssf_number", "label": "NSSF Number", "type": "string", "required": True, "placeholder": "NSSF-001234567", "location": "query"}
            ]
        },
        {
            "agency_code": "DCIC",
            "name": "Passport Verification",
            "description": "Verify passport validity and holder details.",
            "endpoint_url": "/api/v1/passports/verify",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "valid": {"type": "boolean"},
                    "holder_name": {"type": "string"},
                    "expiry_date": {"type": "string"},
                    "nationality": {"type": "string"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 15,
            "retry_count": 2,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 90, "burst": 15},
            "field_definitions": [
                {"name": "passport_number", "label": "Passport Number", "type": "string", "required": True, "placeholder": "A00012345", "location": "body"}
            ]
        },
        {
            "agency_code": "DCIC",
            "name": "Visa Application Status",
            "description": "Check the status of a visa application.",
            "endpoint_url": "/api/v1/visa/status",
            "http_method": "GET",
            "headers": {"Accept": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "applicant_name": {"type": "string"},
                    "visa_type": {"type": "string"},
                    "expected_decision_date": {"type": "string"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 12,
            "retry_count": 2,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 110, "burst": 20},
            "field_definitions": [
                {"name": "application_ref", "label": "Application Reference", "type": "string", "required": True, "placeholder": "VISA-2024-001234", "location": "query"}
            ]
        },
        {
            "agency_code": "UNEB",
            "name": "Verify Examination Results",
            "description": "Verify UNEB examination results and candidate details.",
            "endpoint_url": "/api/v1/results/verify",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "candidate_name": {"type": "string"},
                    "school_name": {"type": "string"},
                    "grades": {"type": "array"},
                    "verified": {"type": "boolean"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 25,
            "retry_count": 2,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 70, "burst": 10},
            "field_definitions": [
                {"name": "index_number", "label": "Index Number", "type": "string", "required": True, "placeholder": "U0001/001", "location": "body"},
                {"name": "year", "label": "Year", "type": "integer", "required": True, "placeholder": 2024, "location": "body"}
            ]
        },
        {
            "agency_code": "UNEB",
            "name": "Check School Registration",
            "description": "Verify if a school is registered and accredited by UNEB.",
            "endpoint_url": "/api/v1/schools/verify",
            "http_method": "GET",
            "headers": {"Accept": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "registered": {"type": "boolean"},
                    "school_name": {"type": "string"},
                    "district": {"type": "string"},
                    "accreditation_status": {"type": "string"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 15,
            "retry_count": 2,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 100, "burst": 15},
            "field_definitions": [
                {"name": "school_code", "label": "School Code", "type": "string", "required": True, "placeholder": "UNEB-SCH-001", "location": "query"}
            ]
        },
        {
            "agency_code": "KCCA",
            "name": "Business License Verification",
            "description": "Verify whether a business license issued by KCCA is valid.",
            "endpoint_url": "/api/v1/licenses/verify",
            "http_method": "GET",
            "headers": {"Accept": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "valid": {"type": "boolean"},
                    "business_name": {"type": "string"},
                    "expiry_date": {"type": "string"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 12,
            "retry_count": 2,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 100, "burst": 20},
            "field_definitions": [
                {"name": "license_number", "label": "License Number", "type": "string", "required": True, "placeholder": "KCCA-BL-2024-001234", "location": "query"}
            ]
        },
        {
            "agency_code": "KCCA",
            "name": "Apply for Business License",
            "description": "Submit a new business license application to KCCA.",
            "endpoint_url": "/api/v1/licenses/apply",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string"},
                    "status": {"type": "string"},
                    "license_fee": {"type": "number"},
                    "payment_deadline": {"type": "string"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 20,
            "retry_count": 2,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 40, "burst": 8},
            "field_definitions": [
                {"name": "business_name", "label": "Business Name", "type": "string", "required": True, "placeholder": "Acme Enterprises Ltd", "location": "body"},
                {"name": "business_type", "label": "Business Type", "type": "string", "required": True, "placeholder": "Retail Shop", "location": "body"},
                {"name": "location", "label": "Business Location", "type": "string", "required": True, "placeholder": "Plot 45, Kampala Road", "location": "body"},
                {"name": "owner_nin", "label": "Owner NIN", "type": "string", "required": True, "placeholder": "CM1234567890AB", "location": "body"},
                {"name": "contact_phone", "label": "Contact Phone", "type": "string", "required": False, "placeholder": "+256700123456", "location": "body"}
            ]
        },
        {
            "agency_code": "UNBS",
            "name": "Product Certification Verification",
            "description": "Verify whether a product has been certified by UNBS.",
            "endpoint_url": "/api/v1/products/certification/verify",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "certified": {"type": "boolean"},
                    "certificate_number": {"type": "string"},
                    "expiry_date": {"type": "string"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 18,
            "retry_count": 2,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 85, "burst": 15},
            "field_definitions": [
                {"name": "product_code", "label": "Product Code", "type": "string", "required": True, "placeholder": "UNBS-CERT-001234", "location": "body"},
                {"name": "manufacturer", "label": "Manufacturer", "type": "string", "required": False, "placeholder": "Acme Manufacturing Ltd", "location": "body"}
            ]
        },
        {
            "agency_code": "UNBS",
            "name": "Apply for Quality Mark",
            "description": "Submit an application for UNBS quality mark certification.",
            "endpoint_url": "/api/v1/quality-mark/apply",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string"},
                    "status": {"type": "string"},
                    "inspection_date": {"type": "string"},
                    "estimated_cost": {"type": "number"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 25,
            "retry_count": 1,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 30, "burst": 5},
            "field_definitions": [
                {"name": "product_name", "label": "Product Name", "type": "string", "required": True, "placeholder": "Premium Cooking Oil", "location": "body"},
                {"name": "manufacturer", "label": "Manufacturer", "type": "string", "required": True, "placeholder": "Acme Foods Ltd", "location": "body"},
                {"name": "product_category", "label": "Category", "type": "string", "required": True, "placeholder": "Food Products", "location": "body"},
                {"name": "sample_quantity", "label": "Sample Quantity", "type": "string", "required": False, "placeholder": "5 litres", "location": "body"}
            ]
        },
        {
            "agency_code": "UNRA",
            "name": "Verify Road Permit",
            "description": "Check validity of a road transport or construction permit.",
            "endpoint_url": "/api/v1/permits/verify",
            "http_method": "GET",
            "headers": {"Accept": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "valid": {"type": "boolean"},
                    "permit_type": {"type": "string"},
                    "expiry_date": {"type": "string"},
                    "holder_name": {"type": "string"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 15,
            "retry_count": 2,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 90, "burst": 15},
            "field_definitions": [
                {"name": "permit_number", "label": "Permit Number", "type": "string", "required": True, "placeholder": "UNRA-2024-001234", "location": "query"}
            ]
        },
        {
            "agency_code": "UNRA",
            "name": "Apply for Road Construction Permit",
            "description": "Submit application for road construction or rehabilitation permit.",
            "endpoint_url": "/api/v1/permits/apply",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string"},
                    "status": {"type": "string"},
                    "permit_fee": {"type": "number"},
                    "inspection_date": {"type": "string"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 30,
            "retry_count": 1,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 25, "burst": 5},
            "field_definitions": [
                {"name": "project_name", "label": "Project Name", "type": "string", "required": True, "placeholder": "Kampala-Jinja Highway Rehabilitation", "location": "body"},
                {"name": "contractor_name", "label": "Contractor", "type": "string", "required": True, "placeholder": "Acme Construction Ltd", "location": "body"},
                {"name": "contractor_reg", "label": "Contractor Reg No", "type": "string", "required": True, "placeholder": "8001000123456", "location": "body"},
                {"name": "road_section", "label": "Road Section", "type": "string", "required": True, "placeholder": "Km 15-45, Kampala-Jinja Road", "location": "body"},
                {"name": "estimated_duration", "label": "Duration (months)", "type": "string", "required": False, "placeholder": "18", "location": "body"}
            ]
        },
        {
            "agency_code": "MIA",
            "name": "Verify Citizenship Status",
            "description": "Verify citizenship status and naturalization records.",
            "endpoint_url": "/api/v1/citizenship/verify",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "citizen": {"type": "boolean"},
                    "citizenship_type": {"type": "string"},
                    "acquisition_date": {"type": "string"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 15,
            "retry_count": 2,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 100, "burst": 15},
            "field_definitions": [
                {"name": "nin", "label": "NIN", "type": "string", "required": True, "placeholder": "CM1234567890AB", "location": "body"},
                {"name": "certificate_number", "label": "Certificate Number (if naturalized)", "type": "string", "required": False, "placeholder": "NAT-2020-001234", "location": "body"}
            ]
        },
        {
            "agency_code": "MIA",
            "name": "Apply for Citizenship by Naturalization",
            "description": "Submit application for citizenship by naturalization.",
            "endpoint_url": "/api/v1/citizenship/apply",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "response_schema": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string"},
                    "status": {"type": "string"},
                    "interview_date": {"type": "string"},
                    "processing_fee": {"type": "number"}
                }
            },
            "authentication_override": {},
            "timeout_seconds": 30,
            "retry_count": 1,
            "status": "ACTIVE",
            "health_status": "HEALTHY",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 20, "burst": 3},
            "field_definitions": [
                {"name": "applicant_name", "label": "Full Name", "type": "string", "required": True, "placeholder": "John Smith", "location": "body"},
                {"name": "date_of_birth", "label": "Date of Birth", "type": "string", "required": True, "placeholder": "1980-01-15", "location": "body"},
                {"name": "nationality", "label": "Current Nationality", "type": "string", "required": True, "placeholder": "British", "location": "body"},
                {"name": "residency_years", "label": "Years in Uganda", "type": "integer", "required": True, "placeholder": 10, "location": "body"},
                {"name": "marriage_certificate", "label": "Marriage Cert (if applicable)", "type": "string", "required": False, "placeholder": "MC-2015-001234", "location": "body"}
            ]
        }
    ]

    created_count = 0
    for data in services_data:
        agency_code = data.pop("agency_code")
        field_definitions = data.pop("field_definitions", [])
        agency_id = agency_map.get(agency_code)

        if not agency_id:
            print(f"  WARNING: Agency {agency_code} not found. Skipping {data['name']}")
            continue

        try:
            agency = Agency.objects.get(id=agency_id)
            service, created = ServiceEndpoint.objects.get_or_create(
                agency=agency,
                name=data["name"],
                defaults={**data, "agency": agency}
            )
            if created:
                created_count += 1
                print(f"  Created service: {service.name} ({agency.code})")
            else:
                print(f"  Service exists: {service.name} ({agency.code})")

            # Store field definitions in service for reference
            service.field_definitions = field_definitions
            service.save(update_fields=['field_definitions'])

        except Exception as e:
            print(f"  ERROR creating {data['name']}: {e}")

    print(f"\n  Total services created: {created_count}")
    return ServiceEndpoint.objects.all()


def seed_service_fields():
    """Create proper ServiceField records for all services."""

    # Field definitions mapped by service name
    SERVICE_FIELDS = {
        "Verify Citizen Identity": [
            {
                "name": "nin",
                "label": "National ID Number",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "CM1234567890AB",
                "help_text": "Enter the 14-character National Identification Number",
                "validation_regex": "^CM[0-9]{10}[A-Z]{2}$",
                "min_length": 14,
                "max_length": 14,
                "order": 1,
                "is_sensitive": False
            },
            {
                "name": "surname",
                "label": "Surname",
                "field_type": "text",
                "required": False,
                "location": "body",
                "placeholder": "Mukasa",
                "help_text": "Optional: Enter surname for additional verification",
                "order": 2,
                "is_sensitive": False
            }
        ],
        "Verify National ID Card Status": [
            {
                "name": "application_ref",
                "label": "Application Reference",
                "field_type": "text",
                "required": True,
                "location": "query",
                "placeholder": "NIRA-2024-001234",
                "help_text": "The reference number given when you applied for the ID card",
                "order": 1,
                "is_sensitive": False
            }
        ],
        "Verify Business Registration": [
            {
                "name": "registration_number",
                "label": "Registration Number",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "8001000123456",
                "help_text": "URSB business registration number (13 digits)",
                "validation_regex": "^[0-9]{13}$",
                "min_length": 13,
                "max_length": 13,
                "order": 1,
                "is_sensitive": False
            },
            {
                "name": "business_name",
                "label": "Business Name",
                "field_type": "text",
                "required": False,
                "location": "body",
                "placeholder": "Acme Enterprises Ltd",
                "help_text": "Optional: Confirm business name",
                "order": 2,
                "is_sensitive": False
            }
        ],
        "Search Company Directors": [
            {
                "name": "registration_number",
                "label": "Company Registration Number",
                "field_type": "text",
                "required": True,
                "location": "query",
                "placeholder": "8001000123456",
                "help_text": "URSB company registration number",
                "validation_regex": "^[0-9]{13}$",
                "min_length": 13,
                "max_length": 13,
                "order": 1,
                "is_sensitive": False
            }
        ],
        "Register New Business": [
            {
                "name": "business_name",
                "label": "Business Name",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "Acme Enterprises Ltd",
                "help_text": "Proposed name for the new business",
                "order": 1,
                "is_sensitive": False
            },
            {
                "name": "business_type",
                "label": "Business Type",
                "field_type": "select",
                "required": True,
                "location": "body",
                "placeholder": "",
                "help_text": "Select the legal structure of the business",
                "options": ["Private Limited Company", "Public Limited Company", "Partnership", "Sole Proprietorship", "Cooperative", "NGO"],
                "order": 2,
                "is_sensitive": False
            },
            {
                "name": "directors",
                "label": "Directors",
                "field_type": "textarea",
                "required": True,
                "location": "body",
                "placeholder": "[{\"name\": \"John Doe\", \"nin\": \"CM1234567890AB\"}]",
                "help_text": "JSON array of director objects with name and NIN",
                "order": 3,
                "is_sensitive": False
            },
            {
                "name": "share_capital",
                "label": "Share Capital (UGX)",
                "field_type": "number",
                "required": False,
                "location": "body",
                "placeholder": "10000000",
                "help_text": "Minimum share capital in Ugandan Shillings",
                "order": 4,
                "is_sensitive": False
            },
            {
                "name": "registered_address",
                "label": "Registered Address",
                "field_type": "textarea",
                "required": False,
                "location": "body",
                "placeholder": "Plot 1, Kampala Road",
                "help_text": "Physical address of the business premises",
                "order": 5,
                "is_sensitive": False
            }
        ],
        "Check Tax Compliance": [
            {
                "name": "tin",
                "label": "Tax Identification Number",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "1000123456",
                "help_text": "URA Tax Identification Number (10 digits)",
                "validation_regex": "^[0-9]{10}$",
                "min_length": 10,
                "max_length": 10,
                "order": 1,
                "is_sensitive": False
            }
        ],
        "Validate TIN": [
            {
                "name": "tin",
                "label": "TIN",
                "field_type": "text",
                "required": True,
                "location": "query",
                "placeholder": "1000123456",
                "help_text": "URA Tax Identification Number",
                "validation_regex": "^[0-9]{10}$",
                "min_length": 10,
                "max_length": 10,
                "order": 1,
                "is_sensitive": False
            }
        ],
        "File Tax Return": [
            {
                "name": "tin",
                "label": "TIN",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "1000123456",
                "help_text": "Taxpayer Identification Number",
                "validation_regex": "^[0-9]{10}$",
                "min_length": 10,
                "max_length": 10,
                "order": 1,
                "is_sensitive": False
            },
            {
                "name": "tax_period",
                "label": "Tax Period",
                "field_type": "select",
                "required": True,
                "location": "body",
                "placeholder": "",
                "help_text": "Select the tax period for this return",
                "options": ["2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4", "2025-Q1"],
                "order": 2,
                "is_sensitive": False
            },
            {
                "name": "gross_income",
                "label": "Gross Income (UGX)",
                "field_type": "number",
                "required": True,
                "location": "body",
                "placeholder": "50000000",
                "help_text": "Total gross income for the period",
                "order": 3,
                "is_sensitive": False
            },
            {
                "name": "tax_deducted",
                "label": "Tax Deducted (UGX)",
                "field_type": "number",
                "required": False,
                "location": "body",
                "placeholder": "15000000",
                "help_text": "Tax already deducted at source (if applicable)",
                "order": 4,
                "is_sensitive": False
            }
        ],
        "Check NSSF Employer Compliance": [
            {
                "name": "employer_number",
                "label": "Employer Number",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "NSSF-EMP-001234",
                "help_text": "NSSF employer registration number",
                "order": 1,
                "is_sensitive": False
            }
        ],
        "Verify Employee Contributions": [
            {
                "name": "nssf_number",
                "label": "NSSF Number",
                "field_type": "text",
                "required": True,
                "location": "query",
                "placeholder": "NSSF-001234567",
                "help_text": "Employee NSSF membership number",
                "order": 1,
                "is_sensitive": False
            }
        ],
        "Passport Verification": [
            {
                "name": "passport_number",
                "label": "Passport Number",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "A00012345",
                "help_text": "Ugandan passport number (format: A00000000)",
                "validation_regex": "^[A-Z][0-9]{8}$",
                "min_length": 9,
                "max_length": 9,
                "order": 1,
                "is_sensitive": False
            }
        ],
        "Visa Application Status": [
            {
                "name": "application_ref",
                "label": "Application Reference",
                "field_type": "text",
                "required": True,
                "location": "query",
                "placeholder": "VISA-2024-001234",
                "help_text": "Visa application reference number",
                "order": 1,
                "is_sensitive": False
            }
        ],
        "Verify Examination Results": [
            {
                "name": "index_number",
                "label": "Index Number",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "U0001/001",
                "help_text": "UNEB examination index number",
                "order": 1,
                "is_sensitive": False
            },
            {
                "name": "year",
                "label": "Year",
                "field_type": "number",
                "required": True,
                "location": "body",
                "placeholder": "2024",
                "help_text": "Year of examination",
                "validation_regex": "^[0-9]{4}$",
                "min_length": 4,
                "max_length": 4,
                "order": 2,
                "is_sensitive": False
            }
        ],
        "Check School Registration": [
            {
                "name": "school_code",
                "label": "School Code",
                "field_type": "text",
                "required": True,
                "location": "query",
                "placeholder": "UNEB-SCH-001",
                "help_text": "UNEB school registration code",
                "order": 1,
                "is_sensitive": False
            }
        ],
        "Business License Verification": [
            {
                "name": "license_number",
                "label": "License Number",
                "field_type": "text",
                "required": True,
                "location": "query",
                "placeholder": "KCCA-BL-2024-001234",
                "help_text": "KCCA business license number",
                "order": 1,
                "is_sensitive": False
            }
        ],
        "Apply for Business License": [
            {
                "name": "business_name",
                "label": "Business Name",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "Acme Enterprises Ltd",
                "help_text": "Name of the business to be licensed",
                "order": 1,
                "is_sensitive": False
            },
            {
                "name": "business_type",
                "label": "Business Type",
                "field_type": "select",
                "required": True,
                "location": "body",
                "placeholder": "",
                "help_text": "Category of business activity",
                "options": ["Retail Shop", "Restaurant", "Hotel", "Manufacturing", "Professional Services", "Transport", "Construction", "Healthcare", "Education", "Other"],
                "order": 2,
                "is_sensitive": False
            },
            {
                "name": "location",
                "label": "Business Location",
                "field_type": "textarea",
                "required": True,
                "location": "body",
                "placeholder": "Plot 45, Kampala Road",
                "help_text": "Physical address within Kampala",
                "order": 3,
                "is_sensitive": False
            },
            {
                "name": "owner_nin",
                "label": "Owner NIN",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "CM1234567890AB",
                "help_text": "National ID of the business owner",
                "validation_regex": "^CM[0-9]{10}[A-Z]{2}$",
                "min_length": 14,
                "max_length": 14,
                "order": 4,
                "is_sensitive": False
            },
            {
                "name": "contact_phone",
                "label": "Contact Phone",
                "field_type": "phone",
                "required": False,
                "location": "body",
                "placeholder": "+256700123456",
                "help_text": "Business contact phone number",
                "order": 5,
                "is_sensitive": False
            }
        ],
        "Product Certification Verification": [
            {
                "name": "product_code",
                "label": "Product Code",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "UNBS-CERT-001234",
                "help_text": "UNBS product certification code",
                "order": 1,
                "is_sensitive": False
            },
            {
                "name": "manufacturer",
                "label": "Manufacturer",
                "field_type": "text",
                "required": False,
                "location": "body",
                "placeholder": "Acme Manufacturing Ltd",
                "help_text": "Name of the product manufacturer",
                "order": 2,
                "is_sensitive": False
            }
        ],
        "Apply for Quality Mark": [
            {
                "name": "product_name",
                "label": "Product Name",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "Premium Cooking Oil",
                "help_text": "Name of the product to be certified",
                "order": 1,
                "is_sensitive": False
            },
            {
                "name": "manufacturer",
                "label": "Manufacturer",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "Acme Foods Ltd",
                "help_text": "Company manufacturing the product",
                "order": 2,
                "is_sensitive": False
            },
            {
                "name": "product_category",
                "label": "Category",
                "field_type": "select",
                "required": True,
                "location": "body",
                "placeholder": "",
                "help_text": "Product category for certification",
                "options": ["Food Products", "Beverages", "Cosmetics", "Pharmaceuticals", "Electronics", "Textiles", "Construction Materials", "Chemicals", "Other"],
                "order": 3,
                "is_sensitive": False
            },
            {
                "name": "sample_quantity",
                "label": "Sample Quantity",
                "field_type": "text",
                "required": False,
                "location": "body",
                "placeholder": "5 litres",
                "help_text": "Quantity of sample to submit for testing",
                "order": 4,
                "is_sensitive": False
            }
        ],
        "Verify Road Permit": [
            {
                "name": "permit_number",
                "label": "Permit Number",
                "field_type": "text",
                "required": True,
                "location": "query",
                "placeholder": "UNRA-2024-001234",
                "help_text": "UNRA road permit reference number",
                "order": 1,
                "is_sensitive": False
            }
        ],
        "Apply for Road Construction Permit": [
            {
                "name": "project_name",
                "label": "Project Name",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "Kampala-Jinja Highway Rehabilitation",
                "help_text": "Name of the road construction project",
                "order": 1,
                "is_sensitive": False
            },
            {
                "name": "contractor_name",
                "label": "Contractor",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "Acme Construction Ltd",
                "help_text": "Registered construction company",
                "order": 2,
                "is_sensitive": False
            },
            {
                "name": "contractor_reg",
                "label": "Contractor Reg No",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "8001000123456",
                "help_text": "URSB registration number of contractor",
                "validation_regex": "^[0-9]{13}$",
                "min_length": 13,
                "max_length": 13,
                "order": 3,
                "is_sensitive": False
            },
            {
                "name": "road_section",
                "label": "Road Section",
                "field_type": "textarea",
                "required": True,
                "location": "body",
                "placeholder": "Km 15-45, Kampala-Jinja Road",
                "help_text": "Specific section of road to be worked on",
                "order": 4,
                "is_sensitive": False
            },
            {
                "name": "estimated_duration",
                "label": "Duration (months)",
                "field_type": "number",
                "required": False,
                "location": "body",
                "placeholder": "18",
                "help_text": "Estimated project duration in months",
                "order": 5,
                "is_sensitive": False
            }
        ],
        "Verify Citizenship Status": [
            {
                "name": "nin",
                "label": "NIN",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "CM1234567890AB",
                "help_text": "National Identification Number",
                "validation_regex": "^CM[0-9]{10}[A-Z]{2}$",
                "min_length": 14,
                "max_length": 14,
                "order": 1,
                "is_sensitive": False
            },
            {
                "name": "certificate_number",
                "label": "Certificate Number (if naturalized)",
                "field_type": "text",
                "required": False,
                "location": "body",
                "placeholder": "NAT-2020-001234",
                "help_text": "Only required for naturalized citizens",
                "order": 2,
                "is_sensitive": False
            }
        ],
        "Apply for Citizenship by Naturalization": [
            {
                "name": "applicant_name",
                "label": "Full Name",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "John Smith",
                "help_text": "Full legal name of applicant",
                "order": 1,
                "is_sensitive": False
            },
            {
                "name": "date_of_birth",
                "label": "Date of Birth",
                "field_type": "date",
                "required": True,
                "location": "body",
                "placeholder": "1980-01-15",
                "help_text": "Date of birth (YYYY-MM-DD format)",
                "order": 2,
                "is_sensitive": False
            },
            {
                "name": "nationality",
                "label": "Current Nationality",
                "field_type": "text",
                "required": True,
                "location": "body",
                "placeholder": "British",
                "help_text": "Current citizenship/nationality",
                "order": 3,
                "is_sensitive": False
            },
            {
                "name": "residency_years",
                "label": "Years in Uganda",
                "field_type": "number",
                "required": True,
                "location": "body",
                "placeholder": "10",
                "help_text": "Number of years legally resident in Uganda",
                "order": 4,
                "is_sensitive": False
            },
            {
                "name": "marriage_certificate",
                "label": "Marriage Cert (if applicable)",
                "field_type": "text",
                "required": False,
                "location": "body",
                "placeholder": "MC-2015-001234",
                "help_text": "Only if applying through marriage to Ugandan",
                "order": 5,
                "is_sensitive": False
            }
        ]
    }

    total_created = 0
    total_skipped = 0

    for service_name, fields in SERVICE_FIELDS.items():
        try:
            service = ServiceEndpoint.objects.get(name=service_name)
        except ServiceEndpoint.DoesNotExist:
            print(f"  WARNING: Service '{service_name}' not found. Skipping {len(fields)} fields.")
            continue

        print(f"\n{service.name} ({service.agency.code}):")

        for field_data in fields:
            field_data["service"] = service

            # Ensure options is a list
            if "options" in field_data and field_data["options"]:
                field_data["options"] = list(field_data["options"])
            else:
                field_data["options"] = []

            # Use get_or_create to avoid duplicates
            field_obj, created = ServiceField.objects.get_or_create(
                service=service,
                name=field_data["name"],
                defaults=field_data
            )

            if created:
                total_created += 1
                print(f"  + {field_data['name']} ({field_data['field_type']})")
            else:
                total_skipped += 1
                print(f"  = {field_data['name']} (exists)")

    print(f"\n  Fields created: {total_created}")
    print(f"  Fields skipped: {total_skipped}")
    return ServiceField.objects.all()


def run_full_seed():
    """Run complete seeding: Agencies → Services → ServiceFields."""
    print("=" * 60)
    print("BRIDGE UGANDA - COMPLETE DATABASE SEEDING")
    print("=" * 60)

    print("\n[1/3] Seeding Agencies...")
    agencies = seed_agencies()

    print("\n[2/3] Seeding Services...")
    services = seed_services()

    print("\n[3/3] Seeding Service Fields...")
    fields = seed_service_fields()

    print("\n" + "=" * 60)
    print(f"SEEDING COMPLETE")
    print(f"  Agencies:       {agencies.count()}")
    print(f"  Services:        {services.count()}")
    print(f"  Service Fields:  {fields.count()}")
    print(f"  Services with fields: {ServiceEndpoint.objects.filter(service_fields__isnull=False).distinct().count()}")
    print("=" * 60)


if __name__ == "__main__":
    run_full_seed()
