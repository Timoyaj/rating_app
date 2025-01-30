"""
Setup configuration for the Content Rating System package.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="content-rating-system",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive system for rating and evaluating content resources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/content-rating-system",
    packages=find_packages(exclude=["tests*", "example.py"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'pytest-mock>=3.11.1',
            'black',
            'pylint',
        ],
    },
    entry_points={
        'console_scripts': [
            'rate-content=example:main',
        ],
    },
    include_package_data=True,
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/content-rating-system/issues",
        "Documentation": "https://github.com/yourusername/content-rating-system/wiki",
        "Source Code": "https://github.com/yourusername/content-rating-system",
    },
)
