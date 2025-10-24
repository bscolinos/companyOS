#!/usr/bin/env python3
"""
CompanyOS Development Runner
Run both frontend and backend services with a single command.

Usage: python run.py
"""

import subprocess
import os
import sys
import signal
import time
import socket
from pathlib import Path
from threading import Thread
from typing import List

class ServiceRunner:
    """Manages running multiple services"""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.root_dir = Path(__file__).parent
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "frontend"
    
    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is already in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    def kill_process_on_port(self, port: int):
        """Kill process using the specified port"""
        try:
            # Find process using the port
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    print(f"Killing process {pid} on port {port}")
                    subprocess.run(["kill", "-9", pid])
                time.sleep(1)
        except Exception as e:
            print(f"Error killing process on port {port}: {e}")
        
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        print("Checking prerequisites...")
        
        # Check directories
        if not self.backend_dir.exists():
            print(f"Error: Backend directory not found: {self.backend_dir}")
            return False
        
        if not self.frontend_dir.exists():
            print(f"Error: Frontend directory not found: {self.frontend_dir}")
            return False
        
        # Check for npm
        try:
            subprocess.check_output(["npm", "--version"], stderr=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: npm not found. Please install Node.js and npm")
            return False
        
        # Check and kill processes on ports if needed
        if self.is_port_in_use(8000):
            print("Port 8000 is in use. Stopping existing process...")
            self.kill_process_on_port(8000)
        
        if self.is_port_in_use(3000):
            print("Port 3000 is in use. Stopping existing process...")
            self.kill_process_on_port(3000)
        
        return True
    
    def stream_output(self, process: subprocess.Popen, prefix: str):
        """Stream process output with prefix"""
        if process.stdout is None:
            return
            
        for line in iter(process.stdout.readline, b''):
            if line:
                try:
                    decoded_line = line.decode('utf-8').rstrip()
                    print(f"{prefix} {decoded_line}")
                except UnicodeDecodeError:
                    pass
    
    def start_backend(self):
        """Start the FastAPI backend"""
        print("Starting backend server...")
        
        backend_env = os.environ.copy()
        
        # Check if virtual environment exists
        venv_python = self.backend_dir / "venv" / "bin" / "python"
        if venv_python.exists():
            python_cmd = str(venv_python)
        else:
            python_cmd = sys.executable
        
        # Start uvicorn
        cmd = [
            python_cmd, "-m", "uvicorn",
            "main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(self.backend_dir),
                env=backend_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            self.processes.append(process)
            
            # Start output streaming in a separate thread
            thread = Thread(
                target=self.stream_output,
                args=(process, "[BACKEND]"),
                daemon=True
            )
            thread.start()
            
            print("Backend started: http://localhost:8000")
            return process
            
        except Exception as e:
            print(f"Failed to start backend: {e}")
            return None
    
    def start_frontend(self):
        """Start the React frontend"""
        print("Starting frontend server...")
        
        # Check if node_modules exists
        node_modules = self.frontend_dir / "node_modules"
        if not node_modules.exists():
            print("Installing npm dependencies...")
            install_process = subprocess.Popen(
                ["npm", "install"],
                cwd=str(self.frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            install_process.wait()
            if install_process.returncode != 0:
                print("Failed to install dependencies")
                return None
        
        # Start React development server
        frontend_env = os.environ.copy()
        frontend_env["BROWSER"] = "none"  # Don't auto-open browser
        
        cmd = ["npm", "start"]
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(self.frontend_dir),
                env=frontend_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            self.processes.append(process)
            
            # Start output streaming in a separate thread
            thread = Thread(
                target=self.stream_output,
                args=(process, "[FRONTEND]"),
                daemon=True
            )
            thread.start()
            
            print("Frontend started: http://localhost:3000")
            return process
            
        except Exception as e:
            print(f"Failed to start frontend: {e}")
            return None
    
    def cleanup(self, signum=None, frame=None):
        """Clean up and terminate all processes"""
        print("\nShutting down services...")
        
        for process in self.processes:
            try:
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
            except Exception as e:
                print(f"Error terminating process: {e}")
        
        print("All services stopped")
        sys.exit(0)
    
    def run(self):
        """Main run method"""
        print("CompanyOS Dev Server")
        print("=" * 50)
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("Prerequisites check failed.")
            sys.exit(1)
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
        
        # Start services
        print("\nStarting services...\n")
        
        backend_process = self.start_backend()
        if not backend_process:
            print("Failed to start backend. Exiting.")
            sys.exit(1)
        
        # Give backend a moment to start
        time.sleep(2)
        
        frontend_process = self.start_frontend()
        if not frontend_process:
            print("Failed to start frontend. Stopping backend and exiting.")
            self.cleanup()
            sys.exit(1)
        
        # Print success message
        print("\n" + "="*50)
        print("Services running:")
        print("  Backend:  http://localhost:8000")
        print("  API Docs: http://localhost:8000/docs")
        print("  Frontend: http://localhost:3000")
        print("\nPress Ctrl+C to stop\n")
        print("="*50 + "\n")
        
        # Keep the main thread alive
        try:
            while True:
                # Check if any process has died
                for i, process in enumerate(self.processes):
                    if process.poll() is not None:
                        service_name = "Backend" if i == 0 else "Frontend"
                        print(f"\n{service_name} process died unexpectedly!")
                        self.cleanup()
                        sys.exit(1)
                time.sleep(1)
        except KeyboardInterrupt:
            self.cleanup()

def main():
    """Entry point"""
    runner = ServiceRunner()
    runner.run()

if __name__ == "__main__":
    main()

