from django.db import models
from django.contrib.auth.models import User


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    EXPERIENCE_LEVELS = [
        ("junior", "Junior"),
        ("mid", "Intermedio"),
        ("senior", "Senior"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, default="")
    location = models.CharField(max_length=120, blank=True, default="")
    experience_level = models.CharField(max_length=10, choices=EXPERIENCE_LEVELS, default="junior")
    interests = models.JSONField(default=list, blank=True)
    skills = models.ManyToManyField(Skill, through="ProfileSkill", related_name="profiles")

    def __str__(self):
        return f"Perfil de {self.user.username}"


class ProfileSkill(models.Model):
    LEVELS = [(i, str(i)) for i in range(1, 6)]  # 1..5
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.PositiveSmallIntegerField(choices=LEVELS, default=3)
    years_experience = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ("profile", "skill")


class Opportunity(models.Model):
    MODALITIES = [
        ("remote", "Remoto"),
        ("hybrid", "Híbrido"),
        ("onsite", "Presencial"),
    ]
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=150)
    description = models.TextField()
    location = models.CharField(max_length=120, blank=True, default="")
    modality = models.CharField(max_length=10, choices=MODALITIES, default="remote")
    experience_level = models.CharField(max_length=10, default="junior")
    min_skill_level = models.PositiveSmallIntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    required_skills = models.ManyToManyField(Skill, through="OpportunitySkill", related_name="opportunities")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} @ {self.company}"


class OpportunitySkill(models.Model):
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    weight = models.PositiveSmallIntegerField(default=3)  # 1..5 importancia

    class Meta:
        unique_together = ("opportunity", "skill")


class Application(models.Model):
    STATUS = [
        ("pending", "Pendiente"),
        ("reviewed", "Revisada"),
        ("accepted", "Aceptada"),
        ("rejected", "Rechazada"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=10, choices=STATUS, default="pending")
    match_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "opportunity")