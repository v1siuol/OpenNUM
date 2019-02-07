from link import Link


class LinkPool(object):

    def __init__(self):
        self.link_pool = []
        self.counter = 0
        self.trace = {}

    def add_link(self, curr_capacity=0.0, max_capacity=25.0, price=0.5, traffic=None):
        if traffic is None:
            traffic = set()
        new_link = Link(self.counter, curr_capacity, max_capacity, price, traffic)
        self.link_pool.append(new_link)
        self.trace[new_link] = [[], []]  # price, curr_capacity

        self.counter += 1

    def update_price_next_tick(self, alpha):
        for link in self.link_pool:
            new_price, new_curr_capacity = link.update_price_next_tick(alpha)
            self.trace[link][0].append(new_price)
            self.trace[link][1].append(new_curr_capacity)

    def save_initial_data(self):
        for link in self.link_pool:
            self.trace[link][0].append(link.price)
            self.trace[link][1].append(link.curr_capacity)

    def get_each_price(self):
        return ((link.index, self.trace[link][0]) for link in self.link_pool)

    def get_each_capacity(self):
        return ((link.index, self.trace[link][1]) for link in self.link_pool)

    def get_link(self, index):
        return self.link_pool[index]

    def bind_link_source(self, link_index, source):
        self.link_pool[link_index].bind_source(source)

    def __repr__(self):
        ret_repr = ''
        for i in range(self.counter):
            ret_repr += '{}: \t max_capacity: {} \t price: {} \t traffic: {}\n'.format(self.link_pool[i].index,
                                                                                       self.link_pool[i].max_capacity,
                                                                                       self.link_pool[i].price,
                                                                                       self.link_pool[i].traffic)
        return ret_repr
