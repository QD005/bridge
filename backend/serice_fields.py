"""
Bridge Uganda - ServiceField Seeding Script
Populates ServiceField records for each ServiceEndpoint.
Run via: docker compose exec backend python manage.py shell
Then: exec(open('/app/seed_service_fields.py').read())
"""

import json
from apps.services.models import ServiceEndpoint, ServiceField

# Field definitions for each service
# Format: { "Service Name": [ {field_data}, ... ] }
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


def seed_service_fields():
    """Create ServiceField records for all services."""
    print("=" * 60)
    print("SEEDING SERVICE FIELDS")
    print("=" * 60)

    total_created = 0
    total_skipped = 0

    for service_name, fields in SERVICE_FIELDS.items():
        try:
            service = ServiceEndpoint.objects.get(name=service_name)
        except ServiceEndpoint.DoesNotExist:
            print(f"\nWARNING: Service '{service_name}' not found. Skipping {len(fields)} fields.")
            continue

        print(f"\n{service.name} ({service.agency.code}):")

        for field_data in fields:
            field_data["service"] = service

            # Handle options - ensure it's a list
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

    print("\n" + "=" * 60)
    print(f"SEEDING COMPLETE")
    print(f"  Fields created: {total_created}")
    print(f"  Fields skipped: {total_skipped}")
    print(f"  Total services with fields: {ServiceEndpoint.objects.filter(service_fields__isnull=False).distinct().count()}")
    print("=" * 60)

    return ServiceField.objects.all()


if __name__ == "__main__":
    seed_service_fields()
