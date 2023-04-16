from setuptools import setup, find_packages

setup(name='tsp-solver',
      version='1.0',
      description='A TSP, VRP solver service',
      author='Ehsan Maiqani',
      author_email='ehsan.maiqani@gmail.com.com',
      packages=find_packages(),
      install_requires=[
          'absl-py==1.4.0',
          'aio-pika==9.0.5',
          'aiormq==6.7.4',
          'idna==3.4',
          'multidict==6.0.4',
          'numpy==1.24.2',
          'ortools==9.6.2534',
          'pamqp==3.2.1',
          'protobuf==4.22.3',
          'pydantic==1.10.7',
          'scipy==1.10.1',
          'typing_extensions==4.5.0',
          'yarl==1.8.2'
      ],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ])
