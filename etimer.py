

class Timer():
    '''Класс таймера для подсчета времени'''

    def __init__(self, time):
        self.time: float = time
        self.changing_intro = False

    def __sub__(self, other) -> float:
        if isinstance(other, Timer):
            return float(self.time - other.time)
        elif isinstance(other, float):
            return float(self.time - other)
        elif isinstance(other, int):
            return float(self.time - float(other))

    def __rsub__(self, other):
        if isinstance(other, float):
            return float(other - self.time)
        elif isinstance(other, int):
            return float(float(other) - self.time)