from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreateDrawView, DraftView, DrawLinkView, ActiveView, CommpletedView, DraftViewset, ManageDrawView, WinnersPrizeInfo, ParticipantsView, DownloadView, SupportView


urlpatterns = [
    path('support/', SupportView.as_view(), name='support'),
    path('download/<int:draw_id>/', DownloadView.as_view(), name='download_participants'),
    path('JoinDraw/<int:draw_id>/', ParticipantsView.as_view(), name='join_draw'),
    # path('WinnerPrizeInfo/<int:pk>', WinnersPrizeInfo.as_view(), name='winner_prize_info'),
    path('draw/', CreateDrawView.as_view(), name='create_draw'),
    path('draw/<int:pk>', ManageDrawView.as_view(), name='manage_draw'),
    path('drawlink/', DrawLinkView.as_view(), name='draw_link'),
    path('drawdraft/', DraftView.as_view(), name='draft_draw'),
    path('drawdraft/<int:pk>', ManageDrawView.as_view(), name='manage_draw'),
    path('active/', ActiveView.as_view(), name='active'),
    path('completed/', CommpletedView.as_view(), name='completed'),
    path('draft/', DraftViewset.as_view(), name='draft'),
]
    