import requests
import time
from celery import shared_task
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def notify_execution_update(execution):
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"execution_{execution.id}",
            {
                "type": "execution_update",
                "data": {
                    "id": execution.id,
                    "status": execution.status,
                    "updated_at": str(execution.updated_at),
                }
            }
        )
    except Exception:
        pass


def execute_service_step(service, input_payload):
    """Execute a SERVICE type step by making HTTP call"""
    if not service:
        raise ValueError("Service step has no service endpoint configured.")

    url = service.get_full_url()
    method = service.http_method
    timeout = min(service.timeout_seconds or 30, 60)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'GovBridge-ExecutionEngine/1.0',
        **service.headers
    }

    agency_auth = service.agency.auth_config or {}
    service_auth = service.authentication_override or {}
    auth_config = {**agency_auth, **service_auth}

    if auth_config.get('api_key_header') and auth_config.get('api_key_value'):
        headers[auth_config['api_key_header']] = auth_config['api_key_value']

    kwargs = {
        'url': url,
        'headers': headers,
        'timeout': timeout,
        'allow_redirects': True,
    }

    if method in ['POST', 'PUT', 'PATCH']:
        kwargs['json'] = input_payload

    if auth_config.get('username') and auth_config.get('password'):
        kwargs['auth'] = (auth_config['username'], auth_config['password'])

    start_time = time.time()
    response = requests.request(method, **kwargs)
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    try:
        response_body = response.json()
    except ValueError:
        response_body = {'raw_text': response.text[:2000]}

    if response.status_code >= 400:
        raise Exception(f"HTTP {response.status_code}: {response.text[:500]}")

    return response_body


def evaluate_condition(step, context):
    """Basic condition evaluator"""
    conditions = step.conditions
    if not conditions or not conditions.get('rules'):
        return True

    operator = conditions.get('operator', 'AND')
    results = []

    def get_value(path, ctx):
        keys = path.split('.')
        val = ctx
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return None
        return val

    for rule in conditions['rules']:
        field = rule.get('field', '')
        op = rule.get('operator', 'eq')
        expected = rule.get('value')
        actual = get_value(field, context)

        if op == 'eq':
            results.append(actual == expected)
        elif op == 'ne':
            results.append(actual != expected)
        elif op == 'gt':
            results.append(actual is not None and actual > expected)
        elif op == 'lt':
            results.append(actual is not None and actual < expected)
        elif op == 'contains':
            results.append(actual is not None and expected in str(actual))
        elif op == 'exists':
            results.append(actual is not None)
        else:
            results.append(True)

    return all(results) if operator == 'AND' else any(results)