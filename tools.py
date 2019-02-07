class Plt_Line_Color(object):
    COLORS = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']

    def __init__(self):
        self.color = (c for c in Plt_Line_Color.COLORS)

        lst_line = ['-']
        self.line = lst_line

    def make(self):
        try:
            color = next(self.color)
            return color + self.line[0]
        except StopIteration:
            print('TOO MANY LINE PLOTING NOT ENOUGH COLORS')
            return 'x'

    def reset(self):
        self.color = (c for c in Plt_Line_Color.COLORS)
