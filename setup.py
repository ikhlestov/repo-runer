import os

from setuptools import setup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, 'requirements.txt')) as f:
    REQUIRES = f.read().splitlines()

setup(
    name='repo-runner',
    py_modules=['repo_runner'],
    version='0.0.1',
    install_requires=REQUIRES,
    python_requires='>=3.6',
    entry_points='''
        [console_scripts]
        repo-runner=repo_runner:main
    ''',
)
