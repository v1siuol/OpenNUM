from source import Source


class SourcePool(object):

    def __init__(self):
        self.source_pool = []
        self._counter = 0  # similar to len(source_pool)
        self.trace = {}

        self.a_rates = self.hit_rate_generator(0)
        # self.b_rates = self.hit_rate_generator(1)
        # self.c_rates = self.hit_rate_generator(2)

    def get_each_rate(self):
        # return ((source.index, self.trace[source][0]) for source in self.source_pool)
        return ((source.index, [sum(x) for x in zip(*[self.trace[source][0], self.trace[source][1]])]) for source in self.source_pool)

    def get_source_rate(self, index):
        assert index < self._counter
        source = self.source_pool[index]
        return (self.trace[source][0], self.trace[source][1])

    def get_total_utility(self, length):
        utility_stat = []
        for tick in range(0, length):
            curr_total_utility = 0
            
            for source in self.source_pool:
                curr_total_utility += self.trace[source][2][tick]

            utility_stat.append(curr_total_utility)
        return utility_stat

    def add_source(self, rates=None, hit_rate=0.5, weight=1, paths=None, battery=1):
        new_source = Source(self._counter, rates, hit_rate, weight, paths, battery)
        self.source_pool.append(new_source)
        self.trace[new_source] = [[], [], []]  # offload rate, local rate, utilities
        self._counter += 1

    def get_source(self, index):
        return self.source_pool[index]

    def update_rate_next_tick(self):
        for source in self.source_pool:
            new_rates, new_utilities = source.update_rate_next_tick()
            offload_rate, local_rate = new_rates
            self.trace[source][0].append(offload_rate)
            self.trace[source][1].append(local_rate)
            self.trace[source][2].append(sum(new_utilities))

    def save_initial_data(self):
        for source in self.source_pool:
            offload_rate, local_rate = source.get_rates()
            self.trace[source][0].append(offload_rate)
            self.trace[source][1].append(local_rate)

            self.trace[source][2].append(sum(source.get_utilities()))

    def bind_source_link(self, path_index, source_index, link):
        self.source_pool[source_index].bind_link(path_index, link)

    def init_paths_rate(self):
        for i in range(self._counter):
            self.source_pool[i].init_paths_rate()

    def hit_rate_generator(self, index):
        if index == 0:
            a_1 = (0.5 for _ in range(3000))
            a_2 = (0.3 for _ in range(7000))
            yield from a_1
            yield from a_2
        elif index == 1:
            b_1 = (0.5 for _ in range(2000))
            b_2 = (0.3 for _ in range(3000))
            yield from b_1
            yield from b_2
        elif index == 2:
            c_1 = (0.5 for _ in range(2000))
            c_2 = (0.3 for _ in range(3000))
            yield from c_1
            yield from c_2
        else:
            pass

    def update_hit_rate(self):
        # self.source_pool[0].set_hit_rate(next(self.a_rates))
        pass

    def __repr__(self):
        ret_repr = ''
        for i in range(self._counter):
            ret_repr += '{}: \t hit_rate: {} \t paths: {}\n'.format(self.source_pool[i].index,
                                                                                         self.source_pool[i].hit_rate,
                                                                                         self.source_pool[
                                                                                             i].paths)
        return ret_repr
