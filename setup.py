import pip
from setuptools import find_packages, setup

setup(
    name='model_serving',
    version='0.1',
    description='Machine learning model serving',
    author='Linker Networks',
    author_email='info@linkernetworks.com',
    url='https://www.linkernetworks.com',
    packages=find_packages(),
    install_requires=[
        str(r.req) for r in pip.req.parse_requirements(
            'requirements.txt', session=pip.download.PipSession())
    ])
