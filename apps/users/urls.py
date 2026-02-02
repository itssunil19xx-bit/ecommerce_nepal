from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .import views

# router for api view
router = DefaultRouter()
router.register(r'', views.UserViewSet, basename='user')

urlpatterns = [
    # for authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),

    # for profile

    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(),
         name='change-password'),

    # for password reser
    path('password-reset/', views.PasswordResetView.as_view(), name='password-reset'),
    path('password-reset-confirm/', views.PasswordResetConformView.as_view(),
         name='password-reset-comnform'),

    # user management for admins only

    path('users/', views.UserListView.as_view(), name='user-list'),
    path('user/<int:id>/', views.UserDetailView.as_view(), name='user-detail'),

]
