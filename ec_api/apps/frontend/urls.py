from django.urls import path
from django.views.generic import TemplateView

from ec_api.apps.frontend import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home_view"),
    path(
        "terms/",
        TemplateView.as_view(template_name="frontend/terms.html"),
        name="terms_view",
    ),
    path("widget/", views.WidgetView.as_view(), name="widget_view"),
    path("widget/widget.js", views.WidgetJSView.as_view(), name="widget_js"),
]
