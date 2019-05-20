# from django.db import models

# class Post(models.Model):
#     """"""
#     message = models.TextField(
#         # max_length=100,
#         verbose_name='タスク',
#     )
#
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name='登録日時',
#     )

from django.db import models
import datetime


class Step(models.Model):
    """ステップモデル。正体は有向グラフのノード。状態を表す"""
    class Meta:
        # テーブル名を定義
        db_table = 'steps'

    # テーブルのカラムに対応するフィールドを定義
    loc = models.IntegerField(verbose_name='位置番号', null=True)
    linker = models.CharField(verbose_name='リンク名', null=True, max_length=255)


class Task(models.Model):
    """タスクモデル。正体は有向グラフのエッジ。動作を表す"""
    class Meta:
        # テーブル名を定義
        db_table = 'tasks'

    # テーブルのカラムに対応するフィールドを定義
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    title = models.CharField(verbose_name='タスク名', max_length=255)
    start = models.DateTimeField(verbose_name='着手日時', null=True)
    expected_time = models.DateTimeField(verbose_name='予想時間', default=datetime.timedelta(hours=1))  # todo デフォルト値
    actual_time = models.DateTimeField(verbose_name='実績時間', default=datetime.timedelta(hours=1))  # todo デフォルト値
    deadline = models.DateTimeField(verbose_name='納期', null=True, blank=True)  # todo デフォルト値
    client = models.IntegerField(verbose_name='依頼者', default=0)  # todo デフォルトは自分
    is_done = models.BooleanField(verbose_name='完了', default=False)
    note = models.TextField(verbose_name='備考', null=True)

    initial_step = models.ForeignKey(Step,
                                     related_name='out_tasks',
                                     verbose_name='始点',
                                     default=None,  # todo 唯一の最始点を設定する？
                                     on_delete=models.PROTECT)
    terminal_step = models.ForeignKey(Step,
                                      related_name='in_tasks',
                                      verbose_name='終点',
                                      default=None,   # todo デフォルトは最終点
                                      on_delete=models.PROTECT)

    def __str__(self):
        return u"{0}:{1}... ".format(self.pk, self.title[:10])




