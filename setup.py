from setuptools import setup

setup(
    name='audiocli',
    version='0.1',
    py_modules=['audi-explorer'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        audiocli=audiocli:cli 
    ''',
)