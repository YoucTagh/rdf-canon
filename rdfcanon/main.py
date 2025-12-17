import itertools
import re
from rdflib import Dataset, URIRef
from rdflib.term import Node, BNode
from sortedcontainers import SortedDict
from rdfcanon.hash_wrapper import HashWrapper
from rdfcanon.identifier_issuer import IdentifierIssuer
from rdfcanon.n_degree_result import NDegreeResult
from rdfcanon.rdfcanon_time_ticker import RDFCanonTimeTicker


class RDFCanon:

    BLANK_A = "_:a"
    BLANK_Z = "_:z"

    def __init__(
        self,
        hash_algorithm: str,
        dataset: Dataset,
        ticker: RDFCanonTimeTicker = None,
    ):
        self.blank_id_to_quad_map: dict[str, list[tuple[Node, Node, Node, Node]]] = (
            dict()
        )
        self.blank_id_to_node_map = dict()
        self.non_normalized_blank_ids: set[str] = set()
        self.blank_id_to_normalized_blank_ids_map: dict[str, str] = dict()
        self.hash_to_blank_id_map: SortedDict[str, set[str]] = SortedDict()
        self.digest = HashWrapper(hash_algorithm)
        self.canon_issuer = IdentifierIssuer("_:c14n")
        self.canon_quads: list[str] = []
        self.dataset = dataset
        self.quads = dataset.quads()
        self.ticker = ticker

    def init_blank_id_quad_map(self, graph: Dataset):
        for quad in graph.quads():
            for node in quad:
                if isinstance(node, BNode):
                    blank_id = str(node)
                    if blank_id not in self.blank_id_to_quad_map:
                        self.blank_id_to_quad_map[blank_id] = []
                    self.blank_id_to_quad_map[blank_id].append(quad)

                    if blank_id not in self.blank_id_to_normalized_blank_ids_map:
                        self.blank_id_to_normalized_blank_ids_map[blank_id] = ""

    def init_non_normalized_blank_ids(self):
        self.non_normalized_blank_ids = set(self.blank_id_to_quad_map.keys())

    def prepare_quads_for_hashing(
        self, quad: tuple[Node, Node, Node, Node], blank_id: str
    ) -> str:

        subject = f"<{quad[0]}>"
        if isinstance(quad[0], BNode):
            subject = self.BLANK_A if str(quad[0]) == blank_id else self.BLANK_Z

        object = f"<{quad[2]}>" if isinstance(quad[2], URIRef) else quad[2].n3()
        if isinstance(quad[2], BNode):
            object = self.BLANK_A if str(quad[2]) == blank_id else self.BLANK_Z

        graph = f"<{quad[3]}>" if quad[3] != self.dataset.default_context.identifier else ".\n"
        if graph != "" and isinstance(quad[3], BNode):
            graph = self.BLANK_A if str(quad[3]) == blank_id else self.BLANK_Z
            graph = f"{graph} .\n"

        return f"{subject} <{quad[1]}> {object} {graph}"

    def hash_first_degree(self, blank_id: str) -> str:

        related = self.blank_id_to_quad_map[blank_id]
        prepared_quads: list[str] = []

        for quad in related:
            self.ticker.tick()
            prepared_quad = self.prepare_quads_for_hashing(quad, blank_id)
            prepared_quads.append(prepared_quad)

        prepared_quads.sort()

        self.digest.reset()

        for pq in prepared_quads:
            self.digest.update(pq.encode("utf-8"))

        return self.digest.hexdigest()

    def issueSimpleIds(self):
        simple: bool = True

        while simple:
            self.ticker.tick()
            simple = False
            self.hash_to_blank_id_map.clear()
            for blank_id in self.non_normalized_blank_ids:
                hash: str = self.hash_first_degree(blank_id)
                if hash not in self.hash_to_blank_id_map:
                    self.hash_to_blank_id_map[hash] = set()
                self.hash_to_blank_id_map[hash].add(blank_id)

        for hash in list(self.hash_to_blank_id_map.keys()):
            self.ticker.tick()
            blank_ids = self.hash_to_blank_id_map[hash]
            if len(blank_ids) == 1:
                blank_id = next(iter(blank_ids))
                self.canon_issuer.get_id(blank_id)
                self.non_normalized_blank_ids.remove(blank_id)
                del self.hash_to_blank_id_map[hash]
                simple = True
            else:
                print(
                    f"Hash collision for hash {hash} with blank IDs: {', '.join(blank_ids)}"
                )

    def issue_n_degree_ids(self):
        for k, v in self.hash_to_blank_id_map.items():

            hash_path_list: list[NDegreeResult] = []

            for blank_id in v:
                self.ticker.tick()
                if self.canon_issuer.hasId(blank_id):
                    continue

                blank_issuer = IdentifierIssuer("_:b")
                blank_issuer.get_id(blank_id)

                path: NDegreeResult = self.hash_n_degree_quads(blank_id, blank_issuer)
                hash_path_list.append(path)

            hash_path_list.sort()

            for result in hash_path_list:
                self.ticker.tick()
                result.issuer.assign(self.canon_issuer)

    def hash_n_degree_quads(self, id: str, issuer: IdentifierIssuer) -> NDegreeResult:
        return HashNDegreeQuads(self).hash(id, issuer)

    def make_canon_quads(self):

        for blank_id in self.blank_id_to_normalized_blank_ids_map.keys():
            canon_id = self.canon_issuer.get_id(blank_id)
            self.blank_id_to_normalized_blank_ids_map[blank_id] = canon_id

        sorted_quads: list[tuple[Node, Node, Node, Node]] = list(self.quads)
        lines: list[str] = []

        for quad in sorted_quads:
            subject = quad[0]
            if isinstance(subject, BNode):
                subject = BNode(
                    self.blank_id_to_normalized_blank_ids_map[str(quad[0])][2:]
                )
            object = quad[2]
            if isinstance(object, BNode):
                object = BNode(
                    self.blank_id_to_normalized_blank_ids_map[str(quad[2])][2:]
                )

            graph = quad[3]
            if isinstance(graph, BNode):
                graph = BNode(
                    self.blank_id_to_normalized_blank_ids_map[str(quad[3])][2:]
                )

            d = Dataset()
            if graph == self.dataset.default_context.identifier:
                d.add((subject, quad[1], object))
            else:
                d.add((subject, quad[1], object, graph))

            lines.append(d.serialize(format="nquads"))

        output = []
        for line in lines:
            line = self.canonicalize_nquads_escapes(line)
            line = ''.join(line.rsplit('\\n\\n', 1))
            line = ' .'.join(line.rsplit('  .', 1))
            output.append(line)

        output.sort()
        # print("\n".join(output))
        self.canon_quads = output

    def canonicalize_nquads_escapes(self, nq: str) -> str:
        def repl(match):
            ch = match.group(0)
            code = ord(ch)

            short = {
                0x08: r"\b",
                0x09: r"\t",
                0x0A: r"\n",
                0x0C: r"\f",
                0x0D: r"\r",
            }

            if code in short:
                return short[code]
            return f"\\u{code:04X}"

        # C0 controls + DEL
        return re.sub(r"[\x00-\x1F\x7F]", repl, nq)

    def canonize(self) -> str:

        self.ticker.tick()

        self.init_blank_id_quad_map(self.dataset)
        self.init_non_normalized_blank_ids()
        self.issueSimpleIds()
        self.issue_n_degree_ids()
        self.make_canon_quads()

        output = "\n".join(self.canon_quads) + "\n"

        return output if output != "\n" else ""


class HashNDegreeQuads:
    def __init__(self, outer: RDFCanon):
        self.data_to_hash: list[str] = []
        self.chosen_issuer = None
        self.chosen_path: list[str] = []
        self.outer = outer

    def append_to_path(
        self,
        related: str,
        path: list[str],
        issuer_copy: IdentifierIssuer,
        recursion_list: list[str],
    ):
        if self.outer.canon_issuer.hasId(related):
            path.append(self.outer.canon_issuer.get_id(related))
        else:
            if not issuer_copy.hasId(related):
                recursion_list.append(related)

            path.append(issuer_copy.get_id(related))

    def create_hash_to_related(self, id: str, issuer: IdentifierIssuer) -> SortedDict:
        hash_to_related: SortedDict[str, set[str]] = SortedDict()

        refer = self.outer.blank_id_to_quad_map[id]

        for quad in refer:
            self.outer.ticker.tick()
            for position in [0, 2, 3]:
                node = quad[position]
                if isinstance(node, BNode):
                    related = str(node)
                    if related != id:
                        hash: str = self.hash_related_blank_node(
                            related, quad, issuer, position
                        )
                        hash_to_related.setdefault(hash, set()).add(related)

        return hash_to_related

    def do_permutation(self, permutation: list[str], issuer: IdentifierIssuer):

        self.outer.ticker.tick()
        issuer_copy = issuer.copy()
        path: list[str] = []
        recursion_list: list[str] = []

        for related in permutation:
            self.outer.ticker.tick()
            self.append_to_path(related, path, issuer_copy, recursion_list)

            if len(self.chosen_path) > 0 and "".join(path) > "".join(self.chosen_path):
                return

        for related in recursion_list:
            self.outer.ticker.tick()
            result: NDegreeResult = self.outer.hash_n_degree_quads(related, issuer_copy)

            path.extend([issuer_copy.get_id(related), "<", result.hash, ">"])
            issuer_copy = result.issuer

            if len(self.chosen_path) > 0 and "".join(path) > "".join(self.chosen_path):
                return

        if len(self.chosen_path) == 0 or "".join(path) < "".join(self.chosen_path):
            self.chosen_path = path
            self.chosen_issuer = issuer_copy

    def hash(self, id: str, default_issuer: IdentifierIssuer) -> NDegreeResult:

        hash_to_related: SortedDict = self.create_hash_to_related(id, default_issuer)

        for k, v in hash_to_related.items():
            self.data_to_hash.append(k)
            self.chosen_path = []
            self.chosen_issuer = None

            permutations = [list(p) for p in itertools.permutations(v)]

            for permutation in permutations:
                self.outer.ticker.tick()
                self.do_permutation(permutation, default_issuer)

            self.data_to_hash.extend(self.chosen_path)
            default_issuer = self.chosen_issuer

        self.outer.digest.reset()
        self.outer.digest.update("".join(self.data_to_hash).encode("utf-8"))
        hash: str = self.outer.digest.hexdigest()
        return NDegreeResult(hash, default_issuer)

    def hash_related_blank_node(
        self,
        related: str,
        quad: tuple[Node, Node, Node, Node],
        issuer: IdentifierIssuer,
        position: int,
    ) -> str:

        id: str = None

        if self.outer.canon_issuer.hasId(related):
            id = self.outer.canon_issuer.get_id(related)
        elif issuer.hasId(related):
            id = issuer.get_id(related)
        else:
            id = self.outer.hash_first_degree(related)

        self.outer.digest.reset()
        self.outer.digest.update(self.get_position_tag(position).encode("utf-8"))

        if position != 3:
            self.outer.digest.update("<".encode("utf-8"))
            self.outer.digest.update(quad[1].encode("utf-8"))
            self.outer.digest.update(">".encode("utf-8"))

        self.outer.digest.update(id.encode("utf-8"))

        return self.outer.digest.hexdigest()

    def get_position_tag(self, position: int) -> str:
        if position == 0:
            return "s"
        elif position == 2:
            return "o"
        elif position == 3:
            return "g"
        else:
            raise Exception("Invalid position for hashing related blank node")
