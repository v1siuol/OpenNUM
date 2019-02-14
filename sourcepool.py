from source import Source


class SourcePool(object):

    def __init__(self):
        self.source_pool = []
        self._counter = 0  # similar to len(source_pool)
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

    def add_source(self, rates=None, hit_rate=0.5, weight=1, paths=None):
        new_source = Source(self._counter, rates, hit_rate, weight, paths)
        self.source_pool.append(new_source)
        self.trace[new_source] = [[], []]  # rates, utilities
        self._counter += 1

    def get_source(self, index):
        return self.source_pool[index]

    def update_rate_next_tick(self):
        for source in self.source_pool:
            new_rates, new_utilities = source.update_rate_next_tick()
            self.trace[source][0].append(sum(new_rates))
            self.trace[source][1].append(sum(new_utilities))

    def save_initial_data(self):
        for source in self.source_pool:
            self.trace[source][0].append(sum(source.get_rates()))
            self.trace[source][1].append(sum(source.get_utilities()))

    def bind_source_link(self, path_index, source_index, link):
        self.source_pool[source_index].bind_link(path_index, link)

    def init_paths_rate(self):
        for i in range(self._counter):
            self.source_pool[i].init_paths_rate()

    def __repr__(self):
        ret_repr = ''
        for i in range(self._counter):
            ret_repr += '{}: \t hit_rate: {} \t paths: {}\n'.format(self.source_pool[i].index,
                                                                                         self.source_pool[i].hit_rate,
                                                                                         self.source_pool[
                                                                                             i].paths)
        return ret_repr
