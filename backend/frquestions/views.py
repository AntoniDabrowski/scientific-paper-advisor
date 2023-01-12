from django.http import HttpResponse, HttpRequest


def index(request: HttpRequest):
    print(request.method)
    return HttpResponse("Hello, world. You're at the frquestion index.")
