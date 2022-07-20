import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="locust_influxdb_listener", # Replace with your own username
    version="0.0.5",
    author="Pablo Calvo",
    author_email="pjcalvov@gmail.com",
    description="Locust.io 1.X influxdb listener",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hoodoo-digital/locust_influxdb_listener",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'locust>=2.8.0',
        'influxdb>=5.2.2',
    ],
    python_requires='>=3.6',
)