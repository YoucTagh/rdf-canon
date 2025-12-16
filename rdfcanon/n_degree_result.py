from rdfcanon.identifier_issuer import IdentifierIssuer


class NDegreeResult:

    def __init__(self, hash: str, issuer: IdentifierIssuer):
        self.hash = hash
        self.issuer = issuer

    def __lt__(self, other: "NDegreeResult") -> bool:
        return self.hash < other.hash

    def __eq__(self, other: "NDegreeResult") -> bool:
        return self.hash == other.hash

    def __str__(self):
        return f"NDegreeResult(hash={self.hash}, issuer={self.issuer.prefix})"

    def __repr__(self):
        return self.__str__()
