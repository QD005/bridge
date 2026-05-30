import random
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


def _delay():
    """Simulate network latency"""
    time.sleep(random.uniform(0.3, 1.2))


def _json_response(data, status=200):
    response = JsonResponse(data, status=status)
    response["Content-Type"] = "application/json"
    return response


# ─────────────────────────────────────────────
# NIRA — National Identification & Registration Authority
# ─────────────────────────────────────────────

@csrf_exempt
def nira_verify_identity(request):
    """POST /mock/nira/verify"""
    _delay()

    if request.method != 'POST':
        return _json_response({"error": "Method not allowed"}, 405)

    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        body = {}

    nin = body.get('nin', '')
    surname = body.get('surname', '')

    # Simulate validation
    if not nin or len(nin) < 5:
        return _json_response({
            "verified": False,
            "error_code": "INVALID_NIN",
            "message": "National Identification Number is invalid or missing."
        }, 400)

    # Simulate some NINs failing
    if nin.endswith('999'):
        return _json_response({
            "verified": False,
            "error_code": "NOT_FOUND",
            "message": "Citizen record not found in NIRA database."
        }, 404)

    return _json_response({
        "verified": True,
        "nin": nin,
        "full_name": f"{surname or 'Kato'} John Bosco",
        "date_of_birth": "1985-03-15",
        "nationality": "Ugandan",
        "gender": "M",
        "photo_url": "https://mock.govbridge.go.ug/photos/citizen_001.jpg",
        "verification_timestamp": "2026-05-26T12:00:00Z",
        "agency": "NIRA"
    })


@csrf_exempt
def nira_fetch_citizen(request):
    """GET /mock/nira/citizen/{nin}"""
    _delay()
    nin = request.GET.get('nin', 'CM1234567890AB')

    return _json_response({
        "nin": nin,
        "full_name": "Kato John Bosco",
        "date_of_birth": "1985-03-15",
        "place_of_birth": "Kampala",
        "district": "Kampala",
        "occupation": "Business Owner",
        "marital_status": "Married",
        "phone": "+256700123456",
        "address": {
            "village": "Bwaise",
            "parish": "Kawaala",
            "sub_county": "Kawempe",
            "county": "Kawempe Division"
        }
    })


# ─────────────────────────────────────────────
# URA — Uganda Revenue Authority
# ─────────────────────────────────────────────

@csrf_exempt
def ura_tax_compliance(request):
    """GET /mock/ura/tax/compliance"""
    _delay()

    tin = request.GET.get('tin', '1000123456')

    # Simulate some TINs being non-compliant
    if tin.endswith('99'):
        return _json_response({
            "compliant": False,
            "tin": tin,
            "taxpayer_name": "Unknown Enterprise",
            "status": "NON_COMPLIANT",
            "reasons": [
                "Outstanding VAT returns for Q1 2026",
                "Unpaid PAYE for March 2026"
            ],
            "amount_due_ugx": 2450000,
            "last_filing_date": "2025-12-31",
            "agency": "URA"
        }, 422)

    return _json_response({
        "compliant": True,
        "tin": tin,
        "taxpayer_name": "Kato Enterprises Ltd",
        "status": "COMPLIANT",
        "tax_types": ["VAT", "PAYE", "Corporate Tax", "Local Service Tax"],
        "last_filing_date": "2026-04-30",
        "next_due_date": "2026-06-30",
        "amount_due_ugx": 0,
        "clearance_certificate": f"URA-CLR-{tin}-2026",
        "agency": "URA"
    })


@csrf_exempt
def ura_validate_tin(request):
    """POST /mock/ura/tin/validate"""
    _delay()

    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        body = {}

    tin = body.get('tin', '')

    if not tin:
        return _json_response({"valid": False, "error": "TIN is required"}, 400)

    return _json_response({
        "valid": True,
        "tin": tin,
        "registered_name": "Kato Enterprises Ltd",
        "registration_date": "2018-07-12",
        "business_nature": "Trading & Services",
        "agency": "URA"
    })


# ─────────────────────────────────────────────
# URSB — Uganda Registration Services Bureau
# ─────────────────────────────────────────────

@csrf_exempt
def ursb_business_verify(request):
    """GET /mock/ursb/business/verify"""
    _delay()

    reg_no = request.GET.get('registration_number', 'UB123456')

    if reg_no.startswith('BAD'):
        return _json_response({
            "verified": False,
            "registration_number": reg_no,
            "status": "NOT_FOUND",
            "message": "Business not registered with URSB."
        }, 404)

    return _json_response({
        "verified": True,
        "registration_number": reg_no,
        "business_name": "Kato Enterprises Ltd",
        "business_type": "Private Limited Company",
        "date_of_registration": "2018-07-12",
        "share_capital_ugx": 10000000,
        "directors": [
            {"name": "Kato John Bosco", "nin": "CM1234567890AB", "shares": 60},
            {"name": "Nakato Mary", "nin": "CM9876543210CD", "shares": 40}
        ],
        "annual_returns_status": "UP_TO_DATE",
        "agency": "URSB"
    })


@csrf_exempt
def ursb_company_search(request):
    """POST /mock/ursb/company/search"""
    _delay()

    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        body = {}

    query = body.get('query', '')

    return _json_response({
        "results_count": 2,
        "results": [
            {
                "registration_number": "UB123456",
                "business_name": "Kato Enterprises Ltd",
                "status": "ACTIVE"
            },
            {
                "registration_number": "UB654321",
                "business_name": "Kato Holdings Ltd",
                "status": "ACTIVE"
            }
        ],
        "query": query,
        "agency": "URSB"
    })


# ─────────────────────────────────────────────
# POLICE — Uganda Police Force
# ─────────────────────────────────────────────

@csrf_exempt
def police_clearance(request):
    """GET /mock/police/clearance"""
    _delay()

    nin = request.GET.get('nin', 'CM1234567890AB')

    # Simulate some people having records
    if nin.endswith('666'):
        return _json_response({
            "cleared": False,
            "nin": nin,
            "status": "FLAGGED",
            "flags": [
                {"type": "CRIMINAL_RECORD", "description": "Pending court case - theft", "date": "2025-11-10"},
                {"type": "TRAFFIC_VIOLATION", "description": "Unpaid traffic fines", "count": 3}
            ],
            "recommendation": "NOT_RECOMMENDED",
            "agency": "POLICE"
        }, 403)

    return _json_response({
        "cleared": True,
        "nin": nin,
        "status": "CLEAR",
        "criminal_record": False,
        "traffic_record": False,
        "interpol_check": "CLEAR",
        "clearance_id": f"POL-CLR-{nin}-2026",
        "issued_date": "2026-05-26",
        "expiry_date": "2027-05-26",
        "agency": "POLICE"
    })


# ─────────────────────────────────────────────
# KCCA — Kampala Capital City Authority
# ─────────────────────────────────────────────

@csrf_exempt
def kcca_license_approve(request):
    """POST /mock/kcca/license/approve"""
    _delay()

    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        body = {}

    business_name = body.get('business_name', 'Unknown Business')

    license_number = f"KCCA-BL-{random.randint(10000, 99999)}-2026"

    return _json_response({
        "approved": True,
        "license_number": license_number,
        "business_name": business_name,
        "license_type": "Business Operating License",
        "valid_from": "2026-05-26",
        "valid_until": "2027-05-26",
        "fee_paid_ugx": 150000,
        "issuing_officer": "Officer Kato",
        "department": "Trade & Commerce",
        "status": "ACTIVE",
        "qr_code_url": f"https://mock.govbridge.go.ug/verify/{license_number}",
        "agency": "KCCA"
    })


@csrf_exempt
def kcca_health_inspection(request):
    """POST /mock/kcca/health/inspect"""
    _delay()

    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        body = {}

    premises = body.get('premises_id', 'PREM-001')

    return _json_response({
        "inspection_id": f"KCCA-HI-{random.randint(1000, 9999)}",
        "premises_id": premises,
        "inspection_date": "2026-05-26",
        "inspector": "Dr. Nambi Sarah",
        "findings": {
            "sanitation": "PASS",
            "fire_safety": "PASS",
            "waste_management": "PASS",
            "building_code": "PASS"
        },
        "overall_status": "APPROVED",
        "next_inspection": "2026-11-26",
        "agency": "KCCA"
    })


# ─────────────────────────────────────────────
# HEALTH CHECK / STATUS
# ─────────────────────────────────────────────

def agency_health(request, agency_code):
    """GET /mock/health/{agency_code}/"""
    _delay()

    statuses = {
        'nira': 'ONLINE',
        'ura': 'ONLINE',
        'ursb': 'ONLINE',
        'police': 'DEGRADED',
        'kcca': 'ONLINE',
    }

    status_code = 200 if statuses.get(agency_code.lower()) != 'OFFLINE' else 503

    return _json_response({
        "agency": agency_code.upper(),
        "status": statuses.get(agency_code.lower(), 'UNKNOWN'),
        "timestamp": "2026-05-26T12:00:00Z",
        "version": "1.0.0-mock"
    }, status_code)