import math


class Source(object):

    def __init__(self, index, rate=0.0, hit_rate=0.5, path=None):
        if path is None:
            path = set()
        self.index = index
        self.rate = rate
        self.hit_rate = hit_rate
        self.path = path

    def get_weight(self):
        return self.hit_rate

    def get_utility(self):
        return self.get_weight() * math.log(self.rate + 1)

    # solve 17
    def get_next_opt_rate(self):
        aggregate_price = 0
        for link in self.path:
            aggregate_price += link.price  # ？
        return self.get_weight() / aggregate_price

    # return self.get_weight() / aggregate_price - 1

    def update_rate_next_tick(self):
        new_rate = self.get_next_opt_rate()

        print('Source %d: %.4f\t->\t%.4f' % (self.index, self.rate, new_rate))

        self.rate = new_rate
        return new_rate, self.get_utility()

    def bind_link(self, link):
        self.path.add(link)

    def __repr__(self):
        return '{}: \t rate: {}'.format(self.index, self.rate)

    def __str__(self):
        return '{}: \t rate: {}\n'.format(self.index, self.rate)
