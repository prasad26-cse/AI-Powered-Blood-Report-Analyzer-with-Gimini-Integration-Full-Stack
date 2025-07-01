#!/usr/bin/env python3
"""
Performance Optimizer for Blood Test Analyzer
Monitors and optimizes system performance
"""

import os
import psutil
import time
import logging
from typing import Dict, Any, Optional
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    def __init__(self):
        self.metrics = {}
        self.start_time = time.time()
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'memory_used_gb': memory.used / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3),
                'uptime_seconds': time.time() - self.start_time
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def check_performance_thresholds(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """Check if performance metrics exceed thresholds"""
        warnings = {}
        
        if metrics.get('cpu_percent', 0) > 80:
            warnings['cpu'] = f"High CPU usage: {metrics['cpu_percent']}%"
        
        if metrics.get('memory_percent', 0) > 85:
            warnings['memory'] = f"High memory usage: {metrics['memory_percent']}%"
        
        if metrics.get('disk_percent', 0) > 90:
            warnings['disk'] = f"Low disk space: {100 - metrics['disk_percent']}% free"
        
        return warnings
    
    def optimize_pdf_processing(self) -> Dict[str, Any]:
        """Optimize PDF processing settings"""
        cpu_count = os.cpu_count() or 1
        optimizations = {
            'max_workers': min(4, cpu_count),
            'chunk_size': 1024 * 1024,  # 1MB chunks
            'timeout': 30,
            'retry_attempts': 3
        }
        
        # Adjust based on available memory
        try:
            memory_gb = psutil.virtual_memory().total / (1024**3)
            if memory_gb < 4:
                optimizations['max_workers'] = 2
                optimizations['chunk_size'] = 512 * 1024  # 512KB chunks
            elif memory_gb > 16:
                optimizations['max_workers'] = 8
                optimizations['chunk_size'] = 2 * 1024 * 1024  # 2MB chunks
        except Exception as e:
            logger.warning(f"Could not optimize based on memory: {e}")
        
        return optimizations
    
    def optimize_database_settings(self) -> Dict[str, Any]:
        """Optimize database connection settings"""
        cpu_count = os.cpu_count() or 1
        return {
            'pool_size': min(10, cpu_count * 2),
            'max_overflow': 20,
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'echo': False
        }
    
    def optimize_celery_settings(self) -> Dict[str, Any]:
        """Optimize Celery worker settings"""
        cpu_count = os.cpu_count() or 1
        
        return {
            'worker_concurrency': cpu_count,
            'worker_prefetch_multiplier': 1,
            'task_acks_late': True,
            'task_time_limit': 30 * 60,
            'task_soft_time_limit': 25 * 60,
            'worker_max_tasks_per_child': 1000
        }
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        metrics = self.get_system_metrics()
        warnings = self.check_performance_thresholds(metrics)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': metrics,
            'warnings': warnings,
            'optimizations': {
                'pdf_processing': self.optimize_pdf_processing(),
                'database': self.optimize_database_settings(),
                'celery': self.optimize_celery_settings()
            },
            'recommendations': []
        }
        
        # Generate recommendations
        if warnings.get('cpu'):
            report['recommendations'].append("Consider reducing concurrent PDF processing tasks")
        
        if warnings.get('memory'):
            report['recommendations'].append("Consider implementing memory cleanup in PDF processing")
        
        if warnings.get('disk'):
            report['recommendations'].append("Consider implementing automatic cleanup of old reports")
        
        if metrics.get('cpu_percent', 0) < 30 and metrics.get('memory_percent', 0) < 50:
            report['recommendations'].append("System has capacity for increased concurrent processing")
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None):
        """Save optimization report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Performance report saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving performance report: {e}")
    
    def monitor_performance(self, duration_seconds: int = 300, interval_seconds: int = 30):
        """Monitor performance for a specified duration"""
        logger.info(f"Starting performance monitoring for {duration_seconds} seconds...")
        
        start_time = time.time()
        reports = []
        
        while time.time() - start_time < duration_seconds:
            report = self.generate_optimization_report()
            reports.append(report)
            
            # Log warnings
            for warning_type, message in report['warnings'].items():
                logger.warning(f"Performance warning: {message}")
            
            time.sleep(interval_seconds)
        
        # Generate summary
        if reports:
            summary = {
                'monitoring_duration': duration_seconds,
                'total_reports': len(reports),
                'average_cpu': sum(r['system_metrics']['cpu_percent'] for r in reports) / len(reports),
                'average_memory': sum(r['system_metrics']['memory_percent'] for r in reports) / len(reports),
                'total_warnings': sum(len(r['warnings']) for r in reports)
            }
        else:
            summary = {
                'monitoring_duration': duration_seconds,
                'total_reports': 0,
                'average_cpu': 0,
                'average_memory': 0,
                'total_warnings': 0
            }
        
        logger.info(f"Performance monitoring completed. Summary: {summary}")
        return reports, summary

def main():
    """Main function to run performance optimization"""
    optimizer = PerformanceOptimizer()
    
    # Generate current optimization report
    report = optimizer.generate_optimization_report()
    
    print("Performance Optimization Report")
    print("=" * 50)
    
    # Display system metrics
    metrics = report['system_metrics']
    print(f"CPU Usage: {metrics['cpu_percent']:.1f}%")
    print(f"Memory Usage: {metrics['memory_percent']:.1f}%")
    print(f"Disk Usage: {metrics['disk_percent']:.1f}%")
    print(f"Uptime: {metrics['uptime_seconds']:.0f} seconds")
    
    # Display warnings
    if report['warnings']:
        print("\nPerformance Warnings:")
        for warning_type, message in report['warnings'].items():
            print(f"  - {message}")
    else:
        print("\nNo performance warnings")
    
    # Display recommendations
    if report['recommendations']:
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  - {rec}")
    
    # Save report
    optimizer.save_report(report)
    
    # Display optimizations
    print("\nOptimized Settings:")
    for category, settings in report['optimizations'].items():
        print(f"\n{category.title()}:")
        for key, value in settings.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main() 