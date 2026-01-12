"""
Rate Limiting Decorators
Implements token bucket and fixed window rate limiting
"""
import time
import threading
from functools import wraps
from typing import Callable


class TokenBucket:
    """Token bucket rate limiter"""
    
    def __init__(self, tokens_per_minute: int):
        self.capacity = tokens_per_minute
        self.tokens = tokens_per_minute
        self.fill_rate = tokens_per_minute / 60.0  # tokens per second
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Attempt to consume tokens
        Returns True if successful, False if insufficient tokens
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Add tokens based on elapsed time
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.fill_rate
            )
            self.last_update = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def wait_for_token(self):
        """Wait until a token is available"""
        while not self.consume(1):
            time.sleep(0.1)


class RateLimiter:
    """Rate limiting manager for API calls"""
    
    _limiters: dict[str, TokenBucket] = {}
    
    @classmethod
    def register_limiter(cls, name: str, requests_per_minute: int):
        """Register a new rate limiter"""
        cls._limiters[name] = TokenBucket(requests_per_minute)
    
    @classmethod
    def get_limiter(cls, name: str) -> TokenBucket:
        """Get rate limiter by name"""
        if name not in cls._limiters:
            raise ValueError(f"Rate limiter '{name}' not registered")
        return cls._limiters[name]


def rate_limit(limiter_name: str):
    """
    Decorator for rate-limited API calls
    Usage: @rate_limit('virustotal')
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter = RateLimiter.get_limiter(limiter_name)
            limiter.wait_for_token()
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Pre-register known API rate limiters
RateLimiter.register_limiter('virustotal', requests_per_minute=4)  # 500/day ≈ 4/min
RateLimiter.register_limiter('shodan', requests_per_minute=1)  # Conservative
RateLimiter.register_limiter('censys', requests_per_minute=2)  # Conservative
RateLimiter.register_limiter('otx', requests_per_minute=10)  # No strict limit
RateLimiter.register_limiter('abuseipdb', requests_per_minute=16)  # 1000/day ≈ 16/min
