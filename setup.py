from setuptools import find_packages, setup

requirements = [
    'cython', 'googleapis-common-protos', 'grpcio-tools', 'h5py', 'imgaug',
    'keras', 'numpy', 'opencv-python', 'Pillow', 'scikit-image', 'scipy'
]

setup(
    name='mask-rcnn-serving',
    version='0.1',
    description='Mask R-CNN serving',
    author='Linker Networks',
    author_email='info@linkernetworks.com',
    url='https://www.linkernetworks.com',
    packages=find_packages(),
    install_requires=requirements)
