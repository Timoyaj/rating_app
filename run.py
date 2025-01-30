"""
Script to run both FastAPI server and Streamlit app.
"""
import multiprocessing
import subprocess
import os
import time
import webbrowser
import signal
import sys

def run_fastapi():
    """Run FastAPI server."""
    print("Starting FastAPI server...")
    subprocess.run([
        "uvicorn",
        "api.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])

def run_streamlit():
    """Run Streamlit app."""
    print("Starting Streamlit app...")
    subprocess.run([
        "streamlit",
        "run",
        "streamlit_app/app.py",
        "--server.port", "8501"
    ])

def open_browser():
    """Open browser tabs for both applications."""
    time.sleep(2)  # Wait for servers to start
    webbrowser.open('http://localhost:8501')  # Streamlit app
    webbrowser.open('http://localhost:8000/api/docs')  # FastAPI docs

def handle_shutdown(signum, frame):
    """Handle shutdown signal."""
    print("\nShutting down servers...")
    sys.exit(0)

def main():
    """Main function to run both servers."""
    # Register signal handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Create processes
    api_process = multiprocessing.Process(target=run_fastapi)
    streamlit_process = multiprocessing.Process(target=run_streamlit)
    browser_process = multiprocessing.Process(target=open_browser)

    try:
        # Start processes
        api_process.start()
        streamlit_process.start()
        browser_process.start()

        # Wait for processes
        api_process.join()
        streamlit_process.join()
        browser_process.join()

    except KeyboardInterrupt:
        print("\nShutting down servers...")
        
        # Terminate processes
        api_process.terminate()
        streamlit_process.terminate()
        browser_process.terminate()
        
        # Wait for processes to terminate
        api_process.join()
        streamlit_process.join()
        browser_process.join()
        
        sys.exit(0)

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════╗
║     Content Rating System Server      ║
╚══════════════════════════════════════╝
    
Starting servers...
- FastAPI:   http://localhost:8000
- Streamlit: http://localhost:8501

Press Ctrl+C to stop servers
""")
    main()
