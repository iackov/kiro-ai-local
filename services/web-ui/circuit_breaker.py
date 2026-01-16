"""
Circuit Breaker pattern for resilient service calls
"""
import time
from enum import Enum
from typing import Dict, Callable, Any
from collections import defaultdict

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """Circuit breaker for service resilience"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout  # seconds to wait before trying again
        self.success_threshold = success_threshold
        
        self.states: Dict[str, CircuitState] = defaultdict(lambda: CircuitState.CLOSED)
        self.failure_counts: Dict[str, int] = defaultdict(int)
        self.success_counts: Dict[str, int] = defaultdict(int)
        self.last_failure_time: Dict[str, float] = {}
    
    def call(self, service: str, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        state = self.states[service]
        
        # If circuit is OPEN, check if timeout passed
        if state == CircuitState.OPEN:
            if time.time() - self.last_failure_time[service] > self.timeout:
                # Try half-open
                self.states[service] = CircuitState.HALF_OPEN
                self.success_counts[service] = 0
            else:
                # Still open, reject immediately
                raise CircuitBreakerOpenError(f"Circuit breaker open for {service}")
        
        # Try to execute
        try:
            result = func(*args, **kwargs)
            self._on_success(service)
            return result
        except Exception as e:
            self._on_failure(service)
            raise e
    
    def _on_success(self, service: str):
        """Handle successful call"""
        state = self.states[service]
        
        if state == CircuitState.HALF_OPEN:
            self.success_counts[service] += 1
            if self.success_counts[service] >= self.success_threshold:
                # Service recovered, close circuit
                self.states[service] = CircuitState.CLOSED
                self.failure_counts[service] = 0
        else:
            # Reset failure count on success
            self.failure_counts[service] = 0
    
    def _on_failure(self, service: str):
        """Handle failed call"""
        self.failure_counts[service] += 1
        self.last_failure_time[service] = time.time()
        
        if self.failure_counts[service] >= self.failure_threshold:
            # Open circuit
            self.states[service] = CircuitState.OPEN
    
    def get_state(self, service: str) -> CircuitState:
        """Get current circuit state"""
        return self.states[service]
    
    def reset(self, service: str):
        """Manually reset circuit"""
        self.states[service] = CircuitState.CLOSED
        self.failure_counts[service] = 0
        self.success_counts[service] = 0

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass

# Global circuit breaker instance
circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=30,
    success_threshold=2
)
