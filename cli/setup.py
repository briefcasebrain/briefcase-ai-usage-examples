#!/usr/bin/env python3
"""
Setup configuration for Briefcase AI Telemetry CLI tools.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="briefcase-ai-cli",
    version="0.1.0",
    author="Aansh Shah",
    author_email="aansh@briefcasebrain.com",
    description="CLI tools for Briefcase AI Telemetry SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk",
    project_urls={
        "Bug Reports": "https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk/issues",
        "Source": "https://github.com/briefcasebrain/briefcase-ai-telemetry-sdk",
        "Documentation": "https://docs.briefcasebrain.com",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "rich>=10.0.0",  # For enhanced terminal output
        "briefcase-ai-telemetry-sdk>=0.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "isort>=5.0",
            "mypy>=0.990",
        ],
    },
    entry_points={
        "console_scripts": [
            "briefcase-ai=briefcase_ai_cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "briefcase_ai_cli": ["templates/*", "assets/*"],
    },
)