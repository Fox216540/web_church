from django.shortcuts import render, get_object_or_404
# Create your views here.
from api.models import ChurchDocument

def main(request):
	return render(request, 'main/index.html')

def sermons(request):
	return render(request, "main/sermons.html")

def board(request):
	return render(request, "main/board.html")

def doc(request, slug):
	document = get_object_or_404(ChurchDocument, slug=slug)
	return render(request, "main/doc.html", {"document": document})
def docs(request):
	return render(request, "main/docs.html")

def home_groups(request):
	return render(request, "main/home_groups.html")

def content(request):
	return render(request, "main/content.html")


def custom_404(request, exception):
	return render(request, "404.html", status=404)
