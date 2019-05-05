from setuptools import setup, find_packages

setup(
    name='audiocli',
    version='0.11',
    packages=find_packages(),
    entry_points='''
        [console_scripts]
        audiocli=audiocli:cli 
    ''',
)