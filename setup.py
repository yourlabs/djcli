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
    entry_points={
        'console_scripts': [
            'djcli = djcli:_cli',
        ],
    },
    install_requires=['tabulate', 'clitoo'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Database',
        'Topic :: Software Development',
        'Topic :: System',
        'Topic :: Terminals',
    ],
    python_requires='>=3',
)
