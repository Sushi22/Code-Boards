from django.shortcuts import render,redirect,get_object_or_404
from django.http import Http404
from .models import Boards, Topics,Post
from django.contrib.auth.models import User
from .forms import NewTopicForm,PostForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.db.models import Count
from django.utils import timezone
from django.views.generic import UpdateView,ListView
from django.utils.decorators import method_decorator

# Create your views here.
from django.http import HttpResponse

class BoardsListView(ListView):
    model=Boards
    template_name='home.html'
    context_object_name='boards'


class TopicsListView(ListView):
    model=Topics
    template_name='topics.html'
    context_object_name='topics'
    paginate_by=10

    def get_context_data(self,**kwargs):
        kwargs['board']=self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board=get_object_or_404(Boards, pk=self.kwargs.get("pk"))
        queryset=self.board.topics.order_by('-last_updated').annotate(replies=Count('posts')-1)
        return queryset

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


class PostListView(ListView):
    model=Post
    context_object_name='posts'
    template_name='topic_posts.html'
    paginate_by=2

    def get_context_data(self,**kwargs):

        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        # print(self.request.session[session_key])
        if not self.request.session.get(session_key, False):
            # print(self.request.session[session_key])
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True        
        kwargs['topic']=self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic=get_object_or_404(Topics, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset=self.topic.posts.order_by('created_at')
        return queryset
        
    

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

            topic.last_updated=timezone.now()
            topic.save()
            return redirect('topic_posts',pk=pk,topic_pk=topic_pk)
        
    else:
        form=PostForm()
    return render(request,'reply_topic.html',{'topic':topic ,'form':form})

@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model=Post
    fields=('message',)
    pk_url_kwarg='post_pk'
    template_name='edit_post.html'
    context_object_name='post'

    def form_valid(self,form):
        post=form.save(commit=False)
        post.updated_by=self.request.user
        post.updated_at=timezone.now()
        post.save()
        return redirect('topic_posts',pk=post.topic.board.pk,topic_pk=post.topic.pk)


