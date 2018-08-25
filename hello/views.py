from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from.forms import HelloForm

class HelloView(TemplateView):

   def __init__(self):
       self.params={
               'title': 'Hello',
               'form': HelloForm() ,
               'result': None
             }
       
   def get(self, request):
       return render(request, 'hello/index.html', self.params)
   
   def post(self, request):
<<<<<<< HEAD
       ch = request.POST.getlist('choice')
       result='<ol><b>selected:</b>'
       for item in ch:
           result+='<li>' + item + '</li>'
       result+='</ol>'
       self.params['result']= result
=======
       ch = request.POST['choice']
       self.params['result']= 'selected: "'+ ch +'".'
>>>>>>> parent of 395f48d... multichoice
       self.params['form']= HelloForm(request.POST)
       return render(request,'hello/index.html',self.params)

# Create your views here.
