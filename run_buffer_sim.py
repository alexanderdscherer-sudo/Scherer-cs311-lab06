"""
Lab 6: The Threaded Buffer -- starter + simulator + verification (single file).

Fix the race condition in OrderQueue below. Do NOT change anything
below the "SIMULATOR + VERIFICATION SUITE" line -- that logic (thread
spawning, trial counts, the conservation check) must stay as given.

Run: python run_buffer_sim.py
"""

import base64
import hashlib
import sys
import threading
import time
from typing import Tuple

ASSIGNMENT_ID = "LAB06"


class QueueEmptyError(Exception):
    """Custom exception raised when dequeue is called on an empty queue."""
    pass

class OrderQueue:
    def __init__(self):
        self._queue = []
        self._lock = threading.Lock()

    def enqueue(self, order):
        """Thread-safe enqueue operation."""
        with self._lock:
            self._queue.append(order)

    def dequeue(self):
        """Thread-safe dequeue operation."""
        with self._lock:
            if not self._queue:
                raise QueueEmptyError("Cannot dequeue from an empty queue.")
            return self._queue.pop(0)

    def __len__(self):
        """Thread-safe length check."""
        with self._lock:
            return len(self._queue)


# ============================== SIMULATOR + VERIFICATION SUITE ==============================
# Do not edit below this line.

NUM_PRODUCERS = 50
ORDERS_PER_PRODUCER = 10
NUM_CONSUMERS = 10
TOTAL_ORDERS = NUM_PRODUCERS * ORDERS_PER_PRODUCER
NUM_TRIALS = 20


def get_student_id() -> str:
    """Prompt for the student's USI username; baked into the Success Token
    so a copied/shared token decodes to someone else's name, not yours."""
    student_id = input("Enter your USI username (e.g. cwill): ").strip()
    while not student_id:
        student_id = input("Username cannot be blank. Enter your USI username: ").strip()
    return student_id


def generate_token(assignment_id: str, student_id: str) -> str:
    digest = hashlib.sha256(f"CS311-{assignment_id}-{student_id}-VERIFIED".encode()).hexdigest()[:16]
    raw = f"CS311|{assignment_id}|{student_id}|PASS|{digest}"
    return base64.b64encode(raw.encode()).decode()


def print_success_banner(assignment_id: str) -> None:
    student_id = get_student_id()
    token = generate_token(assignment_id, student_id)
    print("\n" + "=" * 60)
    print(f"  ALL CHECKS PASSED -- {assignment_id}")
    print(f"  STUDENT: {student_id}")
    print("  SUCCESS TOKEN (paste this into Blackboard):")
    print(f"  {token}")
    print("=" * 60 + "\n")


def _producer(queue: OrderQueue, producer_id: int) -> None:
    for i in range(ORDERS_PER_PRODUCER):
        queue.enqueue((producer_id, i))


def _consumer(queue: OrderQueue, producers_done: threading.Event, consumed: list, consumed_lock: threading.Lock, crash_flags: list, worker_index: int) -> None:
    while True:
        try:
            item = queue.dequeue()
        except QueueEmptyError:
            if producers_done.is_set() and len(queue) == 0:
                return
            continue
        except IndexError:
            crash_flags[worker_index] = True
            return
        with consumed_lock:
            consumed.append(item)


def run_single_trial() -> Tuple[int, int, bool]:
    queue = OrderQueue()
    consumed: list = []
    consumed_lock = threading.Lock()
    producers_done = threading.Event()
    crash_flags = [False] * NUM_CONSUMERS

    producer_threads = [threading.Thread(target=_producer, args=(queue, pid)) for pid in range(NUM_PRODUCERS)]
    consumer_threads = [
        threading.Thread(target=_consumer, args=(queue, producers_done, consumed, consumed_lock, crash_flags, i))
        for i in range(NUM_CONSUMERS)
    ]

    for t in consumer_threads:
        t.start()
    for t in producer_threads:
        t.start()
    for t in producer_threads:
        t.join()
    producers_done.set()
    for t in consumer_threads:
        t.join()

    num_consumed = len(consumed)
    remaining = len(queue)
    crashed = any(crash_flags)
    return num_consumed, remaining, crashed


def main() -> int:
    failures: list = []
    print(f"Running {NUM_TRIALS} trials of {NUM_PRODUCERS} producers / {NUM_CONSUMERS} consumers, {TOTAL_ORDERS} orders per trial...\n")

    for trial_num in range(1, NUM_TRIALS + 1):
        num_consumed, remaining, crashed = run_single_trial()
        conserved = (num_consumed + remaining) == TOTAL_ORDERS
        ok = conserved and not crashed
        status = "PASS" if ok else "FAIL"
        detail = ""
        if crashed:
            detail = " (a consumer thread crashed on an unhandled IndexError)"
        elif not conserved:
            detail = f" (consumed={num_consumed} remaining={remaining}, expected total {TOTAL_ORDERS})"
        print(f"  [{status}] trial {trial_num:2d}/{NUM_TRIALS}{detail}")
        if not ok:
            failures.append(f"trial {trial_num}")

    print()
    if failures:
        print(f"{len(failures)}/{NUM_TRIALS} trial(s) failed. No token issued.")
        return 1

    print_success_banner(ASSIGNMENT_ID)
    return 0


if __name__ == "__main__":
    sys.exit(main())
