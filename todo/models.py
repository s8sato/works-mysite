from django.db import models
import datetime


class Step(models.Model):
    """ステップモデル。正体は有向グラフのノード。状態を表す"""
    class Meta:
        # テーブル名を定義
        db_table = 'steps'

    # テーブルのカラムに対応するフィールドを定義
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


class Task(models.Model):
    """タスクモデル。正体は有向グラフのエッジ。動作を表す"""
    class Meta:
        # テーブル名を定義
        db_table = 'tasks'

    # テーブルのカラムに対応するフィールドを定義
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    title = models.CharField(verbose_name='タスク名', max_length=255)
    start = models.DateTimeField(verbose_name='着手日時', null=True, default=datetime.datetime.now())
    expected_time = models.DurationField(verbose_name='予想時間', default=datetime.timedelta(hours=1))  # todo デフォルト値
    actual_time = models.DurationField(verbose_name='実績時間', default=datetime.timedelta())  # todo デフォルト値
    deadline = models.DateTimeField(verbose_name='納期', default=datetime.datetime.now() + datetime.timedelta(hours=1))  # todo デフォルト値
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

    def restring(self):
        return ' '.join([
            r'#' + str(self.pk),
            self.title,
            self.start.strftime('%Y/%m/%d') + r'-',
            self.start.strftime('%H:%M:%S') + r'-',
            r'<' +
            # str(self.expected_time.weeks) + r'w' +
            str(self.expected_time.days) + r'd' +
            # str(self.expected_time.hours) + r'h' +
            # str(self.expected_time.minutes) + r'm' +
            str(self.expected_time.seconds) + r's'
            + r'>',
            r'-' + self.deadline.strftime('%Y/%m/%d'),
            r'-' + self.deadline.strftime('%H:%M:%S'),
            r'@' + str(self.client),
            r'(' + str(self.note) + r')'
        ])
