from pathlib import Path

from setuptools import setup

wemail = Path(__file__).parent / "git_scrape.py"
with wemail.open("r") as f:
    for line in f:
        if line.startswith("__version__"):
            __version__ = line.partition("=")[-1].strip().strip('"').strip("'")
            break

changelog = (Path(__file__).parent / "CHANGELOG.txt").read_text()
readme = (Path(__file__).parent / "README.md").read_text()
long_desc = readme + "\n\n---\n\n" + changelog

tests_require = ["pytest"]
setup(
    name="git-scrape",
    version=__version__,
    author="Wayne Werner",
    author_email="wayne@waynewerner.com",
    url="https://github.com/waynew/upgraded-octo-umbrella",
    py_modules=["git_scrape"],
    entry_points="""
    [console_scripts]
    git-scrape=git_scrape:do_it
    """,
    install_requires=["quiz"],
    long_description=long_desc,
    long_description_content_type="text/markdown",
    tests_require=tests_require,
    extras_require={"test": tests_require, "build": ["wheel"]},
)
