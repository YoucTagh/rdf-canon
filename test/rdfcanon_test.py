import json
from unittest.result import failfast
from rdfcanon.main import RDFCanon
from rdfcanon.nquads_custom_parser import parse_nquads_preserve_bnodes
from rdfcanon.rdfcanon_time_ticker import RDFCanonTimeTicker
from test.rdfcanon_test_case import RDFCanonTestCase, getTestCaseOf
import pytest


def read_manifest(verbose: bool = False) -> list[RDFCanonTestCase]:
    test_cases = []
    with open("test/manifest.jsonld", "r", encoding="utf-8") as f:
        manifest = json.load(f)

        for case in manifest["entries"]:
            test_case = getTestCaseOf(case)

            if verbose:
                print(f"Loaded test case: {test_case.id} - {test_case.name}")

            test_cases.append(test_case)

    print(f"Total test cases loaded: {len(test_cases)}")

    return test_cases


@pytest.mark.parametrize("test_case", read_manifest())
def test_one_case(test_case: RDFCanonTestCase):

    try:
        print("Parsing", "rdfcanon/test/" + test_case.input)

        dataset = parse_nquads_preserve_bnodes("test/" + test_case.input)

        canon: RDFCanon = RDFCanon(
            hash_algorithm=test_case.hash_algorithm,
            dataset=dataset,
            ticker=RDFCanonTimeTicker(3000),
        )

        result = canon.canonize()

        print("Canonization result:\n", result)

        assert result is not None, "Canonization result should not be None"

        with open("test/" + test_case.expected, "r", encoding="utf-8") as f:
            expected = f.read()

        if test_case.type == RDFCanonTestCase.Type.RDFC10EvalTest:
            assert_eval(test_case, expected, result)
        elif test_case.type == RDFCanonTestCase.Type.RDFC10MapTest:
            assert_map(test_case, json.loads(expected), canon.canon_issuer.existing)
        elif test_case.type == RDFCanonTestCase.Type.RDFC10NegativeEvalTest:
            failfast(f"Test case {test_case.id} was expected to fail but passed.")

    except Exception as e:
        if test_case.type != RDFCanonTestCase.Type.RDFC10NegativeEvalTest:
            raise e

    print(f"Test case {test_case.id} passed.")


def assert_eval(test_case: RDFCanonTestCase, expected: str, result: str):
    assert (
        expected == result
    ), f"Test case {test_case.id} failed: expected \n|{expected}|\n, got \n|{result}|\n"


def assert_map(test_case: RDFCanonTestCase, expected: dict, result: dict):
    match = False

    match = len(expected) == len(result)

    clean_result = {k: v[2:] for k, v in result.items() if v.startswith("_:")}

    if match:
        for k, v in expected.items():
            match = (k in clean_result) and (clean_result[k] == v)

            if not match:
                break

    assert (
        match
    ), f"Test case {test_case.id} failed: expected mapping\n|{expected.items()}|\ndoes not match result mapping\n|{clean_result.items()}|\n"
