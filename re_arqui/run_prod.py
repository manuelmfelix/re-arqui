"""
Script to run both Django and FastAPI servers with production settings.
This is a simplified version that runs both servers directly, similar to run.py.
"""
import os
import sys
import subprocess
import signal
import time
import threading

# Set production environment
os.environ["DJANGO_SETTINGS_MODULE"] = "re_arqui.settings_prod"

def run_django():
    """Run Django development server with production settings"""
    django_cmd = ['python', 'manage.py', 'runserver', '127.0.0.1:8000']
    process = subprocess.Popen(
        django_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    return process

def run_fastapi():
    """Run FastAPI server with uvicorn"""
    fastapi_cmd = [
        'uvicorn', 
        'project.api:app', 
        '--host', '127.0.0.1', 
        '--port', '8001',
        '--reload-dir', 'project',  # Only watch the project directory for changes
        '--log-level', 'info'  # More detailed logging
    ]
    process = subprocess.Popen(
        fastapi_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    return process

def print_output(process, prefix):
    """Print output from a process with a prefix"""
    for line in iter(process.stdout.readline, ""):
        if line:
            print(f"{prefix}: {line.strip()}")

def main():
    """Start both servers and manage their processes"""
    print("\n=== Starting RE-ARQUI Production Servers ===\n")
    
    # Start the Django server
    django_process = run_django()
    print("Django server started on http://127.0.0.1:8000")
    
    # Start the FastAPI server
    fastapi_process = run_fastapi()
    print("FastAPI server started on http://127.0.0.1:8001")
    print("FastAPI docs available at http://127.0.0.1:8001/docs")
    print("FastAPI OpenAPI schema at http://127.0.0.1:8001/openapi.json")
    
    # Set up threads to print output
    django_thread = threading.Thread(
        target=print_output,
        args=(django_process, "Django"),
        daemon=True
    )
    django_thread.start()
    
    fastapi_thread = threading.Thread(
        target=print_output,
        args=(fastapi_process, "FastAPI"),
        daemon=True
    )
    fastapi_thread.start()
    
    print("\n=== Both servers are now running ===")
    print("Access Django: http://127.0.0.1:8000")
    print("Access FastAPI: http://127.0.0.1:8001/docs")
    print("Press Ctrl+C to stop all servers")
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        print("\nShutting down servers...")
        django_process.terminate()
        fastapi_process.terminate()
        print("Servers stopped.")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Keep the script running
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main() 