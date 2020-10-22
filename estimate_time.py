import time


class EstimateTime:
    def __init__(self, size):
        self.start = time.time()
        self.size = size
        self.counter = 0
        self.elapsed = 0

    def update(self):
        self.elapsed = time.time() - self.start
        self.counter += 1
        self.estimated = self.elapsed*self.size/self.counter - self.elapsed

    @property
    def elapsed_min(self):
        return int(self.elapsed/60)

    @property
    def elapsed_min_sec(self):
        return self.min_sec(self.elapsed)

    @property
    def estimated_min_sec(self):
        return self.min_sec(self.estimated)

    @staticmethod
    def min_sec(sec):
        # TODO: add hours (only if not zero)
        return "{:d}:{:.1f}".format(
            int(sec/60), sec%60 )

    @staticmethod
    def format_hms(sec):
        # TODO: add hours (only if not zero)
        return "{:d}m{:.1f}s".format(
            int(sec/60), sec%60 )

    @property
    def elapsed_hms(self):
        return self.format_hms(self.elapsed)

    @property
    def estimated_hms(self):
        return self.format_hms(self.elapsed)


if __name__=='__main__':

    v = range(100)

    timer = EstimateTime(len(v))
    print("Counter started to generate {} times".format(timer.size))
    for e in v:
        time.sleep(0.1)
        timer.update()
        print("Elapsed: {}  \tEstimated: {} \t{:4}/{}"
            .format(
                timer.elapsed_min_sec,
                timer.estimated_min_sec,
                timer.counter,
                timer.size))

    print("TOTAL: {} times for {}"
            .format(timer.counter, timer.elapsed_min_sec))
