import os
import tempfile
from pathlib import Path
# from sentence_transformers import SentenceTransformer

# SentenceTransformer('all-MiniLM-L6-v2')

import requests
from django.http import HttpResponse, HttpRequest, JsonResponse
from science_parse_api.api import parse_pdf
from frquestions.process_new_article import pipeline
from frquestions.models import ProcessedPDF


def index(request: HttpRequest):
    print(request.method)
    return HttpResponse("Hello, world. You're at the frquestion index.")


def parsepdf(request: HttpRequest):
    host = 'http://pdfparser'
    port = os.getenv('PDFPARSER_PORT')

    from_db = None
    from_pdf = None
    with tempfile.NamedTemporaryFile() as fp:
        url = request.GET.get('pdfurl')

        if ProcessedPDF.objects.filter(url=url).exists():
            record = ProcessedPDF.objects.get(url=url)
            from_db = {"x": record.x,
                       "y": record.y,
                       "z": record.z,
                       "text": record.hover,
                       "url": record.url,
                       "title": record.category,
                       "color": "black"}
        else:
            response = requests.get(url)
            fp.write(response.content)
            from_pdf = parse_pdf(host, Path(fp.name), port=port)
        to_export = pipeline(from_pdf, from_db, url)

    return JsonResponse(to_export)
