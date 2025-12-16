from enum import Enum


class RDFCanonTestCase:

    class Type(Enum):
        RDFC10MapTest = "rdfc:RDFC10MapTest"
        RDFC10EvalTest = "rdfc:RDFC10EvalTest"
        RDFC10NegativeEvalTest = "rdfc:RDFC10NegativeEvalTest"

    def __init__(self):
        self.id = ""
        self.type = RDFCanonTestCase.Type.RDFC10MapTest
        self.name = ""
        self.comment = ""
        self.input = ""
        self.expected = ""
        self.hash_algorithm = "sha256"


def getTestCaseOf(case: dict) -> RDFCanonTestCase:
    test_case = RDFCanonTestCase()
    test_case.id = case["id"]
    test_case.type = RDFCanonTestCase.Type(case["type"])
    test_case.name = case["name"]
    test_case.comment = case.get("comment", "")
    test_case.input = case["action"]
    test_case.expected = case.get("result", "")

    hash_algorithm = case.get("hashAlgorithm")
    if hash_algorithm == "SHA384":
        test_case.hash_algorithm = "sha384"
    else:
        test_case.hash_algorithm = "sha256"

    return test_case


def print_test_case(test_case: RDFCanonTestCase):
    print(f"Test Case ID: {test_case.id}")
    print(f"Type: {test_case.type}")
    print(f"Name: {test_case.name}")
    print(f"Comment: {test_case.comment}")
    print(f"Input: {test_case.input}")
    print(f"Expected: {test_case.expected}")
    print(f"Hash Algorithm: {test_case.hash_algorithm}")
