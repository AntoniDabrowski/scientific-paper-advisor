from django.db import models

class ProcessedPDF(models.Model):
    url = models.CharField(max_length=1024,primary_key=True)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    category = models.CharField(max_length=512)
    hover = models.CharField(max_length=1024)
