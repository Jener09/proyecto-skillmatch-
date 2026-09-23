from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"skills", views.SkillViewSet, basename="skill")
router.register(r"opportunities", views.OpportunityViewSet, basename="opportunity")

urlpatterns = [
    path("auth/register/", views.register_view),
    path("auth/login/", views.login_view),
    path("auth/me/", views.me_view),
    path("profile/", views.update_profile_view),
    path("profile/skills/", views.add_profile_skill_view),
    path("profile/skills/<int:skill_id>/", views.remove_profile_skill_view),
    path("matches/", views.matches_view),
    path("applications/", views.my_applications_view),
    path("", include(router.urls)),
]