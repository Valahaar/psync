from setuptools import setup, find_packages

setup(
    name="psync",
    version="0.1.0",
    description="A glorified rsync for quickly synchronizing projects across machines.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ],
    keywords="psync project synchronization sharing",
    url="https://github.com/Valahaar/psync",
    author="Niccolò Campolungo",
    author_email="campolungo@di.uniroma1.it",
    license="Apache",
    packages=find_packages(where='.'),
    install_requires=[
        "jsonargparse==3.16.0",
        "omegaconf==2.1.0",
    ],
    entry_points={"console_scripts": ["psync=psync.application:run"]},
    # include_package_data=True,
    python_requires=">=3.8.0",
    zip_safe=False,
)
