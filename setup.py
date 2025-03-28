from setuptools import setup, find_packages

setup(
    name="emailsender",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4==4.12.3',
        'requests==2.31.0',
        'dnspython==2.5.0',
        'python-dotenv==1.0.1',
        'pytest==8.0.2',
        'firebase-admin==6.4.0'
    ]
) 