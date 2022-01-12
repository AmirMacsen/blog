from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.shortcuts import render, get_object_or_404

# Create your views here.
from taggit.models import Tag

from blog.forms import EmailPostForm, CommentForm, SearchForm
from blog.models import Post


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if "query" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # results = Post.objects.annotate(
            #     search=SearchVector('title', 'body'),
            # ).filter(search=query)
            # search_vector = SearchVector("title", weight='A') + SearchVector('body', weight='B')
            # search_query = SearchQuery(query)
            results = Post.objects.annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')

    return render(request,
                  'blog/post/search.html',
                  {"form": form,
                   "query": query,
                   "results": results})


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        # 多对多的关系，使用in查询
        object_list = object_list.filter(tags__name__in=[tag])

    # 每页三条数据
    paginator = Paginator(object_list, 3)
    page = request.GET.get("page")

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # 如果page不是int，则返回第一页
        posts = paginator.page(1)
    except EmptyPage:
        # 如果page超出界限则返回最后一页
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {"page": page,
                   "posts": posts,
                   "tag": tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # 返回所有与post关联的、状态为active的comment，这个字段是通过related_name设置的
    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == "POST":
        # 说明要提交表单了
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # 创建一个comment对象但是并不直接提交到数据库
            new_comment = comment_form.save(commit=False)
            # 将当前post添加到对象中
            new_comment.post = post
            # 提交到数据库
            new_comment.save()
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', 'publish')[:4]

    return render(request,
                  'blog/post/detail.html',
                  {'post': post, "comments": comments, "new_comment": new_comment,
                   "comment_form": comment_form, "similar_posts": similar_posts})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            print(cd)
            # ...send Email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends your read" \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, f"{cd['email']}", [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {"post": post, "form": form, "sent": sent})

# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'
