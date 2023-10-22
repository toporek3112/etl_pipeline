from threading import Thread
from threading import Event
import sys
import time

class ProgressBar:
    def __init__(self, total, current, chunk_size):
        self.finish_message = ""
        self.__failed = False
        self.__finished = False
        self.failed_message = ""
        self.__threadEvent = Event()
        self.__thread = Thread(target=self.__loading, daemon=True)
        self.__threadBlockEvent = Event()
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
            if finished:
                self.__threadEvent.set()
                time.sleep(0.1)
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

    def update(self, current):
        self.current = current
        self.__threadEvent.clear()
        self.__thread = Thread(target=self.__loading, daemon=True)  # Create a new thread
        self.__thread.start()
        self.__threadBlockEvent.set()

    def set_prompt(self, finish_message: str = '✅ Finished', failed_message='❌ Failed'):
        self.finish_message = finish_message
        self.failed_message = failed_message
        self.show_loading()

    def __loading(self):
            if self.finished is True and not self.failed:
                sys.stdout.write(f'\r\033[K{self.finish_message}\n')
            else:
                sys.stdout.write(f'\r\033[K{self.failed_message}\n')
            
            sys.stdout.flush()
            self.__threadBlockEvent.wait()
            self.__threadBlockEvent.clear()
            
            percent = round((self.current + 1) / self.total * 100)
            prog = round(percent / 5)

            sys.stdout.write("\x1b[2A")
            sys.stdout.write('\r')
            sys.stdout.write(f'Querying entries {self.current} to {self.current + self.chunk_size} from {self.total}')
            sys.stdout.write('\n')
            sys.stdout.write('['+'='*prog+'.'*(20-prog)+f'] {percent}%')
            sys.stdout.flush()
            # Wait for the next update
            self.__threadEvent.wait(0.1)
            self.__threadEvent.clear()

    def update_current(self, new_current):
        self.current = new_current

if __name__ == '__main__':
    total = 4672016
    step = 20000
    current = 0
    results = 0

    print("something")

    progress_bar = ProgressBar(total, current, step)

    while True:
        progress_bar.update(current, step)
        current += step
        results += 500  # Replace with actual result count
        time.sleep(1)

        if current >= total:
            break
