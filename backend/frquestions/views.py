import os
import tempfile
from pathlib import Path
import requests
from django.http import HttpResponse, HttpRequest, JsonResponse
from science_parse_api.api import parse_pdf
from frquestions.process_new_article import handle_from_db, handle_from_pdf
from frquestions.models import FR_ProcessedPDF
from sentence_transformers import SentenceTransformer

SentenceTransformer_loaded = SentenceTransformer('all-MiniLM-L6-v2')


def index(request: HttpRequest):
    print(request.method)
    return HttpResponse("Hello, world. You're at the frquestion index.")


def parsepdf(request: HttpRequest):
    host = 'http://{}'.format(os.getenv('PDFPARSER_HOST'))
    port = os.getenv('PDFPARSER_PORT')

    with tempfile.NamedTemporaryFile() as fp:
        url = request.GET.get('pdfurl')

        if FR_ProcessedPDF.objects.filter(url=url).exists():
            to_export = handle_from_db(url)
        else:
            response = requests.get(url)
            fp.write(response.content)
            record = parse_pdf(host, Path(fp.name), port=port)
            to_export = handle_from_pdf(record, url, SentenceTransformer_loaded)
    return JsonResponse(to_export)
