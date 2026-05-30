from django.db import models

class Agency(models.Model):
    AUTH_TYPES = [
        ('API_KEY', 'API Key'),
        ('JWT', 'JWT'),
        ('OAUTH2', 'OAuth2'),
        ('BASIC_AUTH', 'Basic Auth'),
        ('CUSTOM', 'Custom'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('OFFLINE', 'Offline'),
        ('SUSPENDED', 'Suspended'),
        ('MAINTENANCE', 'Maintenance'),
    ]

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    agency_type = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='agency_logos/', blank=True, null=True)
    base_url = models.URLField(blank=True)
    authentication_type = models.CharField(max_length=50, choices=AUTH_TYPES, default='API_KEY')
    
    # Stores API keys, client IDs, secrets, custom headers, etc.
    auth_config = models.JSONField(default=dict, blank=True, help_text="Authentication credentials/config")
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='ACTIVE')
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_agencies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Agencies'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"