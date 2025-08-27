import time
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict
import psutil
import os

class MetricsTracker:
    def __init__(self):
        self.request_counts = defaultdict(int)
        self.response_times = defaultdict(list)
        self.processing_costs = []
        self.start_time = datetime.now()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
    
    def record_request(self, endpoint: str, method: str, response_time: float, status_code: int, cost: float = 0.0):
        """Record request metrics"""
        self.total_requests += 1
        
        if status_code < 400:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        # Track by endpoint
        key = f"{method} {endpoint}"
        self.request_counts[key] += 1
        self.response_times[key].append(response_time)
        
        # Keep only last 1000 response times per endpoint
        if len(self.response_times[key]) > 1000:
            self.response_times[key] = self.response_times[key][-1000:]
        
        # Track costs
        if cost > 0:
            self.processing_costs.append({
                "timestamp": datetime.now().isoformat(),
                "endpoint": endpoint,
                "cost": cost
            })
    
    def get_endpoint_stats(self, endpoint: str, method: str = "POST") -> Dict[str, Any]:
        """Get statistics for a specific endpoint"""
        key = f"{method} {endpoint}"
        times = self.response_times.get(key, [])
        
        if not times:
            return {"message": "No data available for this endpoint"}
        
        return {
            "request_count": self.request_counts[key],
            "avg_response_time": sum(times) / len(times),
            "min_response_time": min(times),
            "max_response_time": max(times),
            "recent_response_times": times[-10:]  # Last 10 requests
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system resource statistics"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
                "process_memory_mb": psutil.Process().memory_info().rss / 1024 / 1024
            }
        except:
            return {"error": "Unable to collect system stats"}
    
    def get_cost_stats(self) -> Dict[str, Any]:
        """Get cost statistics"""
        if not self.processing_costs:
            return {"total_cost": 0.0, "average_cost": 0.0, "request_count": 0}
        
        total_cost = sum(item["cost"] for item in self.processing_costs)
        avg_cost = total_cost / len(self.processing_costs)
        
        return {
            "total_cost": round(total_cost, 4),
            "average_cost": round(avg_cost, 4),
            "request_count": len(self.processing_costs),
            "recent_costs": self.processing_costs[-10:]  # Last 10 requests
        }
    
    def get_full_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics"""
        uptime = datetime.now() - self.start_time
        
        return {
            "overview": {
                "uptime_seconds": uptime.total_seconds(),
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "success_rate": (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
            },
            "endpoints": {
                key: {
                    "count": count,
                    "avg_response_time": sum(self.response_times[key]) / len(self.response_times[key]) if self.response_times[key] else 0
                }
                for key, count in self.request_counts.items()
            },
            "costs": self.get_cost_stats(),
            "system": self.get_system_stats()
        }

# Global metrics tracker
metrics_tracker = MetricsTracker()

async def metrics_middleware(request, call_next):
    """
    Middleware to track request metrics
    """
    start_time = time.time()
    
    try:
        response = await call_next(request)
        processing_time = time.time() - start_time
        
        # Record metrics
        metrics_tracker.record_request(
            endpoint=request.url.path,
            method=request.method,
            response_time=processing_time,
            status_code=response.status_code
        )
        
        # Add processing time to response headers
        response.headers["X-Processing-Time"] = str(round(processing_time, 3))
        
        return response
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        # Record failed request
        metrics_tracker.record_request(
            endpoint=request.url.path,
            method=request.method,
            response_time=processing_time,
            status_code=500
        )
        
        raise e