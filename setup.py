from setuptools import setup, find_packages

setup(
    name='pytivoclient',
    version='0.1',
    packages=find_packages(),
    license='BSD License',
    description='List and download recordings from a TiVo device.',
    author='Jeremy Muhlich',
    author_email='jmuhlich@bitflood.org',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    entry_points={
        'console_scripts': [
            'pytivoclient = pytivoclient.main:main'
        ],
        'pytivoclient.app': [
            'ls = pytivoclient.main:List',
            'dir = pytivoclient.main:List',
            'cd = pytivoclient.main:Chdir',
        ],
    },
    install_requires=[
        "cliff >= 1.4",
        "usersettings >= 1.0",
        "requests >= 2.0",
        ],
)
