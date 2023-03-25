import time

class Dump:
    def __init__(self):
        self.file = open("./testing/results.txt", "r+")
        self.prev_stamp = None
        self.block = None

    def timestamp(self):
        current = time.time()
        if (self.block == None):
            self.block = 0
            self.prev_stamp = current
        stamp = self.prev_stamp - current
        self.file.write(str(self.block)+', '+str(current)+', ' + str(stamp)+'\n')
        self.block += 1
        self.prev_stamp = current