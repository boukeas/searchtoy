from setuptools import setup, find_packages

setup(
    name='searchtoy',
    version='0.1.0',
    description='A library for solving combinatorial search problems',
    long_description='',
    url='https://github.com/boukeas/searchtoy',
    author='George Boukeas',
    author_email='boukeas@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ],
    keywords='combinatorial search optimization problems',
    packages=find_packages(exclude=['examples', 'docs', 'tests'])
)
