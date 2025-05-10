from django.contrib import admin
from .models import Project, Photo

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'architect', 'client', 'project_year', 'construction_year')
    search_fields = ('name', 'architect', 'client')
    list_filter = ('project_year', 'construction_year')
    inlines = [PhotoInline]

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'is_cover_image', 'index')
    list_filter = ('project', 'is_cover_image')
    search_fields = ('title', 'project__name')
