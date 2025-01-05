from django.urls import path

from apps.user.views import MarketListView, ThreadListView, \
    ThreadCreateView, ThreadDeleteView, ThreadDetailView, ThreadAddToCartView, StatisticsListView

urlpatterns = [

    path('market/<str:slug>', MarketListView.as_view(), name='market'),
    path('threads/', ThreadListView.as_view(), name="threads"),
    path('create-thread/', ThreadCreateView.as_view(), name='create-thread'),
    path('delete-thread/<int:pk>', ThreadDeleteView.as_view(), name='delete-thread'),
    path('thread/<int:pk>', ThreadDetailView.as_view(), name='thread-detail'),
    path('thread-add-to-cart/<str:slug>', ThreadAddToCartView.as_view(), name='thread-add-to-cart'),
    path('statistic/', StatisticsListView.as_view(), name='statistic')
]
