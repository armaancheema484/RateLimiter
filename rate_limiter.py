import time
import threading

class RateLimiter:
    """
    A robust rate limiter using the token bucket algorithm.

    This class is now thread-safe, protecting shared data from race conditions
    when used in a multi-threaded environment.
    """

    def __init__(self, max_tokens: int, tokens_per_second: float):
        """
        Initializes the RateLimiter.

        Args:
            max_tokens (int): The maximum number of tokens the bucket can hold.
                              This also defines the maximum burst capacity.
            tokens_per_second (float): The rate at which new tokens are added
                                       to the bucket (tokens per second).
        """
        self.max_tokens = max_tokens
        self.tokens_per_second = tokens_per_second
        self.tokens = max_tokens  # Start with a full bucket
        self.last_refill = time.monotonic()  # Track the last time tokens were added
        self.lock = threading.Lock() # A lock to ensure thread-safety

    def _refill_tokens(self):
        """
        Calculates and adds new tokens to the bucket based on elapsed time.
        This method is protected by the lock.
        """
        now = time.monotonic()
        # Calculate how much time has passed since the last refill
        time_elapsed = now - self.last_refill
        # Calculate how many tokens should have been generated in that time
        tokens_to_add = time_elapsed * self.tokens_per_second
        
        # Add tokens to the bucket, but don't exceed the max capacity
        self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
        self.last_refill = now

    def allow_request(self, cost: float = 1) -> tuple[bool, float]:
        """
        Attempts to allow a request by consuming a token.
        This method is now thread-safe due to the lock.

        Returns:
            bool: True if the request is allowed, False otherwise.
        """
        # Use a 'with' statement to acquire and automatically release the lock
        with self.lock:
            self._refill_tokens()
            
            if self.tokens >= cost:
                # If there's a token, consume it and allow the request
                self.tokens -= cost
                return True, self.tokens
            else:
                # Not enough tokens, so deny the request
                wait_time = (cost - self.tokens) / self.tokens_per_second
                return False, wait_time

# --- Example Usage with Multiple Threads ---
def make_requests(limiter, thread_id, num_requests):
    """A function to simulate requests from a single thread."""
    for i in range(num_requests):
        time.sleep(0.05) # Simulate some work or a slight delay
        if limiter.allow_request():
            print(f"Thread {thread_id}: Request {i+1} ALLOWED")
        else:
            print(f"Thread {thread_id}: Request {i+1} DENIED - Rate Limited")

if __name__ == "__main__":
    # Create a rate limiter that allows 10 requests per second, with a
    # burst capacity of 30 requests.
    limiter = RateLimiter(max_tokens=30, tokens_per_second=10)
    
    # Create multiple threads to simulate concurrent requests
    num_threads = 10
    requests_per_thread = 5
    threads = []
    
    print("Starting concurrent request simulation...")
    
    for i in range(num_threads):
        thread = threading.Thread(target=make_requests, args=(limiter, i+1, requests_per_thread))
        threads.append(thread)
        thread.start()
        
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
        
    print("\nSimulation complete.")
