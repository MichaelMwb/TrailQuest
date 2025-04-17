from django.shortcuts import render

# Index view
def index(request):
    return render(request, 'home/index.html')

# About view
def about(request):
    return render(request, 'home/about.html', {'title': 'About'})
