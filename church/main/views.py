from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def main(request):
    return render(request, 'main/index.html')

def sermons(request):
    return render(request, "main/sermons.html")

def confession_of_faith(request):
    return render(request, 'main/confession_of_faith.html')