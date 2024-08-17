from setuptools import find_packages, setup

setup(
    name="news-aggregator",
    packages=find_packages(exclude=["examples"]),
    version="0.1.0",
    description="API service to fetch news and present data for given time frame and location",
    author="Sagar Verma",
    author_email="sagar@granular.ai",
    url="https://github.com/granularai/weather-api",
    install_requires=[
        "fastapi==0.112.1",
        "uvicorn[standard]==0.30.6",
        "requests==2.32.3",
        "black==22.3.0",
        "autoflake==1.4",
        "isort==5.9.3",
        "tqdm",
    ],
    setup_requires=[
        "pytest-runner",
    ],
    tests_require=["pytest"],
)
