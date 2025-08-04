from setuptools import setup, find_packages

setup(
    name="dr_driving_bot",
    version="2.1.0",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot==20.3",
        "python-dotenv==1.0.0",
        "peewee==3.17.0",
        "apscheduler==3.10.1",
    ],
)
