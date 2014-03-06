from distutils.core import setup

setup(
    name='Mycroft',
    version='0.0.1',
    author='Society of Software Engineers',
    packages=['mycroft'],
    url='https://github.com/rit-sse-mycroft/app-templates/tree/master/python',
    license='LICENSE.txt',
    description='Create mycroft applications in python',
    long_description=open('README.md').read(),
    install_requires=[
        "tlslite >= 0.4.6"
    ],
    package_data={'': ['templates/*']}
)
