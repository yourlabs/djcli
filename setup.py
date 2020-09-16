from setuptools import setup


setup(
    name='djcli',
    versioning='dev',
    setup_requires='setupmeta',
    author='James Pic',
    author_email='jamespic@gmail.com',
    url='https://yourlabs.io/oss/djcli',
    include_package_data=True,
    license='MIT',
    keywords='django cli',
    python_requires='>=3',
    install_requires=['cli2>=2.2.0', 'tabulate'],
    extras_require={
        'test': [
            'django',
            'pytest',
            'pytest-cov',
            'pytest-django',
            'pytest-mock'
        ],
    },
    entry_points={
        'console_scripts': [
            'djcli = djcli:cli.entry_point',
        ],
    },
)
