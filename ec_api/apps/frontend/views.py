import requests
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_control
from django.views.generic import TemplateView

from ec_api.settings import WIDGET_S3_URL


class HomePageView(TemplateView):
    template_name = "frontend/home.html"


class WidgetView(TemplateView):
    template_name = "frontend/widget_view.html"


class WidgetJSView(View):
    @method_decorator(cache_control(max_age=600))
    def get(self, request, *args, **kwargs):
        req = requests.get(WIDGET_S3_URL)
        req.raise_for_status()
        return HttpResponse(req.text, content_type="application/javascript")
