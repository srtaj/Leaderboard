from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from .models import GameSession, Leaderboard


@receiver(post_save, sender=GameSession)
def update_leaderboard(sender, instance, **kwargs):
    user = instance.user
    game_mode = instance.game_mode

    # Calculate total score for the user in this game mode
    total_score = GameSession.objects.filter(user=user, game_mode=game_mode).aggregate(total=Sum('score')).get('total',
                                                                                                               0) or 0

    # Update Leaderboard entry
    leaderboard_entry, created = Leaderboard.objects.update_or_create(
        user=user,
        game_mode=game_mode,
        defaults={'total_score': total_score}
    )

    # Recalculate ranks for this game mode
    entries = Leaderboard.objects.filter(game_mode=game_mode).order_by('-total_score')
    rank = 1
    prev_score = None
    for idx, entry in enumerate(entries, start=1):
        if prev_score is None:
            prev_score = entry.total_score
            entry.rank = rank
        else:
            if entry.total_score < prev_score:
                rank = idx
                prev_score = entry.total_score
            entry.rank = rank
        entry.save()