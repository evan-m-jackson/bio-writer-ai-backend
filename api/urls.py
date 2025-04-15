from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

router = DefaultRouter()
router.register(r'users', views.UsersViewSet)
router.register(r'fields', views.FieldChoicesViewSet)
router.register(r'user-fields', views.UserFieldsViewSet)
router.register(r'achievements', views.UserAchievementsViewSet)
router.register(r'bios', views.UserBioViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='register'),
]
