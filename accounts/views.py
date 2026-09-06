from django.contrib.auth.views import LoginView, LogoutView


class GaplineLoginView(LoginView):
    template_name = "login.html"


class GaplineLogoutView(LogoutView):
    pass

# Create your views here.
