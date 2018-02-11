from setuptools import setup, find_packages

setup(
    name="DanaCompiler",
    version="0.9.0",
    author="Aimilios Tsalapatis",
    author_email="emiltsal@yahoo.gr",
    url="",
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        "ply >= 3.1.0",
        "llvmlite >= 0.21.0",
    ],
)
