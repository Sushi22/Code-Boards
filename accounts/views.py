from django.shortcuts import render,redirect
from django.contrib.auth import login as auth_login
from .forms import SignUpForm
from django.views.generic import UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import ModelFormMixin,FormMixin

# Create your views here.
def signup(request):
    if request.method=='POST':
        form=SignUpForm(request.POST)
        if form.is_valid():
            user=form.save()
            auth_login(request, user)
            return redirect('home')

    else:
        form= SignUpForm()
    return render(request,'signup.html',{'form':form})

@method_decorator(login_required, name='dispatch')
class MyAccountView(UpdateView):
    model=User
    template_name='My_account.html'
    fields=('first_name','last_name','username')
    success_url=reverse_lazy('home')

    
    def get_object(self):
        print(self.request.user.username)
        return self.request.user

    

