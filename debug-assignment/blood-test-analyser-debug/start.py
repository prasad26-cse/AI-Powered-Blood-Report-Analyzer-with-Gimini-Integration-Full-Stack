#!/usr/bin/env python3
"""
BloodReport AI Start Script
Launches all services for the application.
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def start_service(self, command, name, cwd=None):
        """Start a service in a separate process."""
        print(f"🚀 Starting {name}...")
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append((process, name))
            print(f"✅ {name} started (PID: {process.pid})")
            return process
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            return None
    
    def stop_all(self):
        """Stop all running processes."""
        print("\n🛑 Stopping all services...")
        self.running = False
        
        for process, name in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️  {name} force killed")
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")
    
    def monitor_processes(self):
        """Monitor running processes and restart if needed."""
        while self.running:
            for i, (process, name) in enumerate(self.processes):
                if process.poll() is not None:
                    print(f"⚠️  {name} stopped unexpectedly")
                    if self.running:
                        print(f"🔄 Restarting {name}...")
                        # Restart the process
                        new_process = self.start_service(
                            self.get_command_for_service(name),
                            name,
                            self.get_cwd_for_service(name)
                        )
                        if new_process:
                            self.processes[i] = (new_process, name)
            time.sleep(5)
    
    def get_command_for_service(self, name):
        """Get the command for a specific service."""
        commands = {
            "Backend": "uvicorn main:app --reload --host 0.0.0.0 --port 8000",
            "Celery": "celery -A celery_app worker --loglevel=info",
            "Frontend": "npm start"
        }
        return commands.get(name, "")
    
    def get_cwd_for_service(self, name):
        """Get the working directory for a specific service."""
        if name == "Frontend":
            return "frontend"
        return "."

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    print("\n🛑 Received shutdown signal...")
    if hasattr(signal_handler, 'manager'):
        signal_handler.manager.stop_all()
    sys.exit(0)

def check_dependencies():
    """Check if required services are available."""
    print("🔍 Checking dependencies...")
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("❌ .env file not found. Please run setup.py first.")
        return False
    
    # Check if frontend directory exists
    if not Path("frontend").exists():
        print("❌ Frontend directory not found.")
        return False
    
    print("✅ Dependencies check passed")
    return True

def main():
    """Main function to start all services."""
    print("🚀 BloodReport AI - Starting Services")
    print("="*50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create service manager
    manager = ServiceManager()
    signal_handler.manager = manager
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start services
        manager.start_service(
            "uvicorn main:app --reload --host 0.0.0.0 --port 8000",
            "Backend"
        )
        
        time.sleep(2)  # Give backend time to start
        
        manager.start_service(
            "celery -A celery_app worker --loglevel=info",
            "Celery"
        )
        
        time.sleep(2)  # Give celery time to start
        
        manager.start_service(
            "npm start",
            "Frontend",
            "frontend"
        )
        
        print("\n🎉 All services started successfully!")
        print("="*50)
        print("📱 Frontend: http://localhost:3000")
        print("🔧 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("="*50)
        print("Press Ctrl+C to stop all services")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=manager.monitor_processes)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Keep main thread alive
        while manager.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Keyboard interrupt received...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        manager.stop_all()

if __name__ == "__main__":
    main() 