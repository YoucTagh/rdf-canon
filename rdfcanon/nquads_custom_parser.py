from rdflib import BNode, Dataset
from typing import MutableMapping
from rdflib import XSD
from rdflib.term import _toPythonMapping


class IdMap(MutableMapping[str, BNode]):
    def __init__(self, dct=None):
        self.dct = {} if dct is None else dct

    def __getitem__(self, key: str) -> BNode:
        return self.dct.setdefault(key, BNode(key))

    def __setitem__(self, key: str, value: BNode):
        self.dct[key] = value

    def __delitem__(self, key: str):
        return self.dct.__delitem__(key)

    def __iter__(self):
        return iter(self.dct)

    def __len__(self) -> int:
        return len(self.dct)


def parse_nquads_preserve_bnodes(file_path):

    for dt in (
        XSD.dateTime,
        XSD.boolean,
        XSD.double,
        XSD.decimal,
        XSD.integer,
        XSD.int,
        XSD.float,
    ):
        _toPythonMapping.pop(dt, None)

    skolem_graph = Dataset().parse(
            location=file_path, format="nquads", bnode_context=IdMap()
        )

    return skolem_graph
