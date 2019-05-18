from django.db import models

class Post(models.Model):
    """"""
    message = models.TextField(
        # max_length=100,
        verbose_name='タスク',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='登録日時',
    )