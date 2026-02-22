from setuptools import setup, find_packages

setup(
    name="tracecontext",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "langgraph",
        "langchain-anthropic",
        "psycopg2-binary",
        "redis",
        "click",
        "requests",
        "python-dotenv",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "tracecontext=tracecontext.cli:main",
        ],
    },
    author="TraceContext Team",
    description="Persistent AI coding context platform",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tracecontext/tracecontext",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
