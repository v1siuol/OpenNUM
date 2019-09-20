import uuid
from enum import Enum
import collections 

class Result(Enum):
    UNKNOWN = 0
    HIT = 1
    MISS = -1

class Image:

    def __init__(self, ground_truth=Result.UNKNOWN):
        self.id = uuid.uuid4().hex
        self.result = Result.UNKNOWN
        self.ground_truth = ground_truth

class ImageSet:

    def __init__(self):
        self.id = uuid.uuid4().hex
        self.images = []
        self.cursor = 0
        self.uuid2idx = dict()

    def finish(self):
        return self.cursor == len(self.images)

    def set_images(self, images):
        assert isinstance(images, list)
        self.images = images

        for idx, image in enumerate(images):
            assert image.id not in self.uuid2idx
            self.uuid2idx[image.id] = idx

    def get_next_image(self):
        assert not self.finish()
        assert self.cursor < len(self.images)
        img = self.images[self.cursor]
        self.cursor += 1
        return img

    def get_index(self, uuid):
        return self.uuid2idx[uuid]

class Processor():

    def __init__(self, logs, uuid2idx):
        self.id = uuid.uuid4().hex
        self.tasks = collections.defaultdict(list)
        self.logs = logs
        self.uuid2idx = uuid2idx

    def is_busy(self, curr_time):
        if not self.tasks:  # empty 
            return False

        return curr_time < max(self.tasks)

    def add_task(self, curr_time, image, process_time=0):
        finish_time = curr_time + process_time
        self.tasks[finish_time].append(image)
        return finish_time

class LocalProcessor(Processor):
    def add_task(self, curr_time, image, process_time=2):
        start_time = curr_time
        finish_time = start_time + process_time
        self.tasks[finish_time].append(image)

        self.logs[start_time].append('{}/LOCAL begin'.format( str(self.uuid2idx[image.id])) )

        return finish_time

class LinkProcessor(Processor):
    def add_task(self, curr_time, image, processed=False, process_time=0):
        max_prev_finish_time = max(self.tasks) if self.tasks else 0
        start_time = max(max_prev_finish_time, curr_time)
        finish_time = start_time + process_time
        self.tasks[finish_time].append( (image, processed) )

        self.logs[start_time].append('{}/LINK begin'.format( str(self.uuid2idx[image.id])) )

        return finish_time

class GpuProcessor(Processor):
    def add_task(self, curr_time, image, process_time=1):
        max_prev_finish_time = max(self.tasks) if self.tasks else 0
        start_time = max(max_prev_finish_time, curr_time)
        finish_time = start_time + process_time
        self.tasks[finish_time].append(image)

        self.logs[start_time].append('{}/GPU begin'.format( str(self.uuid2idx[image.id])) )

        return finish_time

class User:

    def __init__(self):
        self.id = uuid.uuid4().hex
        # self.hit_rate = 0
        # self.rates = 0
        self.images = ImageSet()

        self.hit_prediction = ''
        self.hit_counter = 0  # (-1, 2)
        self.hit_counter_upper_bound = 2
        self.hit_counter_lower_bound = -1

    def register_logs(self, logs):
        self.logs = logs

    def register_uuid2idx(self, uuid2idx):
        self.uuid2idx = uuid2idx

    def register_processor(self):
        self.local_processor = LocalProcessor(self.logs, self.uuid2idx)

    def register_image(self):

        fake = []
        _ground_truth = '0110011010110001111101111111111001111011010000001000110101100001000101100011111110010001110010011100101101110001011110000011011011111100010111110000101000111011000011010011000000100000100001101101100010101110110000000011011000010101100011111000111111011000111101010111010'  # Counter({'1': 139, '0': 132}) medium clip 

        for i in range(min(len(_ground_truth), 15)):
            fake.append( Image(ground_truth=(Result.HIT if _ground_truth[i] == '1' else Result.MISS)) )

        self.images.set_images(fake)

    def get_feedback(self):
        pass

    def send_local(self, curr_time, logs):
        if not self.local_processor.is_busy(curr_time):

            # a = {0: None}
            # print(curr_time, max({**a, **self.local_processor.tasks}))

            next_img = self.images.get_next_image()
            print('#' + str(self.images.get_index(next_img.id)) + ' ' + str(self.hit_counter))
            self.local_processor.add_task(curr_time, next_img)

    def offload(self, link_processor, curr_time, logs):
        if not link_processor.is_busy(curr_time):
            next_img = self.images.get_next_image()
            print('#' + str(self.images.get_index(next_img.id)) + ' ' + str(self.hit_counter))
            link_processor.add_task(curr_time, next_img)

    # def check_local(self, link_processor, curr_time, logs):
    #     if curr_time in self.local_processor.tasks:

    #         for img in self.local_processor.tasks[curr_time]:
    #             # get result 
    #             img.result = img.ground_truth

    #             result_str = 'HIT' if img.result == Result.HIT else 'MISS'
    #             logs[curr_time].append('{}/LOCAL finish {}'.format( str(self.images.get_index(img.id)), result_str) )

    #             if img.result == Result.HIT:
    #                 # upload
    #                 link_processor.add_task(curr_time, img, processed=True)

    def get_feedback_local(self, curr_time, link_processor, logs):
        if curr_time in self.local_processor.tasks:
            while self.local_processor.tasks[curr_time]:
                img = self.local_processor.tasks[curr_time].pop()
                img.result = img.ground_truth


                result_str = 'UNKNOWN'
                if img.result == Result.HIT:
                    link_processor.add_task(curr_time, img, processed=True)  # upload
                    result_str = 'HIT'
                    if self.hit_counter < self.hit_counter_upper_bound:
                        self.hit_counter += 1
                else:
                    result_str = 'MISS'
                    if self.hit_counter > self.hit_counter_lower_bound:
                        self.hit_counter -= 1

                logs[curr_time].append('{}/LOCAL finish {}'.format( str(self.images.get_index(img.id)), result_str) )
                # print('#', self.hit_counter)


    def get_feedback_gpu(self, curr_time, gpu_tasks, logs):
        if curr_time in gpu_tasks:
            while gpu_tasks[curr_time]:
                img = gpu_tasks[curr_time].pop()
                img.result = img.ground_truth

                result_str = 'UNKNOWN'
                if img.result == Result.HIT:
                    result_str = 'HIT'
                    if self.hit_counter < self.hit_counter_upper_bound:
                        self.hit_counter += 1
                else:
                    result_str = 'MISS'
                    if self.hit_counter > self.hit_counter_lower_bound:
                        self.hit_counter -= 1

                logs[curr_time].append('{}/GPU finish {}'.format( str(self.uuid2idx[img.id]), result_str) )
                # print('#', self.hit_counter)


class Main:

    def __init__(self):
        self.logs = collections.defaultdict(list)
        self.users = []
        self.max_time = 20
        self.uuid2idx = dict()  # images 


        user1 = User()
        user1.register_image()
        self._add_user(user1)
        user1.register_logs(self.logs)
        user1.register_uuid2idx(self.uuid2idx)
        user1.register_processor()

        self.link_processor = LinkProcessor(self.logs, self.uuid2idx)
        self.gpu_processor = GpuProcessor(self.logs, self.uuid2idx)

    def _add_user(self, user):
        self.users.append(user)
        self.uuid2idx = {**self.uuid2idx, **user.images.uuid2idx}

    def run(self):

        for curr_time in range(self.max_time):

            for user in self.users:

                user.get_feedback_local(curr_time, self.link_processor, self.logs)
                user.get_feedback_gpu(curr_time, self.gpu_processor.tasks, self.logs)

                if not user.images.finish():
                    user.send_local(curr_time, self.logs)

                user.get_feedback_local(curr_time, self.link_processor, self.logs)
                # user.get_feedback_gpu(curr_time, self.gpu_processor.tasks, self.logs)

                if not user.images.finish():
                    user.offload(self.link_processor, curr_time, self.logs)

                # user.get_feedback_local(curr_time, self.link_processor, self.logs)
                user.get_feedback_gpu(curr_time, self.gpu_processor.tasks, self.logs)

                # user.check_local(self.link_processor, curr_time, self.logs)


            # arrive at GPU  
            if curr_time in self.link_processor.tasks:
                for img, processed in self.link_processor.tasks[curr_time]:

                    self.logs[curr_time].append('{}/LINK finish'.format( str(self.uuid2idx[img.id])) )

                    if not processed:
                        self.gpu_processor.add_task(curr_time, img)

            # if curr_time in self.gpu_processor.tasks:
            #     for img in self.gpu_processor.tasks[curr_time]:
            #         img.result = img.ground_truth

            #         result_str = 'HIT' if img.result == Result.HIT else 'MISS'
            #         self.logs[curr_time].append('{}/GPU finish {}'.format( str(self.uuid2idx[img.id]), result_str) )


    def print_results(self):
        for time, events in self.logs.items():
            for e in events:
                print('[t={}]: {}'.format(time, e))



if __name__ == '__main__':
    m = Main()
    m.run()
    m.print_results()
