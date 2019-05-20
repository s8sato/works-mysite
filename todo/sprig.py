#!/usr/bin/env python
"""
"""
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
        self.attrs = {
            'head_link': '',
            'title': '',
            'start': datetime.datetime.now(),
            'expected_time': datetime.timedelta(hours=1),
            'actual_time': datetime.timedelta(),
            'deadline': datetime.datetime.now() + datetime.timedelta(hours=1),
            'client': 0,
            'tail_link': '',
            'is_done': False,
            'note': '',
        }
        # self.head_link = ''
        # self.title = ''
        # self.start = datetime.datetime.now()
        # self.expected_time = datetime.timedelta(hours=1)
        # self.actual_time = datetime.timedelta()
        # self.deadline = datetime.datetime.now() + datetime.timedelta(hours=1)
        # self.client = 0
        # self.tail_link = ''
        self.descendants = []
        self.parent = None

        attrs = self.parse()[1]
        self.set_attrs(attrs)

    def parse(self):
        parser = re.search(r'^(({})*)(.*)$'.format(INDENT), self.string)
        if parser:
            self.indent = parser.group(1).count(INDENT) or 0
            self.body = parser.group(3)
        words = self.body.split(' ')
        parser = {
            'head_link': r'(.+)\]',
            'start': r'(.+)-',
            'expected_time': r'<(.+)>',
            'deadline': r'-(.+)',
            'client': r'@(.+)',
            'tail_link': r'\[(.+)',
        }
        for word in words:
            for attr in parser.keys():
                if re.search(parser[attr], word):
                    self.attrs[attr] = re.search(parser[attr], word).group(1)
                    break
            else:
                self.attrs['title'] += word

        return self.indent, self.attrs

    def set_attrs(self, attrs):
        for attr in attrs.keys():
            self.attrs[attr] = attrs[attr]


class Sprig:
    """複数行テキストを解析して有向グラフ構造をもたせたもの"""
    def __init__(self, sprig):
        self.lines = [Line(i, string) for i, string in enumerate(sprig.splitlines())]
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
            # edgeを張ったことにより自動生成されたnodeを初期化
            self.ad.nodes[initial]['linker'] = ''
            self.ad.nodes[terminal]['linker'] = ''

            # head_linkとtail_linkの間にダミーedge（重み0）を張る
            if line.attrs['head_link']:
                dummy_attrs = {
                    'head_link': '',
                    'title': 'dummy',
                    'start': datetime.datetime.now(),
                    'expected_time': datetime.timedelta(),
                    'actual_time': datetime.timedelta(),
                    'deadline': datetime.datetime.now(),
                    'client': 0,
                    'tail_link': '',
                    'is_done': True,
                    'note': '',
                }
                for tail in self.get_tails(line):
                    initial = line.parent.id
                    terminal = tail.id
                    self.ad.add_edge(initial, terminal, **dummy_attrs)

                # linkerをhead_linkから継承
                self.ad.nodes[terminal]['linker'] = line.attrs['head_link']

    def show_arrow_diagram(self):
        # nx.draw_networkx(self.ad, pos=nx.circular_layout(self.ad))
        nx.draw_networkx(self.ad, pos=nx.shell_layout(self.ad))
        # nx.draw_networkx(self.ad, pos=nx.spectral_layout(self.ad))
        # nx.draw_networkx(self.ad, pos=nx.spring_layout(self.ad))
        plt.show()


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
    # omu.show()
    omu.show_arrow_diagram()
    tit = 'abc'
    tit += 'def'
    print(tit)
    text = '        head_link] title start- <expected_time> -deadline @client [tail_link'
    sprig = Sprig(text)
