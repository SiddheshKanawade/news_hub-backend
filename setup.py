from setuptools import find_packages, setup

setup(
    name="news-aggregator",
    packages=find_packages(exclude=["examples"]),
    version="0.1.0",
    description="API service to fetch news and present data for given time frame and location",
    author="Siddhesh Kanawade",
    author_email="siddheshkanawade743@gmail.com",
    url="",
    install_requires=[
        "fastapi==0.112.1",
        "uvicorn[standard]==0.30.6",
        "requests==2.32.3",
        "black==22.3.0",
        "autoflake==1.4",
        "isort==5.9.3",
        "python-jose==3.3.0",
        "passlib==1.7.4",
        "pymongo==4.1.1",
        "pydantic-settings==2.6.0",
        "pydantic[email]==2.9.2",
        "python-multipart==0.0.12",
        "argon2-cffi==23.1.0",
        "tqdm",
        "pandas",
    ],
    setup_requires=[
        "pytest-runner",
    ],
    tests_require=["pytest"],
)
