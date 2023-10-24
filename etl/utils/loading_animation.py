import time

class ProgressBar:
    def __init__(self, total, current, chunk_size):
        self.finish_message = '✅ Finished'
        self.failed_message = '❌ Failed'
        self.__failed = False
        self.__finished = False
        self.__first_run = True

        self.total = total
        self.current = current
        self.chunk_size = chunk_size

    @property
    def finished(self):
        return self.__finished

    @finished.setter
    def finished(self, finished):
        if isinstance(finished, bool):
            self.__finished = finished
            self.update()
        else:
            raise ValueError

    @property
    def failed(self):
        return self.__failed

    @failed.setter
    def failed(self, failed):
        if isinstance(failed, bool):
            self.__failed = failed
            if failed:
                self.__threadEvent.set()
                time.sleep(0.1)
        else:
            raise ValueError
        
    def set_prompt(self, finish_message: str = '✅ Finished', failed_message='❌ Failed'):
        self.finish_message = finish_message
        self.failed_message = failed_message

    @staticmethod
    def __clear_lines(n_lines=1):
        LINE_UP = '\033[1A'
        LINE_CLEAR = '\x1b[2K'
        for idx in range(n_lines):
            print("", end=LINE_CLEAR)
            print("", end=LINE_UP)
            print("", end=LINE_CLEAR)

    def __loading(self):
        percent = round((self.current + 1) / self.total * 100)
        prog = round(percent / 5)
        
        if not self.__first_run:
            ProgressBar.__clear_lines(1)
        else:
            self.__first_run = False

        print(f'Processing entries {self.current} to {self.current + self.chunk_size} from total of {self.total}')
        print('['+'='*prog+'.'*(20-prog)+f'] {percent}%', end='\r')

        if self.finished is True:
            ProgressBar.__clear_lines(1)
            print(self.finish_message)
            print("")
        elif self.failed is True:
            ProgressBar.__clear_lines(1)
            print(self.failed_message)
            print("")

    def update(self, current=0):
        self.current = current
        self.__loading()


if __name__ == '__main__':
    total = 4672016
    step = 20000
    current = 0
    results = 0

    print("something")
    print("")
    print("another one")

    progress_bar = ProgressBar(total, current, step)

    while True:
        progress_bar.update(current)
        current += step
        results += 500  # Replace with actual result count
        time.sleep(1)

        if current >= total:
            break
