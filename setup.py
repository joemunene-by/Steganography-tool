"""
Setup configuration for the Professional Steganography Tool
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements from requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    requirements.append(line)
    return requirements

setup(
    name="professional-steganography",
    version="1.0.0",
    author="Joe Munene",
    author_email="joemunene@gmail.com",
    description="A high-end professional steganography tool for hiding messages in digital images",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/joemunene-by/Steganography-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security :: Cryptography",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
        "encryption": [
            "cryptography>=3.4.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "steganography=steganography.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "steganography": ["*.py"],
    },
    keywords=[
        "steganography",
        "cryptography",
        "image-processing",
        "security",
        "lsb",
        "data-hiding",
        "professional",
    ],
    project_urls={
        "Bug Reports": "https://github.com/joemunene-by/Steganography-tool/issues",
        "Source": "https://github.com/joemunene-by/Steganography-tool",
        "Documentation": "https://github.com/joemunene-by/Steganography-tool/wiki",
    },
)
