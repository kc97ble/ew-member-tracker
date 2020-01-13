from django.db import models


class Folder(models.Model):
    dir = models.CharField(max_length=255, primary_key=True)
    heat_map_str = models.TextField(blank=True)
