from setuptools import setup, find_packages

setup(
    name="dictionote",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple note-taking application",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dictionote",
    packages=find_packages(),
    install_requires=[
        'PyQt6>=6.0.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'dictionote=run:main',
        ],
    },
) 