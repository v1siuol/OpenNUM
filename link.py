class Link(object):

    def __init__(self, index, curr_capacity=0.0, max_capacity=25.0, price=None, traffic=None):
        if traffic is None:
            # traffic = set()
            traffic = []
        if price is None:
            price = 5e-5 * max_capacity
        self.index = index
        self.curr_capacity = curr_capacity
        self.max_capacity = max_capacity
        self.price = price  # Lagrange multiplier
        self.traffic = traffic  # source on this link

    def __repr__(self):
        # return '{}: \t price: {}'.format(self.index, self.price)
        return '[{}]'.format(self.index)

    # not used 
    def update_traffic(self, traffic):
        # assert isinstance(traffic, set)
        self.traffic = traffic

    def bind_source(self, source):
        # self.traffic.add(source)
        self.traffic.append(source)

    def __str__(self):
        # return '{}: price: {}\n'.format(self.index, self.price)
        return '[{}]\n'.format(self.index)

    # hard coding 
    def get_next_tick_price(self, alpha):
        source_total_rate = 0

        for source in set(self.traffic):
            if self.index == 0:
                source_total_rate += source.rates[0]
            elif self.index == 1:
                offload_rate, local_rate = source.rates
                source_total_rate += offload_rate + local_rate * source.hit_rate
            elif self.index in [2,3,4]:
                source_total_rate += source.rates[1]
            else:
                raise ValueError('Invalid link index')

            # if self.index == 1:
            #     offload_rate, local_rate = source.rates
            #     source_total_rate += offload_rate + local_rate * source.hit_rate
            # else:
            #     source_total_rate += sum(source.rates) 

        self.curr_capacity = source_total_rate
        print('curr_capacity', self.index, set(self.traffic), source_total_rate, self.price)
        return abs(self.price - alpha * (self.max_capacity - source_total_rate))

    def update_price_next_tick(self, alpha):
        new_price = self.get_next_tick_price(alpha)
        print('Link %d price: %.4f\t->\t%.4f' % (self.index, self.price, new_price))
        self.price = new_price
        return new_price, self.curr_capacity
