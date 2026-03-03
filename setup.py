from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rdfcanon",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "rdflib==7.5.0",
        "sortedcontainers==2.4.0",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Yousouf Taghzouti",
    author_email="yousouf.taghzouti@gmail.com",
    url="https://github.com/YoucTagh/rdf-canon/",
    download_url="https://pypi.org/project/rdfcanon/",
    license="MIT",
    license_files=["LICENSE"],
    keywords=[
        "semantics",
        "canonicalisation",
        "RDF",
    ],
    python_requires=">=3.12",
)
