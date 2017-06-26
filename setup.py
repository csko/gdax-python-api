from setuptools import setup, find_packages

setup(
      name='gdax-python-api',
      version='0.1',
      description='GDAX API client written in Python3 using async/await',
      url='https://github.com/csko/gdax-python-api',
      license='MIT License',
      keywords='gdax gdax-api gdax-python python3 python-3.6 coinbase '
               'coinbase-api bitcoin ethereum litecoin trading-api',
      author='Kornel Csernai',
      author_email='cskornel@gmail.com',
      install_requires=[
        'aiohttp==2.2.0',
        'async-timeout==1.2.1',
        'requests==2.18.1',
        'websockets==3.3',
        'bintrees==2.0.7',
      ],
      packages=find_packages(),
      include_package_data=True,
      platforms='any',
      tests_require=[
        'pytest',
      ],
      classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
)
