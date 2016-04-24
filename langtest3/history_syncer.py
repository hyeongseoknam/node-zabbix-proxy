import threading

class _HistorySyncer(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.__queue = queue

    def run(self):
        while True:
            doc = self.__queue.get()
            self.__parse(doc)

    def __parse(self, doc):
        data

def start(queue):
    _HistorySyncer(queue).start()