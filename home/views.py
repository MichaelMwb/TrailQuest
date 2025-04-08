from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'home/index.html')
def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request, 'home/about.html',
                {'template_data': template_data})
