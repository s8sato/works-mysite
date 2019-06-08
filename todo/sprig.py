#!/usr/bin/env python
"""複数行テキスト入力の解析に関わるクラスを記述"""

import networkx as nx
# import matplotlib.pyplot as plt
import re
import datetime

INDENT = "    "


class Line:
    """行について納期や親子関係などの解析を済ませたもの"""

    def __init__(self, id, string):
        self.id = id
        self.string = string
        self.indent = 0
        self.body = ''
        self.attrs = {  # attributes
            'pk': None,
            'head_link': '',
            'title': '',
            'start': datetime.datetime.now(),
            'expected_time': datetime.timedelta(),
            'actual_time': datetime.timedelta(),
            'deadline': datetime.datetime.now(),
            'client': 0,  # todo idではなくUserインスタンスに
            'tail_link': '',
            'is_done': False,
            'note': '',
        }
        self.descendants = []
        self.parent = None

        self.parser = {
            'pk': r'#(\d+)',
            'head_link': r'(.+)\]',
            'start_date': r'(\d{4})?/?(\d{1,2})?/(\d{1,2})-',
            'start_time': r'(\d{1,2})?:(\d{1,2}):?(\d{1,2})?-',
            'expected_time': r'<((\d+)w)?((\d+)d)?((\d+)h)?((\d+)m)?((\d+)s)?>',
            'deadline_date': r'-(\d{4})?/?(\d{1,2})?/(\d{1,2})',
            'deadline_time': r'-(\d{1,2})?:(\d{1,2}):?(\d{1,2})?',
            'client': r'@(\d+)',
            'tail_link': r'\[(.+)',
            'note': r'\((.+)\)',
        }
        self.parse()

    def parse(self):
        """行を解析し属性値を設定する"""
        # 行をインデントと本文に分ける
        match_obj = re.search(r'^(({})*)(.*)$'.format(INDENT), self.string)
        if match_obj:
            self.indent = match_obj.group(1).count(INDENT) or 0
            self.body = match_obj.group(3)
        # 本文を単語に分ける
        words = self.body.split(' ')
        for word in words:
            # 単語が属性を表していれば属性値を設定し、そうでなければtitleに含める
            for attr in self.parser.keys():
                match_obj = re.search(self.parser[attr], word)
                if match_obj:
                    self.set_attrs(match_obj, attr)
                    break
            else:
                self.attrs['title'] = ' '.join([self.attrs['title'], word])
        return self.indent, self.attrs

    def set_attrs(self, match_obj, attr):
        now = datetime.datetime.now()
        if attr == 'pk':
            self.attrs['pk'] = int(match_obj.group(1))
        elif attr == 'head_link':
            self.attrs['head_link'] = match_obj.group(1)
        elif attr == 'start_date' or attr == 'deadline_date':
            # 日を決定
            day = int(match_obj.group(3))
            # 月を決定
            if not match_obj.group(2):
                month = now.month
            else:
                month = int(match_obj.group(2))
            # 年を決定
            if not match_obj.group(1):
                year = now.year
            else:
                year = int(match_obj.group(1))
            # 新しいdatetimeオブジェクトに置き換える
            replacement = {
                'day': day,
                'month': month,
                'year': year,
            }
            if attr == 'start_date':
                self.attrs['start'] = self.attrs['start'].replace(**replacement)
            else:
                self.attrs['deadline'] = self.attrs['deadline'].replace(**replacement)
        elif attr == 'start_time' or attr == 'deadline_time':
            # 秒を決定
            second = int(match_obj.group(3) or 0)
            # 分を決定
            minute = int(match_obj.group(2) or 0)
            # 時を決定
            if not match_obj.group(1):
                hour = now.hour
            else:
                hour = int(match_obj.group(1))
            # 新しいdatetimeオブジェクトに置き換える
            replacement = {
                'second': second,
                'minute': minute,
                'hour': hour,
            }
            if attr == 'start_time':
                self.attrs['start'] = self.attrs['start'].replace(**replacement)
            else:
                self.attrs['deadline'] = self.attrs['deadline'].replace(**replacement)
        elif attr == 'expected_time':
            self.attrs['expected_time'] += datetime.timedelta(
                weeks=int(match_obj.group(2) or 0),
                days=int(match_obj.group(4) or 0),
                hours=int(match_obj.group(6) or 0),
                minutes=int(match_obj.group(8) or 0),
                seconds=int(match_obj.group(10) or 0),
            )
        elif attr == 'client':
            self.attrs['client'] = int(match_obj.group(1))
        elif attr == 'tail_link':
            self.attrs['tail_link'] = match_obj.group(1)
        elif attr == 'note':
            self.attrs['note'] = match_obj.group(1)


class Sprig:
    """複数行テキストを解析して有向グラフ構造をもたせたもの"""
    def __init__(self, text):
        self.lines = [Line(i, string) for i, string in enumerate(text.splitlines())]
        self.set_descendants()
        self.set_parent()
        self.ad = nx.DiGraph()  # arrow_diagram
        self.set_arrow_diagram()

    def set_descendants(self):
        for line in self.lines:
            self.get_descendants(line)

    def get_descendants(self, line):
        descendants = []
        for below_line in self.lines[line.id:]:
            if line.indent < below_line.indent:
                descendants.append(below_line)
            else:
                break
        line.descendants = descendants
        return descendants

    def set_parent(self):
        for line in self.lines:
            self.get_parent(line)

    def get_parent(self, line):
        for above_line in self.lines[line.id::-1]:
            if above_line.indent < line.indent:
                line. parent = above_line
                return above_line
        else:
            return line.id - len(self.lines)

    # def show(self):
    #     print('\n'.join([INDENT * line.indent + line.attrs.values() for line in self.lines]))

    def get_head(self, line):
        return [_ for _ in self.lines if _.attrs['head_link'] == line.attrs['tail_link']]

    def get_tails(self, line):
        return [_ for _ in self.lines if _.attrs['tail_link'] == line.attrs['head_link']]

    def set_arrow_diagram(self):
        for line in self.lines:
            # 単純な関係でのedgeを張る。行が自身の下に固有のnodeをもつイメージ
            initial = line.id
            terminal = line.parent.id if line.parent else line.id - len(self.lines)
            self.ad.add_edge(initial, terminal, **line.attrs)

            # head_linkからtail_linkへダミーedge（重み0）を張る
            if line.attrs['head_link']:
                dummy_attrs = {
                    'pk': None,
                    'head_link': '',
                    'title': 'dummy',
                    'start': datetime.datetime.now(),
                    'expected_time': datetime.timedelta(),
                    'actual_time': datetime.timedelta(),
                    'deadline': datetime.datetime.now(),
                    'client': 0,
                    'tail_link': '',
                    'is_done': False,
                    'note': '',
                }
                for tail in self.get_tails(line):
                    initial = line.parent.id
                    terminal = tail.id
                    self.ad.add_edge(initial, terminal, **dummy_attrs)

    def show_arrow_diagram(self):
        # nx.draw_networkx(self.ad, pos=nx.circular_layout(self.ad))
        nx.draw_networkx(self.ad, pos=nx.shell_layout(self.ad))
        # nx.draw_networkx(self.ad, pos=nx.spectral_layout(self.ad))
        # nx.draw_networkx(self.ad, pos=nx.spring_layout(self.ad))
        plt.show()

    # def all_previous(self, edge, ret=None):
    #     if not ret:
    #         ret = []
    #     ret.append(edge)
    #     previous = [_ for _ in self.ad.edges if _[1] == edge[0]]
    #     if previous:
    #         for _ in previous:
    #             self.all_previous(_, ret)
    #     return ret

    def all_previous(self, edge):
        yield edge
        previous = [_ for _ in self.ad.edges if _[1] == edge[0]]
        for _ in previous:
            yield from self.all_previous(_)


if __name__ == '__main__':
    omu = """
ドレスドオムライス完成] 葉など飾る
    成形したチキンライスに卵ドレスを乗せる
        チキンライスを茶碗で成形して皿に盛る
            チキンライス完成] コンソメとケチャップで調味
                ごはんと鶏肉をフライパンに入れて炒める
                    冷凍ごはんを戻す
                    冷凍ボイル鶏肉を戻す
                    たまねぎが透けるまで炒める
                        たまねぎをフライパンへ
                            たまねぎをみじん切りに
                            フライパンにバター
        ドレープをつけ卵ドレスを作る
            卵液をフライパンへ
                卵に水溶き片栗粉を加える
                    ボウルに卵をとく
                フライパンにバター
                    フライパンをキレイに [チキンライス完成
葉など飾る
    成形したチキンライスに卵ドレスを乗せる
        チキンライスを茶碗で成形して皿に盛る
"""
    # omu = Sprig(omu)
    # # omu.show()
    # omu.show_arrow_diagram()
    text = '        head_link] title /21- <d2h4> -/25 @8888 [tail_link'
    sprig = Sprig(omu)
    print([_ for _ in sprig.all_previous((12, 2))])

