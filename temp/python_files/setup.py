"""Setup script for the package."""
from setuptools import setup, find_packages

setup(
    name="code-safe-utils",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "psutil",
    ],
    python_requires=">=3.8",
)
