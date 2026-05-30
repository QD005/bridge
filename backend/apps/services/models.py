from django.db import models


class ServiceEndpoint(models.Model):
    HTTP_METHODS = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    ]

    HEALTH_STATUS = [
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
        ('DEGRADED', 'Degraded'),
        ('MAINTENANCE', 'Maintenance'),
    ]

    agency = models.ForeignKey(
        'agencies.Agency',
        on_delete=models.CASCADE,
        related_name='services'
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    endpoint_url = models.URLField(help_text="Full URL or relative path appended to agency base_url")
    http_method = models.CharField(max_length=10, choices=HTTP_METHODS, default='GET')

    # JSON fields for configuration
    headers = models.JSONField(default=dict, blank=True, help_text="Default headers as key-value pairs")
    response_schema = models.JSONField(default=dict, blank=True, help_text="JSON Schema for response validation")

    # Authentication override for this specific service
    authentication_override = models.JSONField(
        default=dict, blank=True,
        help_text="Override agency auth for this endpoint (e.g., different API key)"
    )

    timeout_seconds = models.PositiveIntegerField(default=30)
    retry_count = models.PositiveIntegerField(default=3)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='ACTIVE')
    health_status = models.CharField(max_length=50, choices=HEALTH_STATUS, default='OFFLINE')
    version = models.CharField(max_length=50, blank=True, default='v1')

    rate_limits = models.JSONField(
        default=dict, blank=True,
        help_text="Rate limit config: {'requests_per_minute': 60, 'burst': 10}"
    )

    # LEGACY: Keep for backward compatibility — will be replaced by ServiceField model
    field_definitions = models.JSONField(
        default=list, blank=True,
        help_text="""Dynamic form fields: [
            {'name': 'nin', 'label': 'National ID Number', 'type': 'text', 'required': true,
             'placeholder': 'CM1234567890AB', 'help_text': '14-character NIN',
             'validation_regex': '^CM[0-9]{10}[A-Z]{2}$', 'min_length': 14, 'max_length': 14,
             'order': 1, 'location': 'query', 'is_sensitive': false, 'options': []}
        ]"""
    )

    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_services'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Service Endpoint'
        verbose_name_plural = 'Service Endpoints'

    def __str__(self):
        return f"{self.name} ({self.agency.code})"

    def get_full_url(self):
        """Return full URL by combining agency base_url + endpoint_url if relative"""
        if self.endpoint_url.startswith('http'):
            return self.endpoint_url
        base = self.agency.base_url.rstrip('/') if self.agency.base_url else ''
        path = self.endpoint_url.lstrip('/')
        return f"{base}/{path}" if base else self.endpoint_url

    def get_fields(self):
        """Return field definitions — prefer ServiceField model, fallback to JSON"""
        fields = list(self.service_fields.all().values(
            'name', 'label', 'field_type', 'required', 'placeholder',
            'help_text', 'validation_regex', 'min_length', 'max_length',
            'order', 'location', 'is_sensitive', 'options', 'default_value'
        ))
        if fields:
            return fields
        # Fallback to legacy JSON field_definitions
        return self.field_definitions or []

    def build_request(self, raw_values):
        """
        Build the actual HTTP request from raw user values.
        Returns: (method, url, headers, body, query_params)
        """
        import re

        url = self.get_full_url()
        method = self.http_method
        headers = dict(self.headers or {})
        body = {}
        query_params = {}

        fields = self.get_fields()

        for field_def in fields:
            field_name = field_def.get('name')
            location = field_def.get('location', 'query' if method == 'GET' else 'body')
            value = raw_values.get(field_name)

            # Skip empty optional fields
            if not value and not field_def.get('required'):
                continue

            if location == 'path':
                # Replace {field_name} in URL
                url = url.replace(f"{{{field_name}}}", str(value))
            elif location == 'header':
                headers[field_name.replace('_', '-').title()] = str(value)
            elif location == 'query':
                query_params[field_name] = value
            else:  # body
                body[field_name] = value

        # Add agency auth headers
        agency_auth = self.agency.auth_config or {}
        service_auth = self.authentication_override or {}
        auth_config = {**agency_auth, **service_auth}

        if auth_config.get('api_key_header') and auth_config.get('api_key_value'):
            headers[auth_config['api_key_header']] = auth_config['api_key_value']

        return {
            'method': method,
            'url': url,
            'headers': headers,
            'body': body if body else None,
            'query_params': query_params if query_params else None,
        }

    def preview_request(self, raw_values):
        """Return a human-readable preview of the request (no actual HTTP call)"""
        req = self.build_request(raw_values)

        preview = f"{req['method']} {req['url']}"

        if req['query_params']:
            q = '&'.join([f"{k}={v}" for k, v in req['query_params'].items()])
            preview += f"?{q}"

        if req['headers']:
            preview += "\n\nHEADERS:\n"
            for k, v in req['headers'].items():
                preview += f"  {k}: {v}\n"

        if req['body']:
            import json
            preview += f"\nBODY:\n{json.dumps(req['body'], indent=2)}"

        return preview


class ServiceField(models.Model):
    """Dedicated model for service input fields — the proper way"""
    LOCATION_CHOICES = [
        ('query', 'Query Parameter'),
        ('body', 'Request Body'),
        ('header', 'HTTP Header'),
        ('path', 'URL Path Segment'),
    ]

    TYPE_CHOICES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('email', 'Email'),
        ('date', 'Date'),
        ('select', 'Select / Dropdown'),
        ('textarea', 'Textarea'),
        ('file', 'File Upload'),
        ('checkbox', 'Checkbox'),
        ('phone', 'Phone'),
        ('password', 'Password'),
    ]

    service = models.ForeignKey(
        ServiceEndpoint,
        on_delete=models.CASCADE,
        related_name='service_fields'
    )

    name = models.CharField(max_length=100, help_text="Technical key, e.g. 'nin'")
    label = models.CharField(max_length=255, help_text="Human readable label")
    field_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='text')
    required = models.BooleanField(default=False)
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES, default='query')

    placeholder = models.CharField(max_length=255, blank=True)
    help_text = models.TextField(blank=True, help_text="Shown below the field in the UI")
    default_value = models.CharField(max_length=255, blank=True)

    validation_regex = models.CharField(max_length=500, blank=True)
    min_length = models.PositiveIntegerField(null=True, blank=True)
    max_length = models.PositiveIntegerField(null=True, blank=True)

    # For select/dropdown fields
    options = models.JSONField(default=list, blank=True, help_text="['Option 1', 'Option 2']")

    order = models.PositiveIntegerField(default=0)
    is_sensitive = models.BooleanField(default=False, help_text="Mask value in logs")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        unique_together = ['service', 'name']

    def __str__(self):
        return f"{self.name} ({self.location}) — {self.service.name}"