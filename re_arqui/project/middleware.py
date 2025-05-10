import os
import django
from django.conf import settings
from django.core.handlers.wsgi import WSGIHandler
from django.http import HttpResponse
import logging
import socket
import errno

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "re_arqui.settings")
django.setup()

# Import the FastAPI app
from project.api import app as fastapi_app

from asgiref.sync import sync_to_async
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger('django')

class DjangoMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.django_app = WSGIHandler()
        self.mount_path = getattr(settings, "FASTAPI_MOUNT_PATH", "/api")

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # If the path starts with the mount path, use FastAPI
        if path.startswith(self.mount_path):
            response = await call_next(request)
            return response
        
        # Otherwise, use Django
        return await self.handle_django(request)
    
    @sync_to_async
    def handle_django(self, request: Request):
        # Convert FastAPI request to Django request
        scope = request.scope
        
        # Handle Django request
        django_response = HttpResponse("Django Response", content_type="text/plain")
        
        # This is a simplified example - in a real implementation, you would
        # need to properly convert the request and get a real Django response
        
        return django_response

# Add middleware to FastAPI
fastapi_app.add_middleware(DjangoMiddleware)

class BrokenPipeErrorMiddleware:
    """
    Middleware to handle broken pipe errors gracefully.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # Check if the exception is a broken pipe error
        if isinstance(exception, (BrokenPipeError, ConnectionResetError)):
            logger.info(f"Handled {type(exception).__name__} gracefully: {str(exception)}")
            return HttpResponse("Connection closed")
        
        # Check for socket errors
        if isinstance(exception, socket.error) and exception.errno in (
            errno.EPIPE,  # Broken pipe
            errno.ECONNRESET,  # Connection reset by peer
        ):
            logger.info(f"Handled socket error gracefully: {str(exception)}")
            return HttpResponse("Connection closed")
        
        return None  # Let other middleware handle other exceptions 