from django.db import models


class FR_ProcessedPDF(models.Model):
    url = models.CharField(max_length=1024, primary_key=True)
    x = models.FloatField(null=True, blank=True, default=None)
    y = models.FloatField(null=True, blank=True, default=None)
    z = models.FloatField(null=True, blank=True, default=None)
    category = models.CharField(max_length=32)
    title = models.CharField(max_length=1024, null=True, blank=True, default="")
    hover = models.CharField(max_length=2048, null=True, blank=True, default="")


class AB_ProcessedPDF(models.Model):
    url = models.CharField(max_length=1024, primary_key=True)
    x = models.FloatField(null=True, blank=True, default=None)
    y = models.FloatField(null=True, blank=True, default=None)
    z = models.FloatField(null=True, blank=True, default=None)
    category = models.CharField(max_length=32)
    title = models.CharField(max_length=1024, null=True, blank=True, default="")
    hover = models.CharField(max_length=2048, null=True, blank=True, default="")
