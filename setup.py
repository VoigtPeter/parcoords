import os
import setuptools


setuptools.setup(
    name="parcoords",
    version="0.1.1",
    author="Peter Voigt",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    license="MIT",
    description="Parallel coordinates plotting",
    long_description=open(os.path.join(os.path.dirname(__file__), "README.md")).read(),
    long_description_content_type="text/markdown",
    keywords=["parallel coordinates", "parallel-coordinates", "plot", "hyperparameter", "visualization"],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]

)
