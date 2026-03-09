class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def pos(self):
        return (self.x, self.y)
