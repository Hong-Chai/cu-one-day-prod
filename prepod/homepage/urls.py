import django.urls

import homepage.views as views

app_name = "homepage"

urlpatterns = [
    django.urls.path("", views.home, name="home"),
]
