import math
import matplotlib.pyplot as plt
from utils import Plt_Line_Color
from linkpool import LinkPool
from sourcepool import SourcePool


class Simulator(object):

    def __init__(self, start_time=0, end_time=1500, alpha=5e-5):
        self.start_time = start_time
        self.time = start_time
        self.end_time = end_time

        self.link_pool = LinkPool()
        self.source_pool = SourcePool()
        self.alpha = alpha

    def reader(self, input_folder_name='./', input_file_name='num_input_0.txt'):
        with open(input_folder_name + input_file_name, 'r') as file:

            # path_num_header = file.readline()
            # path_num_str = path_num_header.split()[0]
            # path_num = int(path_num_str)
            # assert path_num > 0, 'Require a postive path number'

            link_num_header = file.readline()
            link_num_str = link_num_header.split()[0]
            link_num = int(link_num_str)
            assert link_num > 0, 'Require a postive link number'

            for i in range(link_num):
                link_info_line = file.readline()
                link_info = link_info_line.split()
                if len(link_info) == 1:
                    if link_info[0] == 'D':
                        # both default 
                        self.link_pool.add_link()
                    else:
                        raise ValueError('Invalid link parameter')
                elif (len(link_info) == 2):
                    is_default_max_capacity = False
                    if link_info[0] == 'D':
                        # default max_capacity 
                        is_default_max_capacity = True
                    else:
                        max_capacity = float(link_info[0])

                    if link_info[1] == 'D':
                        # default price
                        if (is_default_max_capacity):
                            self.link_pool.add_link()
                        else:
                            self.link_pool.add_link(max_capacity=max_capacity)
                    else:
                        price = float(link_info[1])
                        if (is_default_max_capacity):
                            self.link_pool.add_link(price=price)
                        else:
                            self.link_pool.add_link(max_capacity=max_capacity, price=price)
                else:
                    raise ValueError('Invalid link parameter')


            source_num_header = file.readline()
            source_num_str = source_num_header.split()[0]
            source_num = int(source_num_str)
            assert source_num > 0, 'Require a postive source number'

            for i in range(source_num):
                source_info_line = file.readline()
                source_info = source_info_line.split()
                if len(source_info) == 1:
                    if source_info[0] == 'D':
                        # both default 
                        self.source_pool.add_source()
                    else:
                        raise ValueError('Invalid source parameter')
                elif (len(source_info) == 2):
                    is_default_rate = False
                    if source_info[0] == 'D':
                        # default rate 
                        is_default_rate = True
                    else:
                        rate = float(source_info[0])

                    if source_info[1] == 'D':
                        # default hit_rate
                        if (is_default_rate):
                            self.source_pool.add_source()
                        else:
                            self.source_pool.add_source(rate=rate)
                    else:
                        hit_rate = float(source_info[1])
                        if (is_default_rate):
                            self.source_pool.add_source(hit_rate=hit_rate)
                        else:
                            self.source_pool.add_source(rate=rate, hit_rate=hit_rate)
                else:
                    raise ValueError('Invalid link parameter')


            path_num_header = file.readline()
            path_num_str = path_num_header.split()[0]
            path_num = int(path_num_str)
            assert path_num > 0, 'Require a postive path number'

            # matrix
            for path_index in range(path_num):
                for source_index in range(source_num):
                    route_info_line = file.readline()
                    route_info = route_info_line.split()
                    assert len(route_info) == link_num, ValueError('Invalid path parameter')
                    for link_index in range(link_num):
                        if route_info[link_index] == '1':
                            self.source_pool.bind_source_link(path_index, source_index, self.link_pool.get_link(link_index))
                            self.link_pool.bind_link_source(link_index, self.source_pool.get_source(source_index))
                        elif route_info[link_index] == '0':
                            # do nothing 
                            pass
                        else:
                            raise ValueError('Invalid path parameter')

            self.source_pool.init_paths_rate()

            # print(self.link_pool)
            # print(self.source_pool)

            # care file overflow left ignored 

    def run_next_time_tick(self):
        self.source_pool.update_rate_next_tick()
        self.link_pool.update_price_next_tick(self.alpha)

        # change time on source??
        self.source_pool.update_hit_rate()

        self.time += 1

    def auto_sim(self):
        while self.time < self.end_time:
            self.run_next_time_tick()

        self.auto_plot()

    # external call
    def save_initial_data(self):
        self.link_pool.save_initial_data()
        self.source_pool.save_initial_data()

    def auto_plot(self):

        auto_color = Plt_Line_Color()

        iteration = range(self.start_time, self.end_time + 1)

        # # plot uitility
        plt.figure(1)
        total_utility = self.source_pool.get_total_utility(self.time + 1)
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
            plt.plot(iteration, rate, auto_color.make(), label='S' + str(index))
        plt.legend()

        auto_color.reset()
        # # plot curr_capacity for each link
        plt.figure(3)
        plt.title('Relation Between Iteration and Link Capacity')
        plt.xlabel('Iterations')
        plt.ylabel('Link Capacity')
        link_capacity_generator = self.link_pool.get_each_capacity()
        for index, capacity in link_capacity_generator:
            plt.plot(iteration, capacity, auto_color.make(), label='L' + str(index))
        plt.legend()

        auto_color.reset()
        # # plot price for each link
        plt.figure(4)
        plt.title('Relation Between Iteration and Link Price')
        plt.xlabel('Iterations')
        plt.ylabel('Link Price')
        link_price_generator = self.link_pool.get_each_price()
        for index, price in link_price_generator:
            plt.plot(iteration, price, auto_color.make(), label='L' + str(index))
        plt.legend()


        auto_color.reset()
        plt.figure(5)
        plt.title('Relation Between Rates between Offload and Local Path for Source A')
        plt.xlabel('Iterations')
        plt.ylabel('Rate')
        source_index = 0
        offload_rate, local_rate = self.source_pool.get_source_rate(source_index)
        plt.plot(iteration, offload_rate, auto_color.make(), label='S'+str(source_index)+' - Offload')
        plt.plot(iteration, local_rate, auto_color.make(), label='S'+str(source_index)+' - Local')
        plt.legend()

        plt.show()



# main 
# simulator = Simulator()
simulator = Simulator(end_time=5000, alpha=5e-6)

# simulator.reader(input_file_name='num_input_0.txt')
# simulator.reader(input_file_name='num_input_1.txt')
simulator.reader(input_file_name='num_input_2.txt')
# simulator.reader(input_file_name='num_input_3.txt')

simulator.save_initial_data()
simulator.auto_sim()


# print('Done')
