from django.urls import path

from apps.user.views import ProfileUpdateView, GetDistricts, ChangePasswordFormView

urlpatterns = [
    path('profile/<int:pk>', ProfileUpdateView.as_view(), name='profile'),
    path('get-districts/', GetDistricts.as_view(), name='get_districts'),
    path('change_password/', ChangePasswordFormView.as_view(), name='change_password'),
]
