import json
from django.utils.deprecation import MiddlewareMixin
from .utils import log_action


class AuditMiddleware(MiddlewareMixin):
    """Logs every API request automatically, but skips routine navigation noise."""
    
    # Never log these paths
    SKIP_PATHS = [
        '/admin/', '/static/', '/media/', '/ws/', '/favicon.ico',
        '/api/auditlogs/',          # Don't log the audit logs themselves
        '/api/auth/',          # Auth is too noisy, logged via signals instead
        '/api/collaboration/',  # Chat is too noisy, logged via signals instead
    ]
    
    # Skip routine GET list requests (page navigation noise)
    # These are just loading data for React pages, not real "actions"
    NOISY_LIST_PATHS = [
        '/api/services/',
        '/api/workflows/',
        '/api/agencies/',
        '/api/executions/',
        '/api/accounts/',
        '/api/collaboration/users/',
    ]
    
    # Always log these even if GET (they are real actions)
    ACTION_KEYWORDS = [
        'execute', 'verify', 'submit', 'complete', 'reject', 'cancel',
        'preview', 'test', 'publish', 'run', 'check', 'validate',
        'login', 'logout', 'token', 'refresh',
    ]

    def process_request(self, request):
        request._audit_body = {}
        if request.content_type == 'application/json':
            try:
                request._audit_body = json.loads(request.body.decode('utf-8'))
            except:
                pass
        return None

    def process_response(self, request, response):
        path = request.path
        
        # Skip if in skip list
        if any(path.startswith(skip) for skip in self.SKIP_PATHS):
            return response
        
        method = request.method
        
        # Skip routine GET list requests (navigation noise)
        if method == 'GET':
            # Check if it's a list endpoint (ends with / and no specific ID)
            is_list = path.endswith('/')
            has_id = any(part.isdigit() for part in path.split('/'))
            
            if is_list and not has_id:
                # If it's a known noisy list path, skip it
                if any(path.startswith(noisy) for noisy in self.NOISY_LIST_PATHS):
                    return response
            
            # If it's a detail GET (has ID), still log it as READ
            # unless it's a known noisy path
        
        # Determine action type
        action = 'READ'
        if method in ['POST']:
            action = 'CREATE'
        elif method in ['PUT', 'PATCH']:
            action = 'UPDATE'
        elif method in ['DELETE']:
            action = 'DELETE'
        
        # Check if URL contains action keywords (e.g., /execute/, /verify/)
        url_lower = path.lower()
        if any(kw in url_lower for kw in ['login', 'token', 'refresh']):
            action = 'LOGIN' if response.status_code < 400 else 'LOGIN_FAILED'
        elif 'execute' in url_lower:
            action = 'API_CALL'
        elif any(kw in url_lower for kw in self.ACTION_KEYWORDS):
            action = 'API_CALL'
        
        # Determine status
        status = 'SUCCESS' if response.status_code < 400 else 'FAILED'
        
        # Extract entity type from URL
        entity_type = self._extract_entity(path)
        
        # Get user
        user = getattr(request, 'user', None)
        if user and not getattr(user, 'is_authenticated', False):
            user = None
        
        # Build description
        desc = f"{method} {path}"
        if response.status_code >= 400:
            try:
                err = json.loads(response.content.decode('utf-8', errors='ignore'))
                err_msg = err.get('detail', '') or str(err)
                desc += f" | Error {response.status_code}: {err_msg[:100]}"
            except:
                desc += f" | Error {response.status_code}"
        
        # Log it
        log_action(
            user=user,
            action=action,
            status=status,
            entity_type=entity_type,
            url=request.build_absolute_uri(),
            http_method=method,
            ip_address=self._get_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            status_code=response.status_code,
            description=desc
        )
        
        return response
    
    def _extract_entity(self, path):
        mapping = {
            '/services/': 'ServiceEndpoint',
            '/workflows/': 'Workflow',
            '/executions/': 'WorkflowExecution',
            '/agencies/': 'Agency',
            '/accounts/': 'User',
            '/auth/': 'Authentication',
            '/token/': 'Authentication',
            '/mock/': 'ExternalAPI',
            '/collaboration/': 'Collaboration',
        }
        for prefix, name in mapping.items():
            if prefix in path:
                return name
        return 'Unknown'
    
    def _get_ip(self, request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')