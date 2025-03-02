from django.db import models

# Create your models here.
class Sermon(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    autor = models.CharField(max_length=255)
    video_url = models.URLField(blank=True, null=True)
    date = models.DateField()

    def __str__(self):
        return self.title

class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date_start = models.DateField()
    date_finish = models.DateField(blank=True, null=True)


    def __str__(self):
        return self.name
