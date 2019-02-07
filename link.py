class Link(object):

    def __init__(self, index, curr_capacity=0.0, max_capacity=25.0, price=0.5, traffic=None):
        if traffic is None:
            traffic = set()
        self.index = index
        self.curr_capacity = curr_capacity
        self.max_capacity = max_capacity
        self.price = price  # Lagrange multiplier
        self.traffic = traffic  # source on this link

    def __repr__(self):
        return '{}: \t price: {}'.format(self.index, self.price)

    def update_traffic(self, traffic):
        assert isinstance(traffic, set)
        self.traffic = traffic

    def bind_source(self, source):
        self.traffic.add(source)

    def __str__(self):
        return '{}: price: {}\n'.format(self.index, self.price)

    # solve 19
    def get_next_tick_price(self, alpha):
        source_total_rate = 0
        for source in self.traffic:
            source_total_rate += source.rate
        self.curr_capacity = source_total_rate
        return abs(self.price - alpha * (self.max_capacity - source_total_rate))

    def update_price_next_tick(self, alpha):
        new_price = self.get_next_tick_price(alpha)
        # print('Link %d: %.4f\t->\t%.4f' % (self.index, self.price, new_price))
        self.price = new_price
        return new_price, self.curr_capacity
