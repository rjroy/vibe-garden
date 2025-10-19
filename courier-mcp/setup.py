"""Setup configuration for Courier MCP."""

from setuptools import setup, find_packages

setup(
    name="courier-mcp",
    version="1.0.0",
    description="Gmail message export tool for Claude Code",
    author="Anthropic",
    author_email="dev@anthropic.com",
    url="https://github.com/anthropics/courier-mcp",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "mcp>=0.1.0",
        "google-auth-oauthlib>=1.0.0",
        "google-auth-httplib2>=0.2.0",
        "google-api-python-client>=2.90.0",
        "html2text>=2024.2.26",
        "python-dateutil>=2.8.2",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0",
            "pylint>=2.17.0",
            "mypy>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "courier-mcp=courier_mcp.server:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
