# Create your views here.
from django.views.generic import TemplateView


class APIDocsHome(TemplateView):
    template_name = "api_docs/home.html"
