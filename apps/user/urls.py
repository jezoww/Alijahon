from django.urls import path

from apps.user.views import RulesTemplateView, RegisterCreateView, LoginFormView, logout_view, IndexListView, \
    LikeDislikeView, ProfileUpdateView, GetDistricts, ChangePasswordFormView, Cart, CartListView, AddToCartView, \
    ProductDeleteView, OrderListView, CreateOrderView, OrderCancelView, KonkursListView, MarketListView, ThreadListView, \
    ThreadCreateView, ThreadDeleteView, ThreadDetailView, ThreadAddToCartView

urlpatterns = [
    path('', IndexListView.as_view(), name='index'),
    path('rules/', RulesTemplateView.as_view(), name='rules'),
    path('register/', RegisterCreateView.as_view(), name='register'),
    path('login/', LoginFormView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('like/', LikeDislikeView.as_view(), name='like'),
    path('profile/<int:pk>', ProfileUpdateView.as_view(), name='profile'),
    path('get-districts/', GetDistricts.as_view(), name='get_districts'),
    path('change_password/', ChangePasswordFormView.as_view(), name='change_password'),
    path('cart/', CartListView.as_view(), name='cart'),
    path('add-to-cart/<str:slug>', AddToCartView.as_view(), name='add-to-cart'),
    path('delete-product/<str:slug>', ProductDeleteView.as_view(), name='delete-product'),
    path('orders/', OrderListView.as_view(), name='orders'),
    path('order/', CreateOrderView.as_view(), name='order'),
    path('cancel-order/<int:pk>', OrderCancelView.as_view(), name='cancel-order'),
    path('konkurs/', KonkursListView.as_view(), name='konkurs'),
    path('market/<str:slug>', MarketListView.as_view(), name='market'),
    path('threads/', ThreadListView.as_view(), name="threads"),
    path('create-thread/', ThreadCreateView.as_view(), name='create-thread'),
    path('delete-thread/<int:pk>', ThreadDeleteView.as_view(), name='delete-thread'),
    path('thread/<int:pk>', ThreadDetailView.as_view(), name='thread-detail'),
    path('thread-add-to-cart/<str:slug>', ThreadAddToCartView.as_view(), name='thread-add-to-cart')
]
