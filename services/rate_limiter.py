import time
from collections import defaultdict
from fastapi import Request, HTTPException

class InMemoryLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_history = defaultdict(list)

    async def check_limit(self, request: Request):
        xff = request.headers.get("X-Forwarded-For")
        if xff:
            ip_address = xff.split(",")[0].strip()
        else:
            ip_address = request.client.host if request.client else "127.0.0.1"

        current_time = time.time()
        
        self.request_history[ip_address] = [
            timestamp for timestamp in self.request_history[ip_address]
            if current_time - timestamp < self.window_seconds
        ]
        
        if len(self.request_history[ip_address]) >= self.max_requests:
            raise HTTPException(
                status_code=429,
                detail=f"Too many requests. Maximum {self.max_requests} attempts allowed every {self.window_seconds} seconds."
            )
            
        self.request_history[ip_address].append(current_time)