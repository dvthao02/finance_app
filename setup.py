from setuptools import setup, find_packages

setup(
    name="finance_app",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'bcrypt',
        'Pillow',
    ],
    package_data={
        'finance_app': [
            'assets/*',
            'data/*.json',
        ],
    },
    python_requires='>=3.8',
)
