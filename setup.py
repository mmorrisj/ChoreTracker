from setuptools import setup, find_packages

setup(
    name="ChoreTracker",
    version="0.1.0",
    description="A chore tracking web app for families to manage and reward kids' tasks.",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/mmorrisj/ChoreTracker",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Add main dependencies here, for example:
        "Flask",  # if using Flask as the web framework
        "SQLAlchemy",  # if using SQLAlchemy for database interaction
        # add more dependencies as required by your app
    ],
    extras_require={
        "dev": [
            "pytest",  # or another testing framework
            "flake8",  # for linting
            "black",  # for code formatting
            # other development dependencies
        ]
    },
    entry_points={
        "console_scripts": [
            "choretracker=app:main",  # Replace 'app' and 'main' with the actual module and function name to start your app
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Adjust if your project uses a different license
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)