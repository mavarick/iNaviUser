from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

# Create your views here.


def login(request):
    return HttpResponseRedirect(reverse("user:login"))


def register(request):
    return HttpResponseRedirect(reverse("user:register"))


def get_index(request):
    tempalte_file = "index/index.html"
    return render(request, tempalte_file)





