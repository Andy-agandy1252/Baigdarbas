from django.db import models
from django.contrib.auth.models import User


class Article(models.Model):
    title = models.CharField(max_length=200)
    headline = models.CharField(max_length=200)
    image = models.ImageField(upload_to='photos', blank=True, null=True)
    author = models.CharField(max_length=100)
    pub_date = models.DateTimeField(auto_now_add=True)
    lead = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.title


class Reklama(models.Model):
    nuotrauka = models.ImageField('', upload_to='photos', blank=True, null=True)
    papildoma_info = models.TextField('')

    # arba link

    def __str__(self):
        return f'{self.nuotrauka} {self.papildoma_info}'


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)  # Add default value here
    dislikes = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(User, through='CommentLike', related_name='liked_comments')
    disliked_by = models.ManyToManyField(User, through='CommentDislike', related_name='dosliked_comments')

    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"


class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)


class CommentDislike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    disliked_at = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='photos', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    balanse = models.IntegerField()

    def __str__(self):
        return f'{self.user.username} Profile'


class Feedback(models.Model):
    name = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
