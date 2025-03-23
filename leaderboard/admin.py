# leaderboard/admin.py
from django.contrib import admin
from .models import User, GameSession, Leaderboard, GameMode

@admin.register(GameMode)
class GameModeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

admin.site.register(User)
admin.site.register(GameSession)
admin.site.register(Leaderboard)