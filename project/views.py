from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import F, Value, IntegerField, Case, When

from .models import Project, Photo

# Frontend views
def home(request):
    # Order by public_private_project, then by construction_year or project_year
    projects = Project.objects.annotate(
        year_for_sorting=Case(
            When(construction_year__isnull=False, then=F('construction_year')),
            When(project_year__isnull=False, then=F('project_year')),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).order_by('public_private_project', 'year_for_sorting')
    
    return render(request, 'project/home.html', {
        'projects': projects,
        'header_visible': True,
        'now': timezone.now()
    })

def project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    photos = project.photo_set.all()
    
    return render(request, 'project/project.html', {
        'project': project,
        'photos': photos,
        'header_visible': True,
        'now': timezone.now()
    })

def about(request):
    return render(request, 'project/about.html', {
        'header_visible': True,
        'now': timezone.now()
    })
