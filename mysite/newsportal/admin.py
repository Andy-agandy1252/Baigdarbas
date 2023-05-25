from django.contrib import admin
from .models import Article, Reklama, UserProfile, Comment, CommentLike, CommentDislike, Feedback
from django.utils.html import format_html

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'headline', 'image', 'author', 'pub_date', 'lead', 'content')


class ReklamaAdmin(admin.ModelAdmin):
    list_display = ('nuotrauka', 'papildoma_info')


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'avatar', 'location', 'balanse')
    def display_avatar(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.avatar.url)

    display_avatar.short_description = 'Avatar'


class ComentAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'content', 'created_at', 'likes', 'dislikes')


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment', 'created_at')

admin.site.register(Article, ArticleAdmin)
admin.site.register(Reklama, ReklamaAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Comment, ComentAdmin)
admin.site.register(CommentLike)
admin.site.register(CommentDislike)
admin.site.register(Feedback, FeedbackAdmin)
