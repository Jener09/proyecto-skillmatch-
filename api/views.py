from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Skill, Profile, ProfileSkill, Opportunity, OpportunitySkill, Application
from .serializers import (
    SkillSerializer, ProfileSerializer, ProfileSkillSerializer,
    OpportunitySerializer, OpportunitySkillSerializer, ApplicationSerializer,
    UserSerializer,
)
from .matching import compute_match_score, rank_opportunities


# ---------- Autenticación ----------
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register_view(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email", "")
    if not username or not password:
        return Response({"detail": "Usuario y contraseña requeridos."}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({"detail": "El usuario ya existe."}, status=400)
    user = User.objects.create_user(username=username, password=password, email=email)
    Profile.objects.create(user=user)
    refresh = RefreshToken.for_user(user)
    return Response({
        "user": UserSerializer(user).data,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }, status=201)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_view(request):
    user = authenticate(username=request.data.get("username"), password=request.data.get("password"))
    if not user:
        return Response({"detail": "Credenciales inválidas."}, status=401)
    refresh = RefreshToken.for_user(user)
    return Response({
        "user": UserSerializer(user).data,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    })


@api_view(["GET"])
def me_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return Response(ProfileSerializer(profile).data)


# ---------- Perfil ----------
@api_view(["PUT", "PATCH"])
def update_profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    for field in ["bio", "location", "experience_level", "interests"]:
        if field in request.data:
            setattr(profile, field, request.data[field])
    profile.save()
    return Response(ProfileSerializer(profile).data)


@api_view(["POST"])
def add_profile_skill_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    name = (request.data.get("skill_name") or "").strip()
    skill_id = request.data.get("skill_id")
    level = int(request.data.get("level", 3))
    years = int(request.data.get("years_experience", 0))

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, _ = Skill.objects.get_or_create(name=name.title())
    else:
        return Response({"detail": "Debes indicar skill_name o skill_id."}, status=400)

    ps, created = ProfileSkill.objects.update_or_create(
        profile=profile, skill=skill,
        defaults={"level": level, "years_experience": years},
    )
    return Response(ProfileSkillSerializer(ps).data, status=201 if created else 200)


@api_view(["DELETE"])
def remove_profile_skill_view(request, skill_id):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    ProfileSkill.objects.filter(profile=profile, skill_id=skill_id).delete()
    return Response(status=204)


# ---------- Skills ----------
class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all().order_by("name")
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]


# ---------- Oportunidades ----------
class OpportunityViewSet(viewsets.ModelViewSet):
    queryset = Opportunity.objects.filter(is_active=True).prefetch_related("opportunityskill_set__skill")
    serializer_class = OpportunitySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=["post"])
    def apply(self, request, pk=None):
        opp = self.get_object()
        profile, _ = Profile.objects.get_or_create(user=request.user)
        score = compute_match_score(profile, opp)
        app, created = Application.objects.get_or_create(
            user=request.user, opportunity=opp,
            defaults={"match_score": score},
        )
        if not created:
            return Response({"detail": "Ya te postulaste."}, status=400)
        return Response(ApplicationSerializer(app).data, status=201)

    @action(detail=True, methods=["post"])
    def add_skill(self, request, pk=None):
        opp = self.get_object()
        name = (request.data.get("skill_name") or "").strip()
        skill_id = request.data.get("skill_id")
        weight = int(request.data.get("weight", 3))
        if skill_id:
            skill = get_object_or_404(Skill, pk=skill_id)
        elif name:
            skill, _ = Skill.objects.get_or_create(name=name.title())
        else:
            return Response({"detail": "Debes indicar skill_name o skill_id."}, status=400)
        os_, created = OpportunitySkill.objects.update_or_create(
            opportunity=opp, skill=skill, defaults={"weight": weight}
        )
        return Response(OpportunitySkillSerializer(os_).data, status=201 if created else 200)


# ---------- Matches ----------
@api_view(["GET"])
def matches_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    opps = Opportunity.objects.filter(is_active=True).prefetch_related("opportunityskill_set__skill")
    ranked = rank_opportunities(profile, opps)
    data = []
    for op, score in ranked:
        item = OpportunitySerializer(op).data
        item["match_score"] = score
        data.append(item)
    # umbral mínimo recomendado: 30
    return Response(data)


# ---------- Aplicaciones ----------
@api_view(["GET"])
def my_applications_view(request):
    apps = Application.objects.filter(user=request.user).select_related("opportunity")
    return Response(ApplicationSerializer(apps, many=True).data)