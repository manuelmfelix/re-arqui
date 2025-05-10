"""
Script to run both Django (with Gunicorn) and FastAPI (with Uvicorn) in production
"""
import os
import sys
import subprocess
import signal
import time
from threading import Thread

# Set production environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "re_arqui.settings_prod")

def run_django():
    """Run the Django server with Gunicorn"""
    # Gunicorn command with appropriate settings
    django_process = subprocess.Popen([
        'gunicorn',
        '--bind', '127.0.0.1:8000',
        '--workers', '3',
        '--timeout', '120',
        '--access-logfile', 'gunicorn_access.log',
        '--error-logfile', 'gunicorn_error.log',
        're_arqui.wsgi:application'
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    return django_process

def run_fastapi():
    """Run the FastAPI server with uvicorn"""
    # Import after setting the environment variable
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "re_arqui.settings_prod")
    
    # Run FastAPI with uvicorn
    fastapi_process = subprocess.Popen([
        'uvicorn',
        'project.api:app',
        '--host', '127.0.0.1',
        '--port', '8001',
        '--workers', '2',
        '--log-level', 'warning',
        '--log-file', 'uvicorn.log'
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    return fastapi_process

def handle_output(process, prefix, logfile):
    """Log process output to a file"""
    with open(logfile, 'a') as log:
        for line in iter(process.stdout.readline, ""):
            if not line:
                break
            log.write(f"{prefix}: {line}")
            log.flush()

def main():
    """Main function to run both servers"""
    print("Starting Django and FastAPI servers in production mode...")
    
    # Start Django with Gunicorn
    django_process = run_django()
    print("Django server (Gunicorn) started on http://127.0.0.1:8000")
    
    # Start FastAPI with Uvicorn
    fastapi_process = run_fastapi()
    print("FastAPI server (Uvicorn) started on http://127.0.0.1:8001")
    
    # Function to clean up processes
    def signal_handler(sig, frame):
        print("\nShutting down servers...")
        django_process.terminate()
        fastapi_process.terminate()
        sys.exit(0)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Log Django output
    django_thread = Thread(target=handle_output, args=(django_process, "Django", "django_output.log"))
    django_thread.daemon = True
    django_thread.start()
    
    # Log FastAPI output
    fastapi_thread = Thread(target=handle_output, args=(fastapi_process, "FastAPI", "fastapi_output.log"))
    fastapi_thread.daemon = True
    fastapi_thread.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main() 