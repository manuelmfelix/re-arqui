"""
Script to run both Django and FastAPI together
"""
import os
import sys
import subprocess
import signal
import time

def run_django():
    """Run the Django development server"""
    django_process = subprocess.Popen(
        ['python', 'manage.py', 'runserver', '8000'],
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    return django_process

def run_fastapi():
    """Run the FastAPI server with uvicorn"""
    # Set environment variable for Django settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "re_arqui.settings")
    
    # Import FastAPI app after setting the environment variable
    from project.api import app
    
    import uvicorn
    
    # Run FastAPI with uvicorn in a separate process
    fastapi_process = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'project.api:app', '--host', '127.0.0.1', '--port', '8001'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    return fastapi_process

def handle_output(process, prefix):
    """Print process output with a prefix"""
    for line in iter(process.stdout.readline, ""):
        if not line:
            break
        print(f"{prefix}: {line.strip()}")

def main():
    """Main function to run both servers"""
    print("Starting Django and FastAPI servers...")
    
    # Start Django
    django_process = run_django()
    print("Django server started on http://127.0.0.1:8000")
    
    # Start FastAPI
    fastapi_process = run_fastapi()
    print("FastAPI server started on http://127.0.0.1:8001")
    
    # Function to clean up processes
    def signal_handler(sig, frame):
        print("\nShutting down servers...")
        django_process.terminate()
        fastapi_process.terminate()
        sys.exit(0)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Print Django output
    from threading import Thread
    django_thread = Thread(target=handle_output, args=(django_process, "Django"))
    django_thread.daemon = True
    django_thread.start()
    
    # Print FastAPI output 
    fastapi_thread = Thread(target=handle_output, args=(fastapi_process, "FastAPI"))
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