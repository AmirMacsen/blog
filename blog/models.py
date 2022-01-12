from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', "Draft"),
        ('published', "Published"),
    )

    title = models.CharField(max_length=250)
    # 用于URL种，作为一种简短的标记，slug仅仅包含数字、字母、下划线及连接符。用于构建具有较好外观的，SEO友好的URL
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    # 当删除用户时，数据库将删除关联的帖子，related_name指定反向关系的名称
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    body = models.TextField()
    # 使用django的时区now方法作为默认值，并以时区格式返回当前日期
    publish = models.DateTimeField(default=timezone.now)
    # 当创建某个帖子时，日期将被自动更新
    created = models.DateTimeField(auto_now_add=True)
    # 当保存某个对象时，日期将被自动更新
    updated = models.DateTimeField(auto_now=True)
    # 选择帖子的状态
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")

    objects = models.Manager()  # 默认管理器
    published = PublishedManager()  # 定制管理器'

    # 标签管理器
    tags = TaggableManager()

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day, self.slug])

    class Meta:
        ordering = ('-publish',)
        verbose_name_plural="文章列表"

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=60)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)
        verbose_name_plural="评论列表"

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"
