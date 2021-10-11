"""Setup timvt."""

from setuptools import find_packages, setup

with open("README.md") as f:
    long_description = f.read()

inst_reqs = [
    "asyncpg>=0.23.0",
    "buildpg>=0.3",
    "fastapi>=0.65,<0.68",
    "jinja2>=2.11.2,<3.0.0",
    "morecantile>=3.0.0a1,<3.1",
    "starlette-cramjam>=0.1.0,<0.2",
    "dataclasses;python_version<'3.7'",
    "async_exit_stack>=1.0.1,<2.0.0;python_version<'3.7'",
    "async_generator>=1.10,<2.0.0;python_version<'3.7'",
    "importlib_resources>=1.1.0;python_version<'3.9'",
]

test_reqs = [
    "pytest",
    "pytest-cov",
    "pytest-asyncio",
    "requests",
    "psycopg2",
    "pytest-pgsql",
    "mapbox-vector-tile",
    "numpy",
]

extra_reqs = {
    "test": test_reqs,
    "dev": test_reqs + ["pre-commit"],
    "server": ["uvicorn[standard]>=0.12.0,<0.14.0"],
    "docs": [
        "nbconvert",
        "mkdocs",
        "mkdocs-material",
        "mkdocs-jupyter",
        "pygments",
        "pdocs",
    ],
}


setup(
    name="timvt",
    description=u"",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="FastAPI MVT POSTGIS",
    author=u"Vincent Sarago",
    author_email="vincent@developmentseed.org",
    url="https://github.com/developmentseed/timvt",
    license="MIT",
    packages=find_packages(exclude=["tests*"]),
    package_data={"timvt": ["templates/*.html"]},
    include_package_data=True,
    zip_safe=False,
    install_requires=inst_reqs,
    extras_require=extra_reqs,
)
