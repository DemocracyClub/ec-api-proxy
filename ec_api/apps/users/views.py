from django.contrib.auth import get_user_model, login
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import FormView
from django.views.generic.base import TemplateView
from django.template.loader import render_to_string
from django.urls import reverse
from sesame.utils import get_user, get_query_string

from frontend.utils import get_domain
from users.forms import LoginForm

User = get_user_model()

__all__ = ["LoginView"]


class LoginView(FormView):
    form_class = LoginForm
    template_name = "users/login.html"

    def form_valid(self, form):
        """
        Create or retrieve a user trigger the send login email
        """
        user, created = User.objects.get_or_create(
            email=form.cleaned_data["email"]
        )
        if created:
            user.set_unusable_password()
            user.save()

        self.send_login_url(user=user)
        return HttpResponseRedirect(self.get_success_url())

    def send_login_url(self, user):
        """
        Send an email to the user with a link to authenticate and log in
        """
        querystring = get_query_string(user=user)
        domain = get_domain(request=self.request)
        path = reverse("users:authenticate")
        url = f"{self.request.scheme}://{domain}{path}{querystring}"
        subject = "Your magic link to log in to the Electoral Commision API"
        txt = render_to_string(
            template_name="users/email/login_message.txt",
            context={
                "authenticate_url": url,
                "subject": subject,
            },
        )
        return user.email_user(subject=subject, message=txt)

    def get_context_data(self, **kwargs):
        """
        Adds success context variable
        """
        context = super().get_context_data(**kwargs)
        context["success"] = "success" in self.request.GET
        return context

    def get_success_url(self):
        """
        Adds success param so that success message is displayed
        """
        return ".?success"


class AuthenticateView(TemplateView):
    template_name = "users/authenticate.html"

    def get(self, request, *args, **kwargs):
        """
        Attempts to get user from the request and log them in. Redirect to error
        page if django-sesame fails to get a user from the request.
        """
        user = get_user(request)
        if not user:
            return redirect("users:authenticate-error")

        login(request, user)
        # TODO should we redirect logged in user to a different page?
        return super().get(request, *args, **kwargs)


class AuthenticateErrorView(TemplateView):
    template_name = "users/authenticate_error.html"
