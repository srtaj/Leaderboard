# leaderboard/models.py
from django.db import models

class GameMode(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    join_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)
class GameSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    game_mode = models.ForeignKey(GameMode, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class Leaderboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)
    game_mode = models.ForeignKey(GameMode, on_delete=models.CASCADE)
    rank = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'game_mode')