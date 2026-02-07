import time
import threading
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from typing import Optional, Callable, List


@dataclass
class IncomeConfig:
    """Configuration for income calculations"""
    annual_salary: Decimal
    currency: str = "$"
    work_hours_per_day: Decimal = Decimal("8")
    work_days_per_year: Decimal = Decimal("250")
    side_income: Decimal = Decimal("0")
    passive_income: Decimal = Decimal("0")
    
    @property
    def total_annual(self) -> Decimal:
        return self.annual_salary + self.side_income + self.passive_income
    
    @property
    def per_second(self) -> Decimal:
        total_seconds = self.work_hours_per_day * Decimal("3600") * self.work_days_per_year
        if total_seconds == 0:
            return Decimal("0")
        return (self.total_annual / total_seconds).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


class IncomeTracker:
    """Real-time income tracker with threading support"""
    
    def __init__(self, config: IncomeConfig):
        self.config = config
        self.accumulated = Decimal("0")
        self.start_time = time.time()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable] = []
        self._lock = threading.Lock()
    
    def start(self):
        self._running = True
        self.start_time = time.time()
        self._thread = threading.Thread(target=self._track_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
    
    def _track_loop(self):
        while self._running:
            elapsed = time.time() - self.start_time
            with self._lock:
                self.accumulated = Decimal(str(elapsed)) * self.config.per_second
            for callback in self._callbacks:
                try:
                    callback(self.accumulated, elapsed)
                except Exception:
                    pass
            time.sleep(0.1)
    
    def get_current(self) -> tuple[Decimal, float]:
        with self._lock:
            elapsed = time.time() - self.start_time
            current = Decimal(str(elapsed)) * self.config.per_second
            return current, elapsed
    
    def on_update(self, callback: Callable):
        self._callbacks.append(callback)
    
    def reset(self):
        with self._lock:
            self.start_time = time.time()
            self.accumulated = Decimal("0")

