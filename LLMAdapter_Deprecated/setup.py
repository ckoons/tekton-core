#!/usr/bin/env python

from setuptools import setup, find_packages
import os

requires = [
    'anthropic>=0.10.0',
    'fastapi>=0.103.0',
    'uvicorn>=0.23.2',
    'websockets>=11.0.3',
    'python-dotenv>=1.0.0',
    'sse-starlette>=1.6.5',
    'tekton-core>=0.1.0',  # FastMCP integration
]

setup(
    name="llm-adapter",
    version="0.1.0",
    description="LLM Adapter for Tekton - Unified interface for language model interactions",
    long_description="LLM Adapter provides a unified interface for interacting with various language models including Anthropic Claude, OpenAI GPT, and local models. Supports both HTTP and WebSocket APIs with streaming capabilities.",
    author="Tekton Project",
    author_email="tekton@example.com",
    url="https://github.com/example/tekton",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "llm_adapter": ["config/*.json", "templates/*.html"],
    },
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'llm-adapter=llm_adapter.server:main',
            'llm-adapter-http=llm_adapter.http_server:main',
            'llm-adapter-ws=llm_adapter.ws_server:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)