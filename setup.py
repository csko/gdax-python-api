from setuptools import setup, find_packages

setup(
      name='gdax-python-api',
      version='0.2',
      description='GDAX API client written in Python3 using async/await',
      url='https://github.com/csko/gdax-python-api',
      license='MIT License',
      keywords='gdax gdax-api gdax-python python3 python-3.6 coinbase '
               'coinbase-api bitcoin ethereum litecoin trading-api',
      author='Kornel Csernai',
      author_email='cskornel@gmail.com',
      install_requires=[
        'aiohttp==3.8.1',
        'aiofiles==0.3.1',
        'async_timeout==1.2.1',
        'sortedcontainers==1.5.9',
      ],
      packages=find_packages(),
      include_package_data=True,
      platforms='any',
      tests_require=[
        'pytest',
      ],
      classifiers=[
        'Programming Language :: Python :: 3 :: Only',
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
