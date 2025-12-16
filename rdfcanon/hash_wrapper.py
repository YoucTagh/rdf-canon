import hashlib


class HashWrapper:
    def __init__(self, algo="sha256"):
        self.algo = algo
        self.h = hashlib.new(algo)

    def update(self, data):
        self.h.update(data)

    def digest(self):
        return self.h.digest()

    def hexdigest(self):
        return self.h.hexdigest()

    def reset(self):
        self.h = hashlib.new(self.algo)
