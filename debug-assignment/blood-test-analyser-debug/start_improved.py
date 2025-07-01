#!/usr/bin/env python3
"""
Improved Startup Script for Blood Test Analyzer
Features enhanced error handling, performance monitoring, and automatic optimization
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('startup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ServiceManager:
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.running = True
        
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        logger.info("Checking dependencies...")
        
        required_packages = [
            'fastapi', 'uvicorn', 'sqlalchemy', 'celery', 'redis',
            'crewai', 'langchain', 'google-generativeai'
        ]
        
        # Package name mapping for import
        package_mapping = {
            'google-generativeai': 'google.generativeai'
        }
        
        missing_packages = []
        for package in required_packages:
            try:
                import_name = package_mapping.get(package, package.replace('-', '_'))
                __import__(import_name)
                logger.info(f"[OK] {package}")
            except ImportError:
                missing_packages.append(package)
                logger.error(f"[ERROR] {package} - Not installed")
        
        if missing_packages:
            logger.error(f"Missing packages: {', '.join(missing_packages)}")
            logger.info("Run: pip install -r requirements.txt")
            return False
        
        logger.info("All dependencies are installed")
        return True
    
    def check_environment(self) -> bool:
        """Check environment configuration"""
        logger.info("Checking environment configuration...")
        
        # Check if .env file exists
        if not os.path.exists('.env'):
            logger.warning(".env file not found")
            if os.path.exists('env.template'):
                logger.info("Copy env.template to .env and configure your settings")
            return False
        
        # Load and check critical environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check for SECRET_KEY
        if not os.getenv('SECRET_KEY') or os.getenv('SECRET_KEY') == 'your-secret-key-here-change-this-in-production':
            logger.warning("SECRET_KEY not configured - using default")
            os.environ['SECRET_KEY'] = 'default-secret-key-for-development-only'
        
        # Check for GEMINI_API_KEY (warn but don't fail)
        if not os.getenv('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY') == 'your-gemini-api-key-here':
            logger.warning("GEMINI_API_KEY not configured - AI features will be limited")
            logger.info("Get your API key from: https://makersuite.google.com/app/apikey")
        
        # Set default database URL if not configured
        if not os.getenv('DATABASE_URL'):
            logger.info("Using SQLite database for development")
            os.environ['DATABASE_URL'] = 'sqlite:///./blood_test_analyzer.db'
        
        logger.info("Environment configuration is valid")
        return True
    
    def start_redis(self) -> bool:
        """Start Redis server"""
        logger.info("Starting Redis server...")
        
        try:
            # Check if Redis is already running
            result = subprocess.run(['redis-cli', 'ping'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and 'PONG' in result.stdout:
                logger.info("Redis is already running")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        try:
            # Try to start Redis server
            redis_process = subprocess.Popen(
                ['redis-server'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for Redis to start
            time.sleep(2)
            
            # Check if Redis started successfully
            if redis_process.poll() is None:
                self.processes['redis'] = redis_process
                logger.info("Redis server started successfully")
                return True
            else:
                stdout, stderr = redis_process.communicate()
                logger.error(f"Redis failed to start: {stderr}")
                return False
                
        except FileNotFoundError:
            logger.error("Redis not found. Please install Redis or use Docker.")
            return False
        except Exception as e:
            logger.error(f"Error starting Redis: {e}")
            return False
    
    def start_celery_worker(self) -> bool:
        """Start Celery worker"""
        logger.info("Starting Celery worker...")
        
        try:
            celery_process = subprocess.Popen(
                ['celery', '-A', 'celery_app', 'worker', '--loglevel=info'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for Celery to start
            time.sleep(3)
            
            if celery_process.poll() is None:
                self.processes['celery'] = celery_process
                logger.info("Celery worker started successfully")
                return True
            else:
                stdout, stderr = celery_process.communicate()
                logger.error(f"Celery failed to start: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting Celery: {e}")
            return False
    
    def start_backend(self) -> bool:
        """Start FastAPI backend"""
        logger.info("Starting FastAPI backend...")
        
        try:
            backend_process = subprocess.Popen(
                ['python', 'main_optimized.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for backend to start
            time.sleep(5)
            
            if backend_process.poll() is None:
                self.processes['backend'] = backend_process
                logger.info("FastAPI backend started successfully")
                return True
            else:
                stdout, stderr = backend_process.communicate()
                logger.error(f"Backend failed to start: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting backend: {e}")
            return False
    
    def start_frontend(self) -> bool:
        """Start React frontend"""
        logger.info("Starting React frontend...")
        
        # Check if frontend directory exists
        if not os.path.exists('frontend'):
            logger.warning("Frontend directory not found")
            return False
        
        try:
            # Change to frontend directory
            os.chdir('frontend')
            
            # Check if node_modules exists
            if not os.path.exists('node_modules'):
                logger.info("Installing frontend dependencies...")
                subprocess.run(['npm', 'install'], check=True)
            
            # Start frontend
            frontend_process = subprocess.Popen(
                ['npm', 'start'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Change back to root directory
            os.chdir('..')
            
            # Wait a moment for frontend to start
            time.sleep(10)
            
            if frontend_process.poll() is None:
                self.processes['frontend'] = frontend_process
                logger.info("React frontend started successfully")
                return True
            else:
                stdout, stderr = frontend_process.communicate()
                logger.error(f"Frontend failed to start: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting frontend: {e}")
            # Change back to root directory in case of error
            os.chdir('..')
            return False
    
    def run_performance_optimization(self):
        """Run performance optimization"""
        logger.info("Running performance optimization...")
        
        try:
            from performance_optimizer import PerformanceOptimizer
            optimizer = PerformanceOptimizer()
            report = optimizer.generate_optimization_report()
            
            # Log optimization results
            metrics = report['system_metrics']
            logger.info(f"System metrics - CPU: {metrics['cpu_percent']:.1f}%, "
                       f"Memory: {metrics['memory_percent']:.1f}%")
            
            if report['warnings']:
                for warning_type, message in report['warnings'].items():
                    logger.warning(f"Performance warning: {message}")
            
            # Save report
            optimizer.save_report(report)
            
        except Exception as e:
            logger.error(f"Performance optimization failed: {e}")
    
    def monitor_services(self):
        """Monitor running services"""
        logger.info("Starting service monitoring...")
        
        while self.running:
            for service_name, process in self.processes.items():
                if process.poll() is not None:
                    logger.error(f"{service_name} has stopped unexpectedly")
                    # Restart the service
                    self.restart_service(service_name)
            
            time.sleep(30)  # Check every 30 seconds
    
    def restart_service(self, service_name: str):
        """Restart a specific service"""
        logger.info(f"Restarting {service_name}...")
        
        if service_name in self.processes:
            try:
                self.processes[service_name].terminate()
                self.processes[service_name].wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.processes[service_name].kill()
        
        # Restart based on service type
        if service_name == 'redis':
            self.start_redis()
        elif service_name == 'celery':
            self.start_celery_worker()
        elif service_name == 'backend':
            self.start_backend()
        elif service_name == 'frontend':
            self.start_frontend()
    
    def stop_all_services(self):
        """Stop all running services"""
        logger.info("Stopping all services...")
        self.running = False
        
        for service_name, process in self.processes.items():
            try:
                logger.info(f"Stopping {service_name}...")
                process.terminate()
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing {service_name}...")
                process.kill()
            except Exception as e:
                logger.error(f"Error stopping {service_name}: {e}")
    
    def start_all_services(self) -> bool:
        """Start all services"""
        logger.info("Starting Blood Test Analyzer...")
        
        # Check dependencies and environment
        if not self.check_dependencies():
            return False
        
        if not self.check_environment():
            return False
        
        # Run performance optimization
        self.run_performance_optimization()
        
        # Start services
        services = [
            ('Redis', self.start_redis),
            ('Celery', self.start_celery_worker),
            ('Backend', self.start_backend),
            ('Frontend', self.start_frontend)
        ]
        
        failed_services = []
        for service_name, start_func in services:
            if not start_func():
                failed_services.append(service_name)
        
        if failed_services:
            logger.error(f"Failed to start services: {', '.join(failed_services)}")
            return False
        
        logger.info("All services started successfully!")
        logger.info("Frontend: http://localhost:3000")
        logger.info("Backend API: http://localhost:8000")
        logger.info("API Docs: http://localhost:8000/docs")
        
        return True

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Received shutdown signal...")
    if hasattr(signal_handler, 'service_manager'):
        signal_handler.service_manager.stop_all_services()
    sys.exit(0)

def main():
    """Main function"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create service manager
    service_manager = ServiceManager()
    signal_handler.service_manager = service_manager
    
    # Start all services
    if service_manager.start_all_services():
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=service_manager.monitor_services)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        logger.info("Blood Test Analyzer is running!")
        logger.info("Press Ctrl+C to stop all services")
        
        # Keep main thread alive
        try:
            while service_manager.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        logger.error("Failed to start services")
        sys.exit(1)

if __name__ == "__main__":
    main() 