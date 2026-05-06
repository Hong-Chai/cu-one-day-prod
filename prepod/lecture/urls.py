import django.urls

from . import views

app_name = "lecture"

urlpatterns = [
    django.urls.path("", views.lecture_app, name="app"),
    django.urls.path("save-expertise/", views.save_expertise, name="save_expertise"),
    django.urls.path("submit-lecture/", views.submit_lecture, name="submit_lecture"),
]
