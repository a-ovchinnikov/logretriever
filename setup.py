from setuptools import setup, find_packages

console_scripts = ['logretriever = logretriever.main:main']

setup(
    name="LogRetriever",
    description="A tool for monitoring Apache logs",
    version='0.1',
    author='Alex O',
    packages=find_packages(exclude=['*tests']),
    entry_points={'console_scripts': console_scripts},
)
