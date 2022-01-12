from django.contrib import admin

# Register your models here.
from blog.models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # 控制表单和列表的显示字段
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    # 以下字段用来过滤
    list_filter = ('status', 'created', 'publish', 'author')
    # 以下字段用来查询
    search_fields = ('title', 'body')
    # 将字段名称映射到应该预先填充的字段,然后slug会即刻对title中的字符按照规则进行转换
    prepopulated_fields = {'slug': ('title',)}
    # raw_id_fields 是你想改变为 ForeignKey 或 ManyToManyField 的 Input 部件的字段列表
    raw_id_fields = ('author',)
    # 将 date_hierarchy 设置为你的模型中 DateField 或 DateTimeField 的名称，变化列表页将包括一个基于日期的向下扩展。
    date_hierarchy = 'publish'
    # 排序字段
    ordering = ('status', 'publish')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')
