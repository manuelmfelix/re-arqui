from django.db import models

# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    client = models.CharField(max_length=255, null=True, blank=True)
    project_year = models.IntegerField(null=True, blank=True)
    construction_year = models.IntegerField(null=True, blank=True)
    architect = models.CharField(max_length=255, null=True, blank=True)
    builder = models.CharField(max_length=255, null=True, blank=True)
    site = models.CharField(max_length=255, null=True, blank=True)
    public_private_project = models.IntegerField(default=0)
    other = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.description:
            from django.utils.html import linebreaks
            self.description = linebreaks(self.description)
        super().save(*args, **kwargs)

    def cover_image(self):
        cover = self.photo_set.filter(is_cover_image=True).first()
        return cover.image.url if cover else None

class Photo(models.Model):
    index = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='project/photos/')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    is_cover_image = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.is_cover_image:
            Photo.objects.filter(project=self.project, is_cover_image=True).update(is_cover_image=False)
        super().save(*args, **kwargs)
