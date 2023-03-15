from setuptools import setup

setup(
    name="bookmrk",
    version="1.0.0",
    description="A simple bookmark manager.",
    author="Sarvesh Rane",
    author_email="sarveshrane2000@gmail.com",
    url="https://github.com/sarveshrane2000/bookmrk",
    license="MIT",
    py_modules=["main"],
    install_requires=[
        "click==8.1.3",
        "rich==13.3.2",
        "tinydb==4.7.1"
    ],
    entry_points={
        "console_scripts": [
            "bookmrk = main:cli",
        ],
    }
    )