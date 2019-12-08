from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url,include


urlpatterns = [
    path('users/', views.UserList.as_view(),name = 'users'),
    path('users/<int:pk>/', views.UserDetails.as_view(),name = 'users_details'),
    path('register/', views.UserRegistration.as_view(),name = 'register'),
    path('login/', views.UserLogin.as_view(),name = 'login'),
    path('reset_password/',views.ResetPassword.as_view(),name = 'reset_password'),
    path('user_profile/', views.FileUploadView.as_view(),name = 'user_profile'),
    path('user_profile/<int:pk>/', views.ProfileUpdateView.as_view(),name = 'update_profile'),
    path('activate/<uidb64>/<token>/',views.activate, name = "activate"),
    path('password_reset_confirm/<uidb64>/<token>/<password1>/<password2>/',
         views.password_reset_confirm,name="password_reset_confirm"),
    path('social_login/', views.social_login,name = 'social_login'),


]
urlpatterns = format_suffix_patterns(urlpatterns)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT,)