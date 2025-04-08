import random
from time import sleep


def random_delay(min_seconds=2, max_seconds=7):
    """Add a random delay between actions"""
    sleep_time = random.uniform(min_seconds, max_seconds)
    sleep(sleep_time)
