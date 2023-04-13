from setuptools import setup, find_packages

setup(name='tsp-solver',
      version='1.0',
      description='A TSP, VRP solver service',
      author='Ehsan Maiqani',
      author_email='ehsan.maiqani@gmail.com.com',
      packages=find_packages(),
      install_requires=[
          'absl-py==1.4.0',
          'numpy==1.24.2',
          'ortools==9.6.2534',
          'pika==1.3.1',
          'protobuf==4.22.1',
          'scipy==1.10.1'
      ],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ])
