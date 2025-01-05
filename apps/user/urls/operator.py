from django.urls import path

from apps.user.views import OperatorPageListView, ChangeStatusOrderView, ChangeLocationOrderView, AdminWithdrawListView, \
    CheckWithdrawView

urlpatterns = [
    path('operator-page/', OperatorPageListView.as_view(), name='operator'),
    path('change-status-order/<int:pk>', ChangeStatusOrderView.as_view(), name='change-status-order'),
    path('change-locaton-rder/<int:pk>', ChangeLocationOrderView.as_view(), name='change-location-order'),
    path('admin-withdraw-list/', AdminWithdrawListView.as_view(), name='admin-withdraw'),
    path('admin-withdraw/<int:pk>', CheckWithdrawView.as_view(), name='admin-withdraw-update')
]
