from setuptools import setup

setup(
    name='GitHubPRAPI',
    version='1.0',
    description='Module to provide status of the Pull Requests',
    author='Ganesh Kumar J',
    author_email='ganesh.kumar.j@live.com',
    packages=['GitHubPRAPI'],
    install_requires=['flask','urllib3','requests','validators']
)