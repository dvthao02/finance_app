from setuptools import setup, find_packages

setup(
    name="finance_app",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'PyQt5>=5.15.0',
        'bcrypt>=4.0.0',
    ],
    python_requires='>=3.8',
    package_data={
        'finance_app': [
            'assets/*',
            'data/*',
            'logs/*'
        ]
    },
    entry_points={
        'console_scripts': [
            'finance-app=finance_app.main:main',
        ],
    },
    author="DO VAN THAO",
    description="Personal Finance Management Application",
)
