from setuptools import setup, find_packages

# List of files to install relative to root dir containing setup.py
files = [""]
setup(
    name="mriqa",
    version="1.0dev",
    description="MRI Image QA",
    author="Nana Mensah",
    author_email="Nana.mensah1@nhs.net",
    url=".",
    packages=find_packages(),
    include_package_data=True,
    install_requires=['pydicom'],
    python_requires='>=3',
    scripts=['scripts/mriqa']
    )
