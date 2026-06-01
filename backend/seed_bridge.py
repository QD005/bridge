"""
Bridge Uganda - Complete Database Seeding Script
Run this in Django shell or as a custom management command.
"""

import json
from apps.agencies.models import Agency
from apps.services.models import ServiceEndpoint

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
            print(f"Created agency: {agency.name} (ID: {agency.id})")
        else:
            print(f"Agency exists: {agency.name} (ID: {agency.id})")

    print(f"\nTotal agencies created: {created_count}")
    return Agency.objects.all()


def seed_services():
    """Seed all service endpoints."""
    services_data = [
        # NIRA (ID 2) - Identity
        {
            "agency_id": 2,
            "name": "Verify Citizen Identity",
            "description": "Verify a Ugandan citizen's national identity using NIN or registration number.",
            "endpoint_url": "/api/v1/identity/verify",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json", "Accept": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "nin": {"type": "string", "label": "National ID Number", "placeholder": "CM1234567890AB"},
                    "surname": {"type": "string", "label": "Surname", "placeholder": "Mukasa"}
                },
                "required": ["nin"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "verified": {"type": "boolean"},
                    "full_name": {"type": "string"},
                    "date_of_birth": {"type": "string"},
                    "gender": {"type": "string"}
                }
            },
            "timeout_seconds": 15,
            "retry_count": 2,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 120, "burst": 20}
        },
        {
            "agency_id": 2,
            "name": "Verify National ID Card Status",
            "description": "Check if a national ID card is ready for collection.",
            "endpoint_url": "/api/v1/identity/card-status",
            "http_method": "GET",
            "headers": {"Accept": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "application_ref": {"type": "string", "label": "Application Reference", "placeholder": "NIRA-2024-001234"}
                },
                "required": ["application_ref"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "collection_center": {"type": "string"},
                    "expected_date": {"type": "string"}
                }
            },
            "timeout_seconds": 10,
            "retry_count": 2,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 200, "burst": 30}
        },
        # URSB (ID 1) - Business
        {
            "agency_id": 1,
            "name": "Verify Business Registration",
            "description": "Verify if a business is registered with URSB.",
            "endpoint_url": "/api/v1/business/verify",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "registration_number": {"type": "string", "label": "Registration Number", "placeholder": "8001000123456"},
                    "business_name": {"type": "string", "label": "Business Name", "placeholder": "Acme Enterprises Ltd"}
                },
                "required": ["registration_number"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "exists": {"type": "boolean"},
                    "business_name": {"type": "string"},
                    "status": {"type": "string"},
                    "registration_date": {"type": "string"}
                }
            },
            "timeout_seconds": 20,
            "retry_count": 3,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 100, "burst": 15}
        },
        {
            "agency_id": 1,
            "name": "Search Company Directors",
            "description": "Retrieve company directors and shareholders information.",
            "endpoint_url": "/api/v1/company/directors",
            "http_method": "GET",
            "headers": {"Accept": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "registration_number": {"type": "string", "label": "Company Registration Number", "placeholder": "8001000123456"}
                },
                "required": ["registration_number"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string"},
                    "directors": {"type": "array"},
                    "shareholders": {"type": "array"}
                }
            },
            "timeout_seconds": 25,
            "retry_count": 2,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 60, "burst": 10}
        },
        {
            "agency_id": 1,
            "name": "Register New Business",
            "description": "Submit a new business registration application.",
            "endpoint_url": "/api/v1/business/register",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "business_name": {"type": "string", "label": "Business Name", "placeholder": "Acme Enterprises Ltd"},
                    "business_type": {"type": "string", "label": "Business Type", "placeholder": "Private Limited Company"},
                    "directors": {"type": "array", "label": "Directors", "placeholder": "[{\"name\": \"John Doe\", \"nin\": \"CM1234567890AB\"}]"},
                    "share_capital": {"type": "number", "label": "Share Capital (UGX)", "placeholder": 10000000},
                    "registered_address": {"type": "string", "label": "Registered Address", "placeholder": "Plot 1, Kampala Road"}
                },
                "required": ["business_name", "business_type", "directors"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string"},
                    "status": {"type": "string"},
                    "registration_number": {"type": "string"},
                    "expected_completion": {"type": "string"}
                }
            },
            "timeout_seconds": 30,
            "retry_count": 1,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 30, "burst": 5}
        },
        # URA (ID 3) - Tax
        {
            "agency_id": 3,
            "name": "Check Tax Compliance",
            "description": "Check whether a business or individual is tax compliant.",
            "endpoint_url": "/api/v1/tax/compliance",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "tin": {"type": "string", "label": "Tax Identification Number", "placeholder": "1000123456"}
                },
                "required": ["tin"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "compliant": {"type": "boolean"},
                    "taxpayer_name": {"type": "string"},
                    "compliance_status": {"type": "string"}
                }
            },
            "timeout_seconds": 15,
            "retry_count": 3,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 150, "burst": 25}
        },
        {
            "agency_id": 3,
            "name": "Validate TIN",
            "description": "Validate Tax Identification Number details.",
            "endpoint_url": "/api/v1/tin/validate",
            "http_method": "GET",
            "headers": {"Accept": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "tin": {"type": "string", "label": "TIN", "placeholder": "1000123456"}
                },
                "required": ["tin"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "valid": {"type": "boolean"},
                    "taxpayer_name": {"type": "string"},
                    "registration_status": {"type": "string"}
                }
            },
            "timeout_seconds": 10,
            "retry_count": 2,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 200, "burst": 30}
        },
        {
            "agency_id": 3,
            "name": "File Tax Return",
            "description": "Submit a tax return for a registered taxpayer.",
            "endpoint_url": "/api/v1/tax/returns/file",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "tin": {"type": "string", "label": "TIN", "placeholder": "1000123456"},
                    "tax_period": {"type": "string", "label": "Tax Period", "placeholder": "2024-Q1"},
                    "gross_income": {"type": "number", "label": "Gross Income (UGX)", "placeholder": 50000000},
                    "tax_deducted": {"type": "number", "label": "Tax Deducted (UGX)", "placeholder": 15000000}
                },
                "required": ["tin", "tax_period", "gross_income"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "return_id": {"type": "string"},
                    "status": {"type": "string"},
                    "tax_payable": {"type": "number"},
                    "due_date": {"type": "string"}
                }
            },
            "timeout_seconds": 20,
            "retry_count": 2,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 50, "burst": 10}
        },
        # NSSF (ID 9) - Social Security
        {
            "agency_id": 9,
            "name": "Check NSSF Employer Compliance",
            "description": "Check whether an employer is compliant with NSSF contributions.",
            "endpoint_url": "/api/v1/employers/compliance",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "employer_number": {"type": "string", "label": "Employer Number", "placeholder": "NSSF-EMP-001234"}
                },
                "required": ["employer_number"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "compliant": {"type": "boolean"},
                    "last_submission_date": {"type": "string"},
                    "outstanding_balance": {"type": "number"}
                }
            },
            "timeout_seconds": 20,
            "retry_count": 3,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 80, "burst": 10}
        },
        {
            "agency_id": 9,
            "name": "Verify Employee Contributions",
            "description": "Check an employee's NSSF contribution history and balance.",
            "endpoint_url": "/api/v1/employees/contributions",
            "http_method": "GET",
            "headers": {"Accept": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "nssf_number": {"type": "string", "label": "NSSF Number", "placeholder": "NSSF-001234567"}
                },
                "required": ["nssf_number"]
            },
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
            "timeout_seconds": 15,
            "retry_count": 2,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 100, "burst": 15}
        },
        # DCIC (ID 8) - Immigration
        {
            "agency_id": 8,
            "name": "Passport Verification",
            "description": "Verify passport validity and holder details.",
            "endpoint_url": "/api/v1/passports/verify",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "passport_number": {"type": "string", "label": "Passport Number", "placeholder": "A00012345"}
                },
                "required": ["passport_number"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "valid": {"type": "boolean"},
                    "holder_name": {"type": "string"},
                    "expiry_date": {"type": "string"},
                    "nationality": {"type": "string"}
                }
            },
            "timeout_seconds": 15,
            "retry_count": 2,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 90, "burst": 15}
        },
        {
            "agency_id": 8,
            "name": "Visa Application Status",
            "description": "Check the status of a visa application.",
            "endpoint_url": "/api/v1/visa/status",
            "http_method": "GET",
            "headers": {"Accept": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "application_ref": {"type": "string", "label": "Application Reference", "placeholder": "VISA-2024-001234"}
                },
                "required": ["application_ref"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "applicant_name": {"type": "string"},
                    "visa_type": {"type": "string"},
                    "expected_decision_date": {"type": "string"}
                }
            },
            "timeout_seconds": 12,
            "retry_count": 2,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 110, "burst": 20}
        },
        # UNEB (ID 10) - Education
        {
            "agency_id": 10,
            "name": "Verify Examination Results",
            "description": "Verify UNEB examination results and candidate details.",
            "endpoint_url": "/api/v1/results/verify",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "index_number": {"type": "string", "label": "Index Number", "placeholder": "U0001/001"},
                    "year": {"type": "integer", "label": "Year", "placeholder": 2024}
                },
                "required": ["index_number", "year"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "candidate_name": {"type": "string"},
                    "school_name": {"type": "string"},
                    "grades": {"type": "array"},
                    "verified": {"type": "boolean"}
                }
            },
            "timeout_seconds": 25,
            "retry_count": 2,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 70, "burst": 10}
        },
        {
            "agency_id": 10,
            "name": "Check School Registration",
            "description": "Verify if a school is registered and accredited by UNEB.",
            "endpoint_url": "/api/v1/schools/verify",
            "http_method": "GET",
            "headers": {"Accept": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "school_code": {"type": "string", "label": "School Code", "placeholder": "UNEB-SCH-001"}
                },
                "required": ["school_code"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "registered": {"type": "boolean"},
                    "school_name": {"type": "string"},
                    "district": {"type": "string"},
                    "accreditation_status": {"type": "string"}
                }
            },
            "timeout_seconds": 15,
            "retry_count": 2,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 100, "burst": 15}
        },
        # KCCA (ID 6) - City
        {
            "agency_id": 6,
            "name": "Business License Verification",
            "description": "Verify whether a business license issued by KCCA is valid.",
            "endpoint_url": "/api/v1/licenses/verify",
            "http_method": "GET",
            "headers": {"Accept": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "license_number": {"type": "string", "label": "License Number", "placeholder": "KCCA-BL-2024-001234"}
                },
                "required": ["license_number"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "valid": {"type": "boolean"},
                    "business_name": {"type": "string"},
                    "expiry_date": {"type": "string"}
                }
            },
            "timeout_seconds": 12,
            "retry_count": 2,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 100, "burst": 20}
        },
        {
            "agency_id": 6,
            "name": "Apply for Business License",
            "description": "Submit a new business license application to KCCA.",
            "endpoint_url": "/api/v1/licenses/apply",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "business_name": {"type": "string", "label": "Business Name", "placeholder": "Acme Enterprises Ltd"},
                    "business_type": {"type": "string", "label": "Business Type", "placeholder": "Retail Shop"},
                    "location": {"type": "string", "label": "Business Location", "placeholder": "Plot 45, Kampala Road"},
                    "owner_nin": {"type": "string", "label": "Owner NIN", "placeholder": "CM1234567890AB"},
                    "contact_phone": {"type": "string", "label": "Contact Phone", "placeholder": "+256700123456"}
                },
                "required": ["business_name", "business_type", "location", "owner_nin"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string"},
                    "status": {"type": "string"},
                    "license_fee": {"type": "number"},
                    "payment_deadline": {"type": "string"}
                }
            },
            "timeout_seconds": 20,
            "retry_count": 2,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 40, "burst": 8}
        },
        # UNBS (ID 4) - Standards
        {
            "agency_id": 4,
            "name": "Product Certification Verification",
            "description": "Verify whether a product has been certified by UNBS.",
            "endpoint_url": "/api/v1/products/certification/verify",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "product_code": {"type": "string", "label": "Product Code", "placeholder": "UNBS-CERT-001234"},
                    "manufacturer": {"type": "string", "label": "Manufacturer", "placeholder": "Acme Manufacturing Ltd"}
                },
                "required": ["product_code"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "certified": {"type": "boolean"},
                    "certificate_number": {"type": "string"},
                    "expiry_date": {"type": "string"}
                }
            },
            "timeout_seconds": 18,
            "retry_count": 2,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 85, "burst": 15}
        },
        {
            "agency_id": 4,
            "name": "Apply for Quality Mark",
            "description": "Submit an application for UNBS quality mark certification.",
            "endpoint_url": "/api/v1/quality-mark/apply",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string", "label": "Product Name", "placeholder": "Premium Cooking Oil"},
                    "manufacturer": {"type": "string", "label": "Manufacturer", "placeholder": "Acme Foods Ltd"},
                    "product_category": {"type": "string", "label": "Category", "placeholder": "Food Products"},
                    "sample_quantity": {"type": "string", "label": "Sample Quantity", "placeholder": "5 litres"}
                },
                "required": ["product_name", "manufacturer", "product_category"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string"},
                    "status": {"type": "string"},
                    "inspection_date": {"type": "string"},
                    "estimated_cost": {"type": "number"}
                }
            },
            "timeout_seconds": 25,
            "retry_count": 1,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 30, "burst": 5}
        },
        # UNRA (ID 5) - Roads
        {
            "agency_id": 5,
            "name": "Verify Road Permit",
            "description": "Check validity of a road transport or construction permit.",
            "endpoint_url": "/api/v1/permits/verify",
            "http_method": "GET",
            "headers": {"Accept": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "permit_number": {"type": "string", "label": "Permit Number", "placeholder": "UNRA-2024-001234"}
                },
                "required": ["permit_number"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "valid": {"type": "boolean"},
                    "permit_type": {"type": "string"},
                    "expiry_date": {"type": "string"},
                    "holder_name": {"type": "string"}
                }
            },
            "timeout_seconds": 15,
            "retry_count": 2,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 90, "burst": 15}
        },
        {
            "agency_id": 5,
            "name": "Apply for Road Construction Permit",
            "description": "Submit application for road construction or rehabilitation permit.",
            "endpoint_url": "/api/v1/permits/apply",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "label": "Project Name", "placeholder": "Kampala-Jinja Highway Rehabilitation"},
                    "contractor_name": {"type": "string", "label": "Contractor", "placeholder": "Acme Construction Ltd"},
                    "contractor_reg": {"type": "string", "label": "Contractor Reg No", "placeholder": "8001000123456"},
                    "road_section": {"type": "string", "label": "Road Section", "placeholder": "Km 15-45, Kampala-Jinja Road"},
                    "estimated_duration": {"type": "string", "label": "Duration (months)", "placeholder": "18"}
                },
                "required": ["project_name", "contractor_name", "contractor_reg", "road_section"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string"},
                    "status": {"type": "string"},
                    "permit_fee": {"type": "number"},
                    "inspection_date": {"type": "string"}
                }
            },
            "timeout_seconds": 30,
            "retry_count": 1,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 25, "burst": 5}
        },
        # MIA (ID 7) - Ministry
        {
            "agency_id": 7,
            "name": "Verify Citizenship Status",
            "description": "Verify citizenship status and naturalization records.",
            "endpoint_url": "/api/v1/citizenship/verify",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "nin": {"type": "string", "label": "NIN", "placeholder": "CM1234567890AB"},
                    "certificate_number": {"type": "string", "label": "Certificate Number (if naturalized)", "placeholder": "NAT-2020-001234"}
                },
                "required": ["nin"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "citizen": {"type": "boolean"},
                    "citizenship_type": {"type": "string"},
                    "acquisition_date": {"type": "string"}
                }
            },
            "timeout_seconds": 15,
            "retry_count": 2,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 100, "burst": 15}
        },
        {
            "agency_id": 7,
            "name": "Apply for Citizenship by Naturalization",
            "description": "Submit application for citizenship by naturalization.",
            "endpoint_url": "/api/v1/citizenship/apply",
            "http_method": "POST",
            "headers": {"Content-Type": "application/json"},
            "request_schema": {
                "type": "object",
                "properties": {
                    "applicant_name": {"type": "string", "label": "Full Name", "placeholder": "John Smith"},
                    "date_of_birth": {"type": "string", "label": "Date of Birth", "placeholder": "1980-01-15"},
                    "nationality": {"type": "string", "label": "Current Nationality", "placeholder": "British"},
                    "residency_years": {"type": "integer", "label": "Years in Uganda", "placeholder": 10},
                    "marriage_certificate": {"type": "string", "label": "Marriage Cert (if applicable)", "placeholder": "MC-2015-001234"}
                },
                "required": ["applicant_name", "date_of_birth", "nationality", "residency_years"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "application_id": {"type": "string"},
                    "status": {"type": "string"},
                    "interview_date": {"type": "string"},
                    "processing_fee": {"type": "number"}
                }
            },
            "timeout_seconds": 30,
            "retry_count": 1,
            "status": "ACTIVE",
            "version": "v1",
            "rate_limits": {"requests_per_minute": 20, "burst": 3}
        }
    ]

    created_count = 0
    for data in services_data:
        agency_id = data.pop("agency_id")
        try:
            agency = Agency.objects.get(id=agency_id)
            service, created = ServiceEndpoint.objects.get_or_create(
                agency=agency,
                name=data["name"],
                defaults={**data, "agency": agency}
            )
            if created:
                created_count += 1
                print(f"Created service: {service.name} ({agency.code})")
            else:
                print(f"Service exists: {service.name} ({agency.code})")
        except Agency.DoesNotExist:
            print(f"WARNING: Agency ID {agency_id} not found for service {data['name']}")

    print(f"\nTotal services created: {created_count}")
    return ServiceEndpoint.objects.all()


def run_full_seed():
    """Run complete seeding."""
    print("=" * 60)
    print("BRIDGE UGANDA - DATABASE SEEDING")
    print("=" * 60)

    print("\n[1/2] Seeding Agencies...")
    agencies = seed_agencies()

    print("\n[2/2] Seeding Services...")
    services = seed_services()

    print("\n" + "=" * 60)
    print(f"SEEDING COMPLETE")
    print(f"  Agencies: {agencies.count()}")
    print(f"  Services: {services.count()}")
    print("=" * 60)


if __name__ == "__main__":
    run_full_seed()
