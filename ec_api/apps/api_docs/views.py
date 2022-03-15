# Create your views here.
import os

from apiblueprint_view.views import ApiBlueprintView
from django.conf import settings
from django.views.generic import TemplateView


class APIDocsHome(TemplateView):
    template_name = "api_docs/home.html"


class APIDocsConcepts(TemplateView):
    template_name = "api_docs/concepts.html"


class BaseAPIDocsBlueprintView(ApiBlueprintView):
    blueprint_base = os.path.join(
        settings.BASE_DIR, "apps/api_docs/blueprints/"
    )

    # template_name = ("api_docs_template.html",)
    styles = {
        "resource": {"class": "card"},
        "resource_group": {"class": "group"},
        "api-description": {"class": "ds-stack-smaller"},
        "method_GET": {"class": "badge success"},
    }

    @property
    def blueprint(self):
        return self.blueprint_base + self.blueprint_file

    def get_template_names(self):
        self.template_name = "api_docs/api_docs_base.html"
        return [self.template_name]


class APIEndpointsView(BaseAPIDocsBlueprintView):
    blueprint_file = "endpoints.apibp"


class APINotesView(BaseAPIDocsBlueprintView):
    blueprint_file = "notes.apibp"
