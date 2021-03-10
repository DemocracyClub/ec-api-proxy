from django.urls import path

from ec_api.apps.frontend import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home_view"),
    path("widget/", views.WidgetView.as_view(), name="widget_view"),
    path("widget/widget.js", views.WidgetJSView.as_view(), name="widget_js"),
]
