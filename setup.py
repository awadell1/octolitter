from setuptools import setup, find_packages

setup(
    name="octolitter",
    description="Tool for spinning up GitHub Runners",
    version = "0.0.1",
    author="Alexius Wadell",
    author_email="awadell@gmail.com",
    packages=find_packages(),
    install_requires=[
        "requests",
        "GhApi",
    ],
    entry_points={
        "console_scripts": [
            "octolitter=octolitter.cli:cli"
        ]
    }
)
