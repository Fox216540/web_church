from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def main(request):
	return render(request, 'main/index.html')

def sermons(request):
	return render(request, "main/sermons.html")

def board(request):
	return render(request, "main/board.html")

def doc(request):
	return render(request, "main/doc.html")

def docs(request):
	return render(request, "main/docs.html")

def home_groups(request):
	return render(request, "main/home_groups.html")

def content(request):
	return render(request, "main/content.html")