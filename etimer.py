

class Timer():
    '''Класс таймера для подсчета времени'''

    def __init__(self, time):
        self.time = time
        self.changing_intro = False

    def __sub__(self, other):
        return self.time - other.time