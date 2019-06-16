#!/usr/bin/env python
"""複数行テキスト入力の解析に関わるクラスを記述"""

import networkx as nx
# import matplotlib.pyplot as plt
import re
import datetime

INDENT = "    "


class Line:
    """行について納期や親子関係などの解析を済ませたもの"""

    parser = {
        'pk': r'#(\d+)',
        'head_link': r'(.+)\]',
        'start_date': r'(\d{4})?/?(\d{1,2})?/(\d{1,2})-',
        'start_time': r'(\d{1,2})?:(\d{1,2})?:?(\d{1,2})?-',
        'expected_time': r'\(((\d+)w)?((\d+)d)?((\d+)h)?((\d+)m)?((\d+)s)?\)',
        'deadline_date': r'-(\d{4})?/?(\d{1,2})?/(\d{1,2})',
        'deadline_time': r'-(\d{1,2})?:(\d{1,2})?:?(\d{1,2})?',
        'client': r'@(\d+)',
        'tail_link': r'\[(.+)',
    }

    def __init__(self, id, string):
        self.id = id
        self.string = string
        self.indent = 0
        self.words = []
        self.is_note = False
        self.attrs = {  # attributes
            'pk': None,
            'head_link': '',
            'title': '',
            'start': None,
            'expected_time': None,
            'actual_time': datetime.timedelta(),
            'deadline': None,
            'client': 0,  # todo idではなくUserインスタンスに
            'tail_link': '',
            'is_done': False,
            'note': '',
        }
        self.descendants = []
        self.parent = None

        self.parse()

    def parse(self):
        """行を解析し属性値を設定する"""
        NOTE_HEAD = r'+'
        self.string2indent_words()
        # note行には目印をつけるだけ
        if self.words[0] == NOTE_HEAD:
            self.is_note = True
        else:
            self.words2attrs()

    def string2indent_words(self):
        """行をインデントと単語群に分ける"""
        match_obj = re.search(r'^(({})*)(.*)$'.format(INDENT), self.string)
        if match_obj:
            self.indent = match_obj.group(1).count(INDENT) or 0
            self.words = match_obj.group(3).split(' ')
        return self.indent, self.words

    def words2attrs(self):
        """単語群から属性値（タイトル、期限など）を設定する"""
        for word in self.words:
            # 単語が属性を表していれば属性値を設定し、そうでなければtitleに含める
            for attr in self.parser.keys():
                match_obj = re.search(self.parser[attr], word)
                if match_obj:
                    self.set_attr(match_obj, attr)
                    break
            else:
                self.attrs['title'] = ' '.join([self.attrs['title'], word]).strip()
        return self.attrs

    def set_attr(self, match_obj, attr):
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
                if self.attrs['start'] is None:
                    self.attrs['start'] = datetime.datetime.now()
                self.attrs['start'] = self.attrs['start'].replace(**replacement)
            else:
                if self.attrs['deadline'] is None:
                    self.attrs['deadline'] = datetime.datetime.now()
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
                if self.attrs['start'] is None:
                    self.attrs['start'] = datetime.datetime.now()
                self.attrs['start'] = self.attrs['start'].replace(**replacement)
            else:
                if self.attrs['deadline'] is None:
                    self.attrs['deadline'] = datetime.datetime.now()
                self.attrs['deadline'] = self.attrs['deadline'].replace(**replacement)
        elif attr == 'expected_time':
            self.attrs['expected_time'] = datetime.timedelta(
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
            

class Sprig:
    """複数行テキストを解析して有向グラフ構造をもたせたもの"""
    def __init__(self, text):
        self.lines = [Line(i, string) for i, string in enumerate(text.splitlines())]
        self.set_notes()
        self.set_descendants()
        self.set_parent()
        self.set_default_attrs()
        self.ad = nx.DiGraph()  # arrow_diagram
        self.set_arrow_diagram()

    def set_notes(self):
        note = []
        # すべての行を逆順に調べ、
        for line in self.lines[::-1]:
            # note行なら蓄積し、
            if line.is_note:
                note.append(' '.join(line.words))
            # 非note行なら蓄積を反映する
            else:
                line.attrs['note'] += '\n'.join(note[::-1])
                note = []
        self.lines = [_ for _ in self.lines if not _.is_note]

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

    def set_default_attrs(self):
        for line in self.lines:
            if line.attrs['start'] is None:
                try:
                    line.attrs['start'] = line.parent.attrs['start']
                except AttributeError:
                    line.attrs['start'] = datetime.datetime.now()
            if line.attrs['deadline'] is None:
                try:
                    line.attrs['deadline'] = line.parent.attrs['deadline']
                except AttributeError:
                    line.attrs['deadline'] = datetime.datetime.now()
        for line in self.lines[::-1]:
            if line.attrs['expected_time'] is None:
                line.attrs['expected_time'] = datetime.timedelta()

                for descendant in line.descendants:
                    try:
                        line.attrs['expected_time'] += descendant.attrs['expected_time']
                    except AttributeError:
                        line.attrs['expected_time'] += datetime.timedelta(hours=1)

    def show(self):
        print('\n'.join([INDENT * line.indent +
                         ' '.join(map(lambda x: str(x), line.attrs.values()))
                         for line in self.lines]))

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
    omu = Sprig(omu)
    omu.show()
    # omu.show_arrow_diagram()
    # sprig = Sprig(omu)
    # print([_ for _ in sprig.all_previous((12, 2))])

