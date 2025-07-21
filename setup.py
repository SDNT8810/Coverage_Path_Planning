from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="field-coverage-planner",
    version="1.0.0",
    author="davoud nikkhouy",
    author_email="davoudnikkhouy@gmail.com",
    description="A Python library for generating optimal coverage paths for agricultural fields",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SDNT8810/field-coverage-planner",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "ros": ["rclpy>=3.0.0"],
        "dev": ["pytest>=6.2.0", "pytest-cov>=2.12.0", "black>=21.0.0", "flake8>=3.9.0", "mypy>=0.910"],
        "docs": ["sphinx>=4.0.0", "sphinx-rtd-theme>=0.5.0"],
    },
    entry_points={
        "console_scripts": [
            "field-coverage=field_coverage.cli:main",
        ],
    },
)
