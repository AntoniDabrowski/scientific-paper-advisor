from django.db import models
from picklefield import PickledObjectField


class JsonOfArticleGraphs(models.Model):
    title = models.CharField(max_length=65535)
    json = models.JSONField()


class ScholarlyPublication(models.Model):
    title = models.CharField(max_length=512)
    authors = models.CharField(max_length=512)
    publication = PickledObjectField()
