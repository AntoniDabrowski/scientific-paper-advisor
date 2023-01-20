import os
import tempfile
from pathlib import Path

import requests
from django.http import HttpResponse, HttpRequest, JsonResponse
from science_parse_api.api import parse_pdf
from frquestions.process_new_article import pipeline


def index(request: HttpRequest):
    print(request.method)
    return HttpResponse("Hello, world. You're at the frquestion index.")


def parsepdf(request: HttpRequest):
    host = 'http://pdfparser'
    port = os.getenv('PDFPARSER_PORT')

    with tempfile.NamedTemporaryFile() as fp:
        url = request.GET.get('pdfurl')
        response = requests.get(url)
        fp.write(response.content)

        output_dict = parse_pdf(host, Path(fp.name), port=port)
        to_export = pipeline(output_dict, url)

    return JsonResponse(to_export)
