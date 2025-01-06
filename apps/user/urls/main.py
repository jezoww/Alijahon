from django.urls import path

from apps.user.views import IndexListView, CompetitionListView, LikeDislikeView, WithdrawFormView
urlpatterns = [
    path('', IndexListView.as_view(), name='index'),
    path('konkurs/', CompetitionListView.as_view(), name='konkurs'),
    path('like/', LikeDislikeView.as_view(), name='like'),
    path('withdraw/', WithdrawFormView.as_view(), name='withdraw'),

]
