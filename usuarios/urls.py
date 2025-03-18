from django.urls import path
from .views import CompanySettingsView
from .views import (
    CustomLoginView,
    CustomLogoutView,
    ConfigPanelView,
    UserListView,
    UserCreateView,
    AdminPasswordChangeView,
    ActivityLogView,
    ActivityLogDetailView,online_users_list,
    activity_ping
    

)


urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('config/', ConfigPanelView.as_view(), name='config_panel'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/password/', AdminPasswordChangeView.as_view(), name='admin_password_change'),
    path('activity-log/', ActivityLogView.as_view(), name='activity_log'),
    path('activity-log/<int:pk>/', ActivityLogDetailView.as_view(), name='activity_detail'),
    path('online-users/', online_users_list, name='online_users_list'),
    path('activity_ping/', activity_ping, name='activity_ping'),
     path('config/personalizacion/', CompanySettingsView.as_view(), name='customization'),
    
]