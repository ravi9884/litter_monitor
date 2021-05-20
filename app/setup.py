import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="litter_monitor", # Replace with your own username
    version="0.0.1",
    author="Ravi R",
    author_email="author@example.com",
    description="Litter-monitor package to monitor litter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ravi9884/machine-learning-portfolio",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points = {
        'console_scripts': [
            "litter_monitor = litter_monitor.main:main"
        ]
    }
)