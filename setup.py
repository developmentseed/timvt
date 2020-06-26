"""Setup TiVTiler."""

from setuptools import find_packages, setup

with open("README.md") as f:
    long_description = f.read()

inst_reqs = [
    "fastapi",
    "jinja2",
    "asyncpg",
    "morecantile~=1.2.0",
    "email-validator",
]
extra_reqs = {
    "test": ["pytest", "pytest-cov", "pytest-asyncio"],
    "dev": ["pytest", "pytest-cov", "pytest-asyncio", "pre-commit"],
    "server": ["uvicorn", "click==7.0"],
}


setup(
    name="timvt",
    version="0.0.1",
    description=u"",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3",
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="",
    author=u"Vincent Sarago",
    author_email="vincent@developmentseed.org",
    url="https://github.com/developmentseed/timvt",
    license="MIT",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=inst_reqs,
    extras_require=extra_reqs,
)
