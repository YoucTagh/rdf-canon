from test.rdfcanon_test import read_manifest, test_one_case


cases = read_manifest()
test_one_case(cases[0])
