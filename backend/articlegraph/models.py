from django.db import models
from picklefield import PickledObjectField


class ScholarlyPublication(models.Model):
    title = models.CharField(max_length=512)
    authors = models.JSONField()
    publication = PickledObjectField()


class CitationReferences(models.Model):
    article_id = models.ForeignKey(ScholarlyPublication, related_name='article_id', on_delete=models.CASCADE)
    cites_id = models.ForeignKey(ScholarlyPublication, related_name='cites_id', on_delete=models.CASCADE)


class FailedPublicationGrab(models.Model):
    title = models.CharField(max_length=512)
    authors = models.JSONField()
    attemptdate = models.DateField(auto_now=True)
