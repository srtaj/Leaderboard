from django.urls import path
from .views import SubmitScoreView, LeaderboardView, PlayerRankView

urlpatterns = [
    path('leaderboard/submit/', SubmitScoreView.as_view(), name='submit_score'),
    path('leaderboard/top/', LeaderboardView.as_view(), name='leaderboard'),
    path('leaderboard/rank/', PlayerRankView.as_view(), name='player_rank'),
]
