# RDF Canonicalisation

A Python library for **RDF canonicalisation** based on the [W3C RDF Canonicalisation specification](https://www.w3.org/TR/rdf-canon/).
This library allows you to deterministically canonicalise RDF datasets, making it easier to compare, sign, or hash RDF graphs.

## Features

* Deterministic RDF blank node canonicalisation
* Support for multiple hash algorithms (e.g., `sha256`)
* Integration with `rdflib` `Dataset` objects
* Time-based ticker for controlling the maximum duration of the canonicalisation task.

## Installation

```bash
pip install rdfcanon
```

## Usage

```python
from rdfcanon import RDFCanon, RDFCanonTimeTicker
from rdflib import BNode, Dataset, URIRef

# Create a sample RDF dataset
dataset = Dataset()
dataset.add(
    (
        BNode("e0"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        URIRef("http://example.org/vocab#Foo"),
        BNode("g0")
    )
)

# Initialise RDF canonicalisation
rdf_canon = RDFCanon(
    hash_algorithm="sha256",
    dataset=dataset,
    ticker=RDFCanonTimeTicker(3000)  # Optional time ticker
)

# Canonicalise the RDF dataset
print(rdf_canon.canonize())
```

This will output:

```
_:c14n1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://example.org/vocab#Foo> _:c14n0 .
```

## Development

### Build the library

```bash
python setup.py sdist bdist_wheel
```

### Run tests

```bash
pytest
```

## Contributing

Contributions are welcome! Please submit issues or pull requests via GitHub.

## License

MIT License © 2025 YoucTagh