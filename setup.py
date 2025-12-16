from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rdfcanon",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rdflib==7.5.0",
        "sortedcontainers==2.4.0",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="YoucTagh",
)
