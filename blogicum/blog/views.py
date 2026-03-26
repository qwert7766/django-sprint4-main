from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404 
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.core.paginator import Paginator
from django.db.models import Count
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm

User = get_user_model()


def paginate_posts(request, posts, per_page=10):
    paginator = Paginator(posts, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def get_posts_queryset(author=None, is_owner=False):
    """Функция для получения queryset постов в зависимости от контекста."""
    if author is None:
        return Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).select_related('author', 'category', 'location').order_by('-pub_date')
    else:
        if is_owner:
            return Post.objects.filter(
                author=author
            ).select_related('category', 'location').order_by('-pub_date')
        else:
            return Post.objects.filter(
                author=author,
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            ).select_related('category', 'location').order_by('-pub_date')


def index(request):
    posts = get_posts_queryset()
    page_obj = paginate_posts(request, posts)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        if not post.is_published or not post.category.is_published or post.pub_date > timezone.now():
            raise Http404("Пост не найден")
    comments = post.comments.select_related('author').all()
    form = CommentForm() if request.user.is_authenticated else None
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = get_posts_queryset().filter(category=category)
    page_obj = paginate_posts(request, posts)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_owner = request.user == profile_user
    
    posts = get_posts_queryset(author=profile_user, is_owner=is_owner)
    posts = posts.annotate(comment_count=Count('comments'))
    page_obj = paginate_posts(request, posts)
    
    context = {
        'profile': profile_user,
        'page_obj': page_obj,
        'is_owner': is_owner
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request, username):
    if request.user.username != username:
        return redirect('blog:profile', username=username)
    
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            if 'password' in form.fields:
                form.fields.pop('password')
            form.save()
            return redirect('blog:profile', username=username)
    else:
        form = UserChangeForm(instance=request.user)
        if 'password' in form.fields:
            form.fields.pop('password')
    
    return render(request, 'blog/user.html', {'form': form})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': PostForm(instance=post)})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/comment.html', {'form': form, 'comment': comment})


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
    return redirect('blog:post_detail', post_id=post_id)