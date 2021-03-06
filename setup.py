import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

DEPENDENCIES = [
    "Django>=1.10",
    "celery>=3.1.25",
    "eth-utils>=0.7.0",
    "django-solo>=1.1.0",
    "web3>=3.16.4",
]
TEST_DEPENDENCIES = [
    "eth-testrpc>=1.3.3",
]

setup(
    name='django-ethereum-events',
    version='0.1.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=DEPENDENCIES,
    tests_require=TEST_DEPENDENCIES,
    extras_require={
        "test": TEST_DEPENDENCIES,
    },
    license='MIT License',
    description='Django Ethereum Events',
    long_description=README,
    url='https://github.com/artemistomaras/django-ethereum-events',
    author='Artemios Tomaras',
    author_email='artemistomaras@gmail.com',
    keywords='django ethereum',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
