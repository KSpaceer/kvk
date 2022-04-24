

class Timer():
    '''Класс таймера для подсчета времени'''

    def __init__(self, time):
        self.time = time
        self.changing_intro = False

    def __sub__(self, other):
        if isinstance(other, Timer):
            return self.time - other.time
        elif isinstance(other, float):
            return self.time - other

    def __rsub__(self, other):
        if isinstance(other, float):
            return other - self.time