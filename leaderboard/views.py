from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from rest_framework.views import APIView
from django.core.cache import cache
from .models import GameSession, Leaderboard, User, GameMode
from .serializers import GameSessionSerializer, LeaderboardSerializer
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.utils.timezone import make_aware
from datetime import datetime, time
from bisect import bisect_right
from django.views.generic.base import TemplateView
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)


class SubmitScoreView(TemplateView):
    template_name = 'leaderboard/submit_score.html'

    def post(self, request, *args, **kwargs):
        serializer = GameSessionSerializer(data=request.POST)
        if serializer.is_valid():
            try:
                user_id = serializer.validated_data['user_id']
                score = serializer.validated_data['score']
                game_mode = serializer.validated_data['game_mode']

                user = get_object_or_404(User, id=user_id)

                GameSession.objects.create(
                    user=user,
                    score=score,
                    game_mode=game_mode
                )

                total_score = GameSession.objects.filter(
                    user=user, game_mode=game_mode
                ).aggregate(total_score=Sum('score'))['total_score'] or 0

                leaderboard_entry, created = Leaderboard.objects.update_or_create(
                    user=user,
                    game_mode=game_mode,
                    defaults={'total_score': total_score}
                )

                self.update_leaderboard_rank(game_mode, leaderboard_entry)
                submitted_score = {
                    'user_id': user_id,
                    'score': score,
                    'game_mode': game_mode.name
                }

                game_modes = GameMode.objects.all()
                return render(request, self.template_name, {
                    'submitted_score': submitted_score,
                    'game_modes': game_modes
                })

            except IntegrityError as e:
                logger.error(f"Database integrity error: {e}")
                return HttpResponseServerError("Database error occurred.")

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return HttpResponseServerError("User not Found")

        game_modes = GameMode.objects.all()
        return render(request, self.template_name, {'game_modes': game_modes})

    @staticmethod
    def update_leaderboard_rank(game_mode, updated_entry):
        try:
            leaderboard_entries = list(
                Leaderboard.objects.filter(game_mode=game_mode).order_by('-total_score')
            )

            existing_entry = Leaderboard.objects.get(user=updated_entry.user,
                                                     game_mode=updated_entry.game_mode)

            if existing_entry in leaderboard_entries:
                leaderboard_entries.remove(existing_entry)

            scores = [entry.total_score for entry in leaderboard_entries]
            new_position = bisect_right(scores, updated_entry.total_score, lo=0, hi=len(scores))

            leaderboard_entries.insert(len(scores) - new_position, updated_entry)

            for index in range(new_position, len(leaderboard_entries)):
                entry = leaderboard_entries[index]
                entry.rank = index + 1
                entry.save()

        except Exception as e:
            logger.error(f"Error updating leaderboard rank: {e}")

    def get(self, request, *args, **kwargs):
        try:
            game_modes = GameMode.objects.all()
            return render(request, self.template_name, {'game_modes': game_modes})
        except Exception as e:
            logger.error(f"Error loading game modes: {e}")
            return HttpResponseServerError("Failed to load game modes.")


class LeaderboardView(TemplateView):
    template_name = 'leaderboard/leaderboard.html'

    def get(self, request, *args, **kwargs):
        try:
            selected_modes = request.GET.getlist('game_modes')
            search_query = request.GET.get('search', '')
            sort_by = request.GET.get('sort_by', 'rank')
            order = request.GET.get('order', 'asc')
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')

            queryset = GameSession.objects.none()

            if selected_modes:
                game_modes = GameMode.objects.filter(name__in=selected_modes)
                filters = Q(game_mode__in=game_modes)

                if start_date:
                    start_date = make_aware(
                        datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(), time.min)
                    )
                    filters &= Q(timestamp__gte=start_date)

                if end_date:
                    end_date = make_aware(
                        datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(), time.max)
                    )
                    filters &= Q(timestamp__lte=end_date)

                queryset = GameSession.objects.filter(filters).values(
                    'user__id', 'user__username'
                ).annotate(total_score=Sum('score')).order_by('-total_score')

            if search_query:
                queryset = queryset.filter(user__username__icontains=search_query)

            leaderboard_data = [
                {
                    'rank': index + 1,
                    'username': entry['user__username'],
                    'total_score': entry['total_score']
                }
                for index, entry in enumerate(queryset)
            ]

            paginator = Paginator(leaderboard_data, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {
                'leaderboard': page_obj,
                'game_modes': GameMode.objects.all(),
                'selected_modes': selected_modes,
                'page_obj': page_obj,
                'search_query': search_query,
                'sort_by': sort_by,
                'order': order,
                'start_date': start_date,
                'end_date': end_date
            }

            return render(request, self.template_name, context)

        except Exception as e:
            logger.error(f"Error loading leaderboard: {e}")
            return HttpResponseServerError("Failed to load leaderboard.")


class PlayerRankView(TemplateView):
    template_name = 'leaderboard/player_rank.html'

    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id')
        game_mode_name = request.GET.get('game_mode', 'easy')

        try:
            game_modes = GameMode.objects.all()
            selected_mode = game_mode_name
            player_rank = None

            if user_id:
                user = get_object_or_404(User, id=user_id)
                game_mode = get_object_or_404(GameMode, name=game_mode_name)

                leaderboard_entry = Leaderboard.objects.get(user=user, game_mode=game_mode)
                serializer = LeaderboardSerializer(leaderboard_entry)
                player_rank = serializer.data

            context = {
                'game_modes': game_modes,
                'selected_mode': selected_mode,
                'player_rank': player_rank
            }
            return render(request, self.template_name, context)

        except ObjectDoesNotExist:
            return HttpResponseBadRequest("Player or game mode not found.")

        except Exception as e:
            logger.error(f"Error fetching player rank: {e}")
            return HttpResponseServerError("Failed to fetch player rank.")
