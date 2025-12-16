class IdentifierIssuer:
    def __init__(self, prefix):
        self.prefix = prefix
        self.counter = 0
        self.existing = {}

    def get_id(self, id: str) -> str:
        if id in self.existing:
            return self.existing[id]
        else:
            new_id = f"{self.prefix}{self.counter}"
            self.existing[id] = new_id
            self.counter += 1
            return new_id

    def hasId(self, id: str) -> bool:
        return id in self.existing

    def assign(self, other: "IdentifierIssuer"):
        for k in self.existing.keys():
            other.get_id(k)

    def copy(self) -> "IdentifierIssuer":
        new_issuer = IdentifierIssuer(self.prefix)
        new_issuer.counter = self.counter
        new_issuer.existing = self.existing.copy()
        return new_issuer