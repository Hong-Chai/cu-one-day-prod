from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render

import users.forms


def signup(request):
    if request.method == "POST":
        form = users.forms.SignupForm(request.POST or None)
        if form.is_valid():
            password1 = form.cleaned_data["password1"]
            password2 = form.cleaned_data["password2"]
            if password1 == password2:
                username = form.cleaned_data["username"]
                if get_user_model().objects.filter(username=username).exists():
                    messages.error(request, "Имя занято!")
                else:
                    user = get_user_model().objects.create_user(
                        username=username,
                        password=password1,
                        email=form.cleaned_data["email"],
                        is_active=True,
                    )
                    user.save()
                    return redirect("users:login")
            else:
                messages.error(request, "Пароли не совпадают!")

    else:
        form = users.forms.SignupForm()

    return render(request, "users/signup.html", {"form": form})
