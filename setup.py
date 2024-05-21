from setuptools import setup

setup(
    name="uhubctl",
    version="0.1.2",
    author="Nicolai Buchwitz",
    author_email="nb@tipi-net.de",
    description="A basic Python wrapper for uhubctl",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/nbuchwitz/python3-uhubctl",
    packages=["uhubctl"],
    python_requires=">=3.5",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={"Bug Tracker": "https://github.com/nbuchwitz/python3-uhubctl/issues"},
)
