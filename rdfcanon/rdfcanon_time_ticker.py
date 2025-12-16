import time


class RDFCanonTimeTicker:
    def __init__(self, max_time: int):
        self.current_time = 0

        if max_time < 0:
            raise ValueError("max_time must be non-negative")

        self.max_time = max_time

    def tick(self):
        current_time_ms = time.time_ns() / 1000000

        if self.current_time == 0:
            self.current_time = current_time_ms
            return

        time_passed = current_time_ms - self.current_time

        if time_passed >= self.max_time:
            raise TimeoutError("Operation timed out")
