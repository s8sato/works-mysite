#!/usr/bin/env python
"""
"""
import networkx as nx
# import matplotlib.pyplot as plt
import re
import datetime
import uuid

INDENT = "    "


class Line:
    """"""

    def __init__(self, id, string):
        self.id = id
        self.string = string
        self.indent = 0
        self.body = ''
        self.tail_link = ''
        self.head_link = ''
        self.descendants = []
        self.parent = None
        self.title = self.body
        self.start = datetime.timedelta()
        self.expected_time = datetime.timedelta()
        self.actual_time = datetime.timedelta()
        self.deadline = datetime.timedelta()
        self.client = None
        self.is_done = False
        self.is_archived = False
        self.note = ''

        self.initial = None
        self.terminal = None

        self.parse()

    def parse(self):
        parser = re.search(r'^(({})*)(\[.*?\])?([^[]*)(\[.*?\])?'.format(INDENT), self.string)
        if parser:
            self.indent = parser.group(1).count(INDENT) or 0
            self.head_link = parser.group(3) or ''
            self.body = parser.group(4) or ''
            self.tail_link = parser.group(5) or ''
        return self.indent, self.body, self.tail_link, self.head_link


class Sprig:
    """"""
    def __init__(self, sprig, existing):
        self.lines = [Line(i + existing, string) for i, string in enumerate(sprig.splitlines())]
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
            return None

    def show(self):
        print('\n'.join([INDENT * line.indent
                                + line.head_link
                                + line.body
                                + line.tail_link
                         for line in self.lines]))

    def get_head(self, line):
        return [_ for _ in self.lines if _.head_link is line.tail_link]

    def get_tails(self, line):
        return [_ for _ in self.lines if _.tail_link == line.head_link]

    def set_arrow_diagram(self):
        for line in self.lines:
            # 単純な関係でのedgeを張る。行が自身の下に固有のnodeをもつイメージ
            if line.parent:
                attr = {
                    'title': line.title,
                    'start': line.start,
                    'expected_time': line.expected_time,
                    'actual_time': line.actual_time,
                    'deadline': line.deadline,
                    'client': line.client,
                    'is_done': line.is_done,
                    'note': line.note,
                }
                line.initial = line.id
                line.terminal = line.parent.id
                self.ad.add_edge(line.initial, line.terminal, **attr)
            # edgeを張ったことにより自動生成されたnodeを初期化
            for node in self.ad.nodes:
                self.ad.nodes[node]['linker'] = str(uuid.uuid4())
            # ユーザ指定のlinker間にダミーエッジ（重み0）を張る
            if line.head_link:
                attr = {
                    'title': 'dummy',
                    'start': datetime.timedelta(),
                    'expected_time': datetime.timedelta(),
                    'actual_time': datetime.timedelta(),
                    'deadline': datetime.timedelta(),
                    'client': None,
                    'is_done': True,
                    'note': '',
                }
                for tail in self.get_tails(line):
                    initial_of_dummy = line.parent.id
                    terminal_of_dummy = tail.id
                    self.ad.add_edge(initial_of_dummy, terminal_of_dummy, **attr)


    def show_arrow_diagram(self):
        # nx.draw_networkx(self.ad, pos=nx.circular_layout(self.ad))
        nx.draw_networkx(self.ad, pos=nx.shell_layout(self.ad))
        # nx.draw_networkx(self.ad, pos=nx.spectral_layout(self.ad))
        # nx.draw_networkx(self.ad, pos=nx.spring_layout(self.ad))
        plt.show()


class Task:
    """"""

    def __init__(self):
        self.id = 0
        self.parents = []
        self.children = []


class Graph:
    pass

class Edge:
    pass


class Node:
    pass


def set_full_name(str):
    pass


if __name__ == '__main__':
    # ad = nx.DiGraph()  # arrow_diagram
    # ad.add_edge(1, 2, attr='task_a')
    # ad.add_edge(1, 3, attr='task_b')
    # ad.add_edge(2, 5, attr='task_c')
    # ad.add_edge(3, 5, attr='task_d')
    # ad.add_edge(4, 5, attr='task_e')
    # print('task_c: {}'.format(ad[2][5]))
    # print('node_2: {}'.format(ad[5]))
    # ad.remove_edge(4, 5)
    #
    # nx.draw(ad)
    # plt.show()

    omu = """
[ドレスドオムライス完成]葉など飾る
    成形したチキンライスに卵ドレスを乗せる
        チキンライスを茶碗で成形して皿に盛る
            [チキンライス完成]コンソメとケチャップで調味
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
                    フライパンをキレイに[チキンライス完成]
"""


    # line = Line(0, '[ドレスドオムライス完成]葉など飾る')
    omu = Sprig(omu)
    for node in omu.ad.nodes:
        print(omu.ad.nodes[node]['linker'])
    omu.show()
    # omu.show_arrow_diagram()


"""
新規sprigを追加
    ...
    その行が先端の芽を表すなら
    芽までのフルネームを生成してタスク候補とする
    treeとマージする
        同系列の候補のうちdetail_levelが最高のものたちを採用
    チャートを生成して結合
        時間の配分と積算
        指示書No.を指定して着手、工数、納期を取得
    ソート
    ひとつのソースを2通りに表現
        gchartを更新
        treeを更新
    作業用ディレクトリも生成？
編集
    treeとgchartどちらも編集可、互いに同期
完了処理
    gchartの行をコメントアウトして何か実行すると以下からタスクが消える
        tree
            完了日などの記録とともにアーカイブされる
                間違って消したときはアーカイブからsprigを作って再登録
        inbox
        slack
"""
