from setuptools import find_packages, setup

requirements = [
    'cython', 'googleapis-common-protos', 'grpcio-tools', 'h5py', 'imgaug',
    'keras', 'numpy', 'opencv-python', 'Pillow', 'scikit-image', 'scipy'
]

setup(
    name='model_serving',
    version='0.1',
    description='Machine learning model serving',
    author='Linker Networks',
    author_email='info@linkernetworks.com',
    url='https://www.linkernetworks.com',
    packages=find_packages(),
    install_requires=requirements)
