import time


class EstimateTime:
    def __init__(self, size):
        self.start = time.time()
        self.size = size
        self.counter = 0
        self.elapsed_s = 0

    @property
    def current(self):
        return time.time() - self.start

    def update(self):
        self.elapsed_s = self.current
        self.counter += 1
        self.estimated_s = self.elapsed_s*self.size/self.counter - self.elapsed_s

    @property
    def elapsed_min(self):
        return int(self.elapsed_s/60)

    @property
    def elapsed(self):
        return self.min_sec(self.elapsed_s)

    @property
    def estimated(self):
        return self.min_sec(self.estimated_s)

    @staticmethod
    def min_sec(sec):
        # TODO: add hours (only if not zero)
        return "{:d}:{:.1f}".format(
            int(sec/60), sec%60 )

    #@staticmethod
    #def format_hms(sec):
        ## TODO: add hours (only if not zero)
        #return "{:d}m{:.1f}s".format(
            #int(sec/60), sec%60 )

    #@property
    #def elapsed_hms(self):
        #return self.format_hms(self.elapsed_s)

    #@property
    #def estimated_hms(self):
        #return self.format_hms(self.elapsed_s)


if __name__=='__main__':

    v = range(100)

    timer = EstimateTime(len(v))
    print("Counter started to generate {} times".format(timer.size))
    for e in v:
        time.sleep(0.1)
        timer.update()
        print("Elapsed: {}  \tEstimated: {} \t{:4}/{}"
            .format(
                timer.elapsed,
                timer.estimated,
                timer.counter,
                timer.size))

    print("TOTAL: {} times for {}"
            .format(timer.counter, timer.elapsed))
