import math
import matplotlib.pyplot as plt 

class Simulator(object):

	def __init__(self, start_time=0, end_time=1500, alpha=5e-5):
		self.start_time = start_time
		self.time = start_time
		self.end_time = end_time

		self.link_pool = LinkPool()
		self.source_pool = SourcePool()
		self.alpha = alpha 

	def reader(self):
		input_folder_name = './'
		input_file_name = 'num_input_0.txt'
		with open(input_folder_name+input_file_name, 'r') as file_route:
			for line in file_route:
				print(line)

	def run_next_time_tick(self):
		self.source_pool.update_rate_next_tick()
		self.link_pool.update_price_next_tick(self.alpha)

		self.time += 1

	def auto_sim(self):
		while self.time < self.end_time:
			self.run_next_time_tick()
		# self.auto_plot()

	# external call 
	def save_initial_data(self):
		self.link_pool.save_initial_data()
		self.source_pool.save_initial_data()

	def auto_plot(self):

		auto_color = Plt_Line_Color()

		iteration = range(self.start_time, self.end_time+1)

		# # plot uitility 
		plt.figure(1)
		total_utility = self.source_pool.get_total_utility(self.time+1)
		plt.title('Relation Between Iteration and Total Utility')
		plt.xlabel('Iterations')
		plt.ylabel('Total Utility')
		plt.plot(iteration, total_utility)


		# # plot rate for each source  
		plt.figure(2)
		plt.title('Relation Between Iteration and Source Rate')
		plt.xlabel('Iterations')
		plt.ylabel('Source Rate')
		source_rate_generator = self.source_pool.get_each_rate()
		for index, rate in source_rate_generator:
			plt.plot(iteration, rate, auto_color.make(), label='S'+str(index))
		plt.legend()

		# auto_color.reset()
		# # plot curr_capacity for each link  
		plt.figure(3)
		plt.title('Relation Between Iteration and Link Capacity')
		plt.xlabel('Iterations')
		plt.ylabel('Link Capacity')
		link_capacity_generator = self.link_pool.get_each_capacity()
		for index, capacity in link_capacity_generator:
			plt.plot(iteration, capacity, auto_color.make(), label='L'+str(index))
		plt.legend()


		auto_color.reset()
		# # plot price for each link  
		plt.figure(4)
		plt.title('Relation Between Iteration and Link Price')
		plt.xlabel('Iterations')
		plt.ylabel('Link Price')
		link_price_generator = self.link_pool.get_each_price()
		for index, price in link_price_generator:
			plt.plot(iteration, price, auto_color.make(), label='L'+str(index))
		plt.legend()


		plt.show()


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


class LinkPool(object):

	def __init__(self):
		self.link_pool = []
		self.counter = 0
		self.trace = {}


	def add_link(self, curr_capacity=0, max_capacity=25, price=0.5, traffic=set()):
		new_link = Link(self.counter, curr_capacity, max_capacity, price)
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

	def __repr__(self):
		ret_repr = ''
		for i in range(self.counter):
			ret_repr += '{}: \t max_capacity: {} \t price: {} \t traffic: {}\n'.format(self.link_pool[i].index, self.link_pool[i].max_capacity, self.link_pool[i].price, self.link_pool[i].traffic)
		return ret_repr

class Link(object):

	def __init__(self, index, curr_capacity=0, max_capacity=25, price=0.5, traffic=set()):
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


class SourcePool(object):

	def __init__(self):
		self.source_pool = []
		self.counter = 0
		self.trace = {}

	def get_each_rate(self):
		return ((source.index, self.trace[source][0]) for source in self.source_pool)


	def get_total_utility(self, length):
		utility_stat = []
		for tick in range(0,length):
			curr_total_utility = 0
			for source in self.source_pool:
				curr_total_utility += self.trace[source][1][tick]
			utility_stat.append(curr_total_utility)
		return utility_stat

	def add_source(self, rate=1, hit_rate=0.5, occupied_links=set()):
		new_source = Source(self.counter, rate, hit_rate, occupied_links)
		self.source_pool.append(new_source)
		self.trace[new_source] = [[], []]  # rate, utility 
		self.counter += 1

	def update_rate_next_tick(self):
		for source in self.source_pool:
			new_rate, new_utility = source.update_rate_next_tick()
			self.trace[source][0].append(new_rate)
			self.trace[source][1].append(new_utility)

	def save_initial_data(self):
		for source in self.source_pool:
			self.trace[source][0].append(source.rate)
			self.trace[source][1].append(source.get_utility())


	def __repr__(self):
		ret_repr = ''
		for i in range(self.counter):
			ret_repr += '{}: \t rate: {} \t hit_rate: {} \t occupied_links: {}\n'.format(self.source_pool[i].index, self.source_pool[i].rate, self.source_pool[i].hit_rate, self.source_pool[i].occupied_links)
		return ret_repr


class Source(object):

	# def __init__(self, index, rate=1, hit_rate=0.5, occupied_links=set()):
	def __init__(self, index, rate=0, hit_rate=0.5, occupied_links=set()):
		self.index = index
		self.rate = rate
		self.hit_rate = hit_rate
		self.occupied_links = occupied_links

	def get_weight(self):
		return self.hit_rate

	def get_utility(self):
		return self.get_weight() * math.log(self.rate + 1)

	# solve 17 
	def get_next_opt_rate(self):
		aggregate_price = 0
		for link in self.occupied_links:
			aggregate_price += link.price  # ？ 
		return self.get_weight() / aggregate_price
		# return self.get_weight() / aggregate_price - 1

	def update_rate_next_tick(self):
		new_rate = self.get_next_opt_rate()

		print('Source %d: %.4f\t->\t%.4f' % (self.index, self.rate, new_rate))

		self.rate = new_rate
		return new_rate, self.get_utility()

	def __repr__(self):
		return '{}: \t rate: {}'.format(self.index, self.rate)

	def __str__(self):
		return '{}: \t rate: {}\n'.format(self.index, self.rate)



# Reader todo 


# main 
simulator = Simulator()

# print(simulator.reader())

# c1 
# simulator.link_pool.add_link()
# simulator.link_pool.add_link()
# simulator.link_pool.add_link()

# simulator.source_pool.add_source(occupied_links=set([simulator.link_pool.link_pool[0], simulator.link_pool.link_pool[1]]))
# simulator.source_pool.add_source(occupied_links=set([simulator.link_pool.link_pool[1]]))
# simulator.source_pool.add_source(occupied_links=set([simulator.link_pool.link_pool[0]]))

# simulator.link_pool.link_pool[0].update_traffic(set([simulator.source_pool.source_pool[0], simulator.source_pool.source_pool[2]]))
# simulator.link_pool.link_pool[1].update_traffic(set([simulator.source_pool.source_pool[0], simulator.source_pool.source_pool[1]]))



# c2 
simulator.link_pool.add_link(max_capacity=25)
simulator.link_pool.add_link(max_capacity=15)
simulator.link_pool.add_link(max_capacity=25)

simulator.source_pool.add_source(occupied_links=set([simulator.link_pool.link_pool[0], simulator.link_pool.link_pool[1]]))
simulator.source_pool.add_source(occupied_links=set([simulator.link_pool.link_pool[1]]))
simulator.source_pool.add_source(occupied_links=set([simulator.link_pool.link_pool[0]]))

simulator.link_pool.link_pool[0].update_traffic(set([simulator.source_pool.source_pool[0], simulator.source_pool.source_pool[2]]))
simulator.link_pool.link_pool[1].update_traffic(set([simulator.source_pool.source_pool[0], simulator.source_pool.source_pool[1]]))

simulator.save_initial_data()
simulator.auto_sim()





print('Done')


