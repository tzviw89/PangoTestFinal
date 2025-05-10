from setuptools import setup, find_packages

setup(
    name="automation_framework",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "playwright",
        "requests",
        "python-dotenv",
        "dash",
        "plotly",
        "pandas"
    ],
) 