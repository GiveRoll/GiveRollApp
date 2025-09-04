from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreateDrawView, DraftView, DrawLinkView, ActiveView, CommpletedView, DraftViewset, ManageDrawView


urlpatterns = [
    path('draw/', CreateDrawView.as_view(), name='create_draw'),
    path('draw/<int:pk>', ManageDrawView.as_view(), name='manage_draw'),
    path('drawlink/', DrawLinkView.as_view(), name='draw_link'),
    path('drawdraft/', DraftView.as_view(), name='draft_draw'),
    path('drawdraft/<int:pk>', ManageDrawView.as_view(), name='manage_draw'),
    path('active/', ActiveView.as_view(), name='active'),
    path('completed/', CommpletedView.as_view(), name='completed'),
    path('draft/', DraftViewset.as_view(), name='draft'),
]
    