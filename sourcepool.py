from source import Source


class SourcePool(object):

    def __init__(self):
        self.source_pool = []
        self.counter = 0
        self.trace = {}

    def get_each_rate(self):
        return ((source.index, self.trace[source][0]) for source in self.source_pool)

    def get_total_utility(self, length):
        utility_stat = []
        for tick in range(0, length):
            curr_total_utility = 0
            for source in self.source_pool:
                curr_total_utility += self.trace[source][1][tick]
            utility_stat.append(curr_total_utility)
        return utility_stat

    def add_source(self, rate=0.0, hit_rate=0.5, path=None):
        if path is None:
            path = set()
        new_source = Source(self.counter, rate, hit_rate, path)
        self.source_pool.append(new_source)
        self.trace[new_source] = [[], []]  # rate, utility
        self.counter += 1

    def get_source(self, index):
        return self.source_pool[index]

    def update_rate_next_tick(self):
        for source in self.source_pool:
            new_rate, new_utility = source.update_rate_next_tick()
            self.trace[source][0].append(new_rate)
            self.trace[source][1].append(new_utility)

    def save_initial_data(self):
        for source in self.source_pool:
            self.trace[source][0].append(source.rate)
            self.trace[source][1].append(source.get_utility())


    def bind_source_link(self, source_index, link):
        self.source_pool[source_index].bind_link(link)

    def __repr__(self):
        ret_repr = ''
        for i in range(self.counter):
            ret_repr += '{}: \t rate: {} \t hit_rate: {} \t path: {}\n'.format(self.source_pool[i].index,
                                                                                         self.source_pool[i].rate,
                                                                                         self.source_pool[i].hit_rate,
                                                                                         self.source_pool[
                                                                                             i].path)
        return ret_repr
