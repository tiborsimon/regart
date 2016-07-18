from setuptools import find_packages, setup

setup(
    name='regart',
    version='0.0.1',
    description='Register art generator for ASCII based visual register section descriptions.',
    long_description=("."),
    author='Tibor Simon',
    author_email='tibor@tiborsimon.io',
    url='https://github.com/tiborsimon/regart',
    license='MIT',
    test_suite='test',
    keywords='register, ascii, art, printout, tool, helper, bit, section',
    packages=find_packages(),
    scripts=['bin/regart'],
    install_requires=[
          'mock>=2.0.0',
          'termcolor',
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'Topic :: Utilities',
          'Environment :: Console',
          'Natural Language :: English',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Unix',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
    ],
)
