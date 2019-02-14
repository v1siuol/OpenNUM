import math


class Source(object):

    def __init__(self, index, rates=None, hit_rate=0.5, weight=1, paths=None):
        if paths is None:
            paths = []
        if rates is None:
            rates = []
        self.index = index
        self.rates = rates
        self.hit_rate = hit_rate
        self.weight = weight
        self.paths = paths

    def get_rates(self):
        return self.rates

    def get_utilities(self):
        return [self.get_utility(j) for j in range(len(self.paths))]

    def get_utility(self, path_index):
        _log_term = 1
        if (self.rates[path_index] != 0):
            # _log_term = math.log(self.rates[path_index] / self.get_theta(path_index))
            _log_term = math.log(self.rates[path_index] / self.get_theta(path_index) + 1)

        # return self.get_theta(path_index) * self.weight * self.get_theta(path_index) * _log_term
        return self.weight * self.get_theta(path_index) * _log_term

    def get_theta(self, path_index):
        total_rates = sum(self.rates)
        if total_rates == 0:
            return 1
        return self.rates[path_index] / total_rates

    def get_next_opt_rate(self, path_index):
        aggregate_price = 0
        for path in self.paths:
            for link in path:
                aggregate_price += link.price  # ？

        return self.hit_rate * self.weight * self.get_theta(path_index) / aggregate_price

    def update_rate_next_tick(self):
        new_rates = []
        for j in range(len(self.paths)):
            assert self.rates[j] >= 0, 'Source rate cannot be negative'
            new_rates.append(self.get_next_opt_rate(j))

        print('Source %d rates: %s\t->\t%s' % (self.index, str(self.rates), str(new_rates)))
        self.rates = new_rates

        return new_rates, self.get_utilities()

    def bind_link(self, path_index, link):
        if path_index >= len(self.paths):
            # new 
            self.paths.append([link])
        else:
            self.paths[path_index].append(link)

    def init_paths_rate(self):
        # self.rates = [0 for _ in range(len(self.paths))]
        self.rates = [0.01 for _ in range(len(self.paths))]

    def set_path_rate(self, path_index, rate):
        self.rates[path_index] = rate

    def __repr__(self):
        return '[{}]'.format(self.index)

    def __str__(self):
        return '[{}]\n'.format(self.index)
