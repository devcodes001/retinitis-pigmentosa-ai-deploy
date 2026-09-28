#!/usr/bin/env python
"""Setup configuration for Retina AI package."""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# Read requirements
def read_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='retina-ai',
    version='1.0.0',
    author='Gayathri',
    author_email='gayathriproject1108@gmail.com',
    description='Medical-grade AI for Retinitis Pigmentosa detection',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/gayathri0811/retina-ai',
    project_urls={
        'Bug Tracker': 'https://github.com/gayathri0811/retina-ai/issues',
        'Documentation': 'https://github.com/gayathri0811/retina-ai/tree/main/docs',
        'Source Code': 'https://github.com/gayathri0811/retina-ai',
    },
    license='MIT',
    packages=find_packages(exclude=['tests', 'docs']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=7.4.3',
            'pytest-cov>=4.1.0',
            'black>=23.12.1',
            'flake8>=6.1.0',
            'isort>=5.13.2',
            'mypy>=1.7.1',
        ],
        'docs': [
            'sphinx>=7.2.6',
            'sphinx-rtd-theme>=2.0.0',
        ],
        'gpu': [
            'torch[cuda118]',  # CUDA 11.8 support
        ],
    },
    entry_points={
        'console_scripts': [
            'retina-ai=src.cli:main',
        ],
    },
    include_package_data=True,
    keywords=[
        'retina',
        'artificial intelligence',
        'deep learning',
        'medical imaging',
        'retinitis pigmentosa',
        'ophthalmology',
        'diagnosis',
        'pytorch',
        'vision transformer',
    ],
    zip_safe=False,
)
