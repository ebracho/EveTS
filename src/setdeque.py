from collections import deque

# Deque that can never have the same value inserted more than once
# (even if that value has been removed)
class SetDeque:
    def __init__(self, values=[]):
        self.history = set(values)
        self.queue = deque(self.history)

    def append(self, value):
        if value not in self.history:
            self.queue.append(value)
            self.history.update(value)

    def appendleft(self, value):
        if value not in self.history:
            self.queue.appendleft(x)
            self.history.update(value)
   
    def clear(self):
        self.queue.clear()

    def extend(self, values):
        for value in values:
            if value not in self.history:
                self.history.update(value)
                self.queue.append(value)
        
    def extendleft(self, values):
        for value in values:
            if value not in self.history:
                self.history.update(value)
                self.queue.appendleft(value)

    def pop(self):
        value = self.queue.pop()
        return value

    def popleft(self):
        value = self.queue.popleft()
        return value
        
    def remove(self, value):
        self.queue.remove(value)

    def reverse(self):
        self.queue.reverse()

    def rotate(self, n):
        self.queue.rotate(n)

    def __str__(self):
        return self.queue.__str__()

    def __len__(self):
        return len(self.queue)

    def __iter__(self):
        return self.queue.__iter__()

    def __reversed__(self):
        return self.queue.__reversed__()

    def __contains__(self, value):
        return self.history.__contain__(value)

