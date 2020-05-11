from django.shortcuts import render,redirect,get_object_or_404
from django.http import Http404
from .models import Boards, Topics,Post
from django.contrib.auth.models import User
from .forms import NewTopicForm,PostForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.db.models import Count

# Create your views here.
from django.http import HttpResponse

def home(request):
    boards = Boards.objects.all()
    
    return render(request,'home.html',{'boards':boards})

def board_topics(request,pk):
    try:
        board = Boards.objects.get(pk=pk)
        topics=board.topics.annotate(replies=Count('posts'))
    except Boards.DoesNotExist:
        raise Http404
    return render(request, 'topics.html', {'board': board,'topics':topics})

@login_required(login_url='login')
def new_topic(request, pk):
    board = get_object_or_404(Boards, pk=pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user 
            topic.save()
            Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user 
            )
            return redirect('board_topics', pk=board.pk)  
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})


def topic_posts(request,pk,topic_pk):
    topic=get_object_or_404(Topics,board__pk=pk, pk=topic_pk)
    topic.views+=1
    topic.save()
    return render(request,'topic_posts.html',{'topic':topic})

@login_required(login_url='login')
def reply_topic(request,pk,topic_pk):
    topic=get_object_or_404(Topics,board__pk=pk,pk=topic_pk)
    
    if request.method=="POST":
        form=PostForm(request.POST)

        if form.is_valid:
            post=form.save(commit=False)
            post.topic=topic
            post.created_by=request.user
            post.save()
            return redirect('topic_posts',pk=pk,topic_pk=topic_pk)
        
    else:
        form=PostForm()
    return render(request,'reply_topic.html',{'topic':topic ,'form':form})

    