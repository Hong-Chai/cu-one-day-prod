from django.shortcuts import render, redirect


def home(request):
    return redirect("lecture:app")
    # return render(request, "homepage/main.html")    # return render(request, "homepage/main.html")
