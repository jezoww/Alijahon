from django.urls import path

from apps.user.views import RulesTemplateView, RegisterCreateView, LoginFormView, logout_view

urlpatterns = [
    path('rules/', RulesTemplateView.as_view(), name='rules'),
    path('register/', RegisterCreateView.as_view(), name='register'),
    path('login/', LoginFormView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
]
