from setuptools import setup

setup(
    name="listall",
    version="0.0.2.1",
    description="A flexible directory listing tool for sorting, truncating, collecting files, etc.",
    long_description=open("README.md", encoding="utf-8").read(),  # optional
    long_description_content_type="text/markdown",                # optional if using README.md
    author="Dustin Darcy",
    author_email="dustin@scarcityhypothesis.org",
    url="https://github.com/djdarcy/listall",   # or your repo link
    py_modules=["listall"],  # our script is 'listall.py'
    # If you have other dependencies, list them here:
    install_requires=[
        "pyperclip",
        # e.g., "some_other_package>=1.0"
    ],
    entry_points={
        "console_scripts": [
            # "listall" => the command users will type
            # "listall:main" => the 'main' function inside 'listall' module
            "listall=listall:main",
        ]
    },
    # optional classifiers
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",   # or whatever minimum version
)
