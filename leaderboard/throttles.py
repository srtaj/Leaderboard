# leaderboard/throttles.py
from rest_framework.throttling import UserRateThrottle

class BurstThrottle(UserRateThrottle):
    scope = 'burst'