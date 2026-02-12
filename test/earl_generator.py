from pathlib import Path
from datetime import datetime, timezone
from test.rdfcanon_test import read_manifest, test_one_case


class EarlGenerator:
    FILE_NAME = "youctagh-rdfcanon-earl.ttl"
    VERSION = "1.0.0"
    RELEASE_DATE = "2025-12-17"
    REPOSITORY = "https://github.com/YoucTagh/rdf-canon"
    DEV_ID = "https://youctagh.github.io/"
    NAME = "YoucTagh RDF Canonicalization"
    DEV_NAME = "Yousouf Taghzouti"
    ORGANIZATION = "https://team.inria.fr/wimmics"
    ORGANIZATION_NAME = "Wimmics Team"

    def main(self):
        self.generate(Path(self.FILE_NAME))

    def generate(self, path: Path):
        tests = read_manifest()

        with path.open("w", encoding="utf-8") as writer:
            self.print_header(writer)

            for test in tests:
                try:
                    test_one_case(test)
                    self.print_result(writer, test.id, True)
                except Exception:
                    self.print_result(writer, test.id, False)

    @staticmethod
    def _now_iso_instant() -> str:
        return (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )

    @classmethod
    def print_result(cls, writer, test_uri: str, passed: bool):
        if not passed:
            print(f"Failed: {test_uri}")

        writer.write("\n")
        writer.write("[ a earl:Assertion ;\n")
        writer.write(f"  earl:assertedBy <{cls.DEV_ID}> ;\n")
        writer.write(f"  earl:subject <{cls.REPOSITORY}> ;\n")
        writer.write(
            f"  earl:test <https://w3c.github.io/rdf-canon/tests/manifest{test_uri}> ;\n"
        )
        writer.write("  earl:result [\n")
        writer.write("    a earl:TestResult ;\n")
        writer.write(
            f"    earl:outcome {'earl:passed' if passed else 'earl:failed'} ;\n"
        )
        writer.write(
            f'    dc:date "{cls._now_iso_instant()}"^^xsd:dateTime ;\n'
        )
        writer.write("  ] ;\n")
        writer.write("  earl:mode earl:automatic ;\n")
        writer.write("] .\n")

    @classmethod
    def print_header(cls, writer):
        writer.write("@prefix dc: <http://purl.org/dc/terms/> .\n")
        writer.write("@prefix doap: <http://usefulinc.com/ns/doap#> .\n")
        writer.write("@prefix foaf: <http://xmlns.com/foaf/0.1/> .\n")
        writer.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
        writer.write("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n")
        writer.write("@prefix earl: <http://www.w3.org/ns/earl#> .\n\n")

        writer.write(f"<> foaf:primaryTopic <{cls.REPOSITORY}> ;\n")
        writer.write(
            f'  dc:issued "{cls._now_iso_instant()}"^^xsd:dateTime ;\n'
        )
        writer.write(f"  foaf:maker <{cls.DEV_ID}> .\n\n")

        writer.write(
            f"<{cls.REPOSITORY}> a doap:Project, earl:TestSubject, earl:Software ;\n"
        )
        writer.write(f'  doap:name "{cls.NAME}" ;\n')
        writer.write(
            '  doap:description "An implementation of RDF Dataset Canonicalization (RDFC 1.0) in Python"@en ;\n'
        )
        writer.write(f"  doap:organization <{cls.ORGANIZATION}> ;\n")
        writer.write(f"  doap:developer <{cls.DEV_ID}> ;\n")
        writer.write(f"  doap:homepage <{cls.REPOSITORY}> ;\n")
        writer.write(
            f"  doap:license <{cls.REPOSITORY}/blob/master/LICENSE> ;\n"
        )
        writer.write("  doap:release [\n")
        writer.write(f'    doap:name "rdfcanon:{cls.VERSION}" ;\n')
        writer.write(f'    doap:revision "{cls.VERSION}" ;\n')
        writer.write(
            f'    doap:created "{cls.RELEASE_DATE}"^^xsd:date ;\n'
        )
        writer.write("  ] ;\n")
        writer.write('  doap:programming-language "Python" .\n\n')

        writer.write(
            f"<{cls.ORGANIZATION}> a foaf:Organization, earl:Assertor ;\n"
        )
        writer.write(f'  foaf:name "{cls.ORGANIZATION_NAME}" ;\n')
        writer.write(f"  foaf:homepage <{cls.ORGANIZATION}> .\n\n")

        writer.write(
            f"<{cls.DEV_ID}> a foaf:Person, earl:Assertor ;\n"
        )
        writer.write(f'  foaf:name "{cls.DEV_NAME}" ;\n')
        writer.write(f"  foaf:homepage <{cls.DEV_ID}> .\n")


if __name__ == "__main__":
    EarlGenerator().main()
