from django.contrib import admin
from ..models import (
    ProjectCategory,
    Technology,
    Project,
    ProjectLike,
    ProjectFeature,
    ProjectScreenshot,
    ProjectStat,
    ProjectTestimonial,
    ProjectChallenge,
    ProjectIdea,
)


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("name", "fallback_color")
    prepopulated_fields = {"slug": ("name",)}


class ProjectFeatureInline(admin.TabularInline):
    model = ProjectFeature
    extra = 1


class ProjectScreenshotInline(admin.TabularInline):
    model = ProjectScreenshot
    extra = 1


class ProjectStatInline(admin.TabularInline):
    model = ProjectStat
    extra = 1


class ProjectChallengeInline(admin.TabularInline):
    model = ProjectChallenge
    extra = 2


class ProjectTestimonialInline(admin.StackedInline):
    model = ProjectTestimonial
    extra = 0
    max_num = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "status",
        "project_date",
        "team_display",
        "likes_total",
    )
    list_filter = ("status", "category", "technologies")
    search_fields = ("title", "short_description", "client")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("technologies",)
    inlines = [
        ProjectFeatureInline,
        ProjectScreenshotInline,
        ProjectStatInline,
        ProjectTestimonialInline,
        ProjectChallengeInline,
    ]

    @admin.display(description="Likes")
    def likes_total(self, obj):
        return obj.likes.count()


@admin.register(ProjectLike)
class ProjectLikeAdmin(admin.ModelAdmin):
    list_display = ("project", "session_key", "created_at")
    list_filter = ("created_at",)
    readonly_fields = ("project", "session_key", "created_at")

    def has_add_permission(self, request):
        return False


@admin.register(ProjectIdea)
class ProjectIdeaAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "email", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "message")