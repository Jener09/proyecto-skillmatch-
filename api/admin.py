from django.contrib import admin
from .models import Skill, Profile, ProfileSkill, Opportunity, OpportunitySkill, Application


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


class ProfileSkillInline(admin.TabularInline):
    model = ProfileSkill
    extra = 1


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "experience_level", "location")
    list_filter = ("experience_level",)
    search_fields = ("user__username", "location")
    inlines = [ProfileSkillInline]


class OpportunitySkillInline(admin.TabularInline):
    model = OpportunitySkill
    extra = 1


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "company", "modality", "experience_level", "is_active", "created_at")
    list_filter = ("modality", "experience_level", "is_active")
    search_fields = ("title", "company")
    inlines = [OpportunitySkillInline]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "opportunity", "status", "match_score", "created_at")
    list_filter = ("status",)
    search_fields = ("user__username", "opportunity__title")