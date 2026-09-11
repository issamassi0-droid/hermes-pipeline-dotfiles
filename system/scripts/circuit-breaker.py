#!/usr/bin/env python3
"""
Circuit Breaker + Retry with Backoff — Cabinet-Office System
Prevents cascading failures and handles transient errors.
"""
import time
import functools
import threading
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, reject requests
    HALF_OPEN = "half_open" # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker pattern for agent calls.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests are rejected immediately
    - HALF_OPEN: Testing if service recovered (allow limited requests)
    """
    
    def __init__(self, name: str, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self._lock = threading.Lock()
    
    def call(self, fn, *args, **kwargs):
        """Execute function through circuit breaker."""
        with self._lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time >= self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise Exception(f"Circuit breaker OPEN for {self.name} — too many failures")
        
        try:
            result = fn(*args, **kwargs)
            with self._lock:
                if self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
            return result
        except Exception as e:
            with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitState.OPEN
            raise
    
    def get_state(self) -> dict:
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "recovery_timeout": self.recovery_timeout
        }


def retry_with_backoff(max_attempts: int = 3, base_delay: float = 1.0, backoff_factor: float = 2.0):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts
        base_delay: Initial delay in seconds
        backoff_factor: Multiplier for each retry
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        delay = base_delay * (backoff_factor ** attempt)
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


if __name__ == "__main__":
    cb = CircuitBreaker("test", failure_threshold=3, recovery_timeout=5.0)
    
    # Test 1: Normal call
    result = cb.call(lambda: "success")
    print(f"✓ Normal call: {result}")
    
    # Test 2: Circuit opens after failures
    def failing_fn():
        raise Exception("Service down")
    
    for i in range(3):
        try:
            cb.call(failing_fn)
        except Exception as e:
            print(f"  Attempt {i+1}: {e}")
    
    print(f"  Circuit state: {cb.get_state()}")
    
    # Test 3: Circuit rejects when open
    try:
        cb.call(lambda: "should not reach")
    except Exception as e:
        print(f"✓ Circuit rejected: {e}")
    
    print("✓ Circuit breaker working")
