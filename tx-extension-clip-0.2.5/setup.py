from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).parent

long_description = (here / "README.md").read_text(encoding="utf-8").strip()

setup(
    name="tx-extension-clip",
    version="0.2.5",
    author="Technology Coalition Org",
    author_email="tech@technologycoalition.org",
    description="Python Library for Threat Exchange CLIP Extension",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TechnologyCoalitionOrg/tx-extension-clip",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "faiss-cpu>=1.7.3",  # faiss
        "numpy>=1.24.2",  # faiss
        "open-clip-torch>=2.32.0", # using currently available latest version with the open clip patch in hasher.py
        "Pillow>=9.4.0",
        "scipy>=1.11.3",
        "threatexchange>=1.0.13",
        "torch>=2.0.1",
        "torchvision>=0.15.2",
        "transformers>=4.34.0",
    ],
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.6",
)
