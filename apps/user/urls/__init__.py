from apps.user.urls.auth import urlpatterns as auth_url
from apps.user.urls.cart import urlpatterns as cart_url
from apps.user.urls.main import urlpatterns as main_url
from apps.user.urls.order import urlpatterns as order_url
from apps.user.urls.profile import urlpatterns as profile_url
from apps.user.urls.thread import urlpatterns as thread_url
from apps.user.urls.operator import urlpatterns as oper_url

urlpatterns = auth_url + cart_url + main_url + order_url + profile_url + thread_url + oper_url
