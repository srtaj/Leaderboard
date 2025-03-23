# leaderboard/serializers.py
from rest_framework import serializers
from .models import GameSession, Leaderboard, User, GameMode

class GameSessionSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    game_mode = serializers.SlugRelatedField(
        slug_field='name',
        queryset=GameMode.objects.all()
    )

    class Meta:
        model = GameSession
        fields = ['user_id', 'score', 'game_mode']
        extra_kwargs = {
            'game_mode': {'required': True}
        }

class LeaderboardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    game_mode = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    class Meta:
        model = Leaderboard
        fields = ['username', 'total_score', 'rank', 'game_mode']