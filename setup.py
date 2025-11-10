"""Setup script for Ising Life Lab."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="isinglab",
    version="0.1.0",
    author="Mythmaker28",
    description="Experimental framework for CA and Ising systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mythmaker28/ising-life-lab",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "pyyaml>=6.0",
        "pandas>=2.0.0",
    ],
    extras_require={
        "viz": ["matplotlib>=3.7.0", "seaborn>=0.12.0"],
        "dev": ["pytest>=7.3.0", "pytest-cov>=4.1.0"],
    },
    entry_points={
        "console_scripts": [
            "isinglab-scan=isinglab.scan_rules:main",
        ],
    },
)

