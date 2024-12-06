from setuptools import find_packages, setup

setup(
    name="trading",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "pyupbit>=0.2.34",
        "pyjwt>=2.0.0",
        "python-dotenv",
        "groq",
    ],
    author="iamiks",
    author_email="mineru664500@gmail.com",
    description="A trading module package",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Mineru98/crypto_quant",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
