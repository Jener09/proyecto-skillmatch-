from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Skill, Profile, ProfileSkill, Opportunity, OpportunitySkill, Application


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]


class ProfileSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), source="skill", write_only=True
    )
    skill_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = ProfileSkill
        fields = ["id", "skill", "skill_id", "skill_name", "level", "years_experience"]

    def create(self, validated_data):
        name = validated_data.pop("skill_name", None)
        if name and "skill" not in validated_data:
            skill, _ = Skill.objects.get_or_create(name=name.strip().title())
            validated_data["skill"] = skill
        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skills = ProfileSkillSerializer(source="profileskill_set", many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "user", "bio", "location", "experience_level", "interests", "skills"]


class OpportunitySkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), source="skill", write_only=True
    )
    skill_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = OpportunitySkill
        fields = ["id", "skill", "skill_id", "skill_name", "weight"]

    def create(self, validated_data):
        name = validated_data.pop("skill_name", None)
        if name and "skill" not in validated_data:
            skill, _ = Skill.objects.get_or_create(name=name.strip().title())
            validated_data["skill"] = skill
        return super().create(validated_data)


class OpportunitySerializer(serializers.ModelSerializer):
    required_skills = OpportunitySkillSerializer(source="opportunityskill_set", many=True, read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            "id", "title", "company", "description", "location", "modality",
            "experience_level", "min_skill_level", "created_at", "is_active",
            "required_skills",
        ]


class ApplicationSerializer(serializers.ModelSerializer):
    opportunity = OpportunitySerializer(read_only=True)
    opportunity_id = serializers.PrimaryKeyRelatedField(
        queryset=Opportunity.objects.all(), source="opportunity", write_only=True
    )

    class Meta:
        model = Application
        fields = ["id", "opportunity", "opportunity_id", "status", "match_score", "created_at"]