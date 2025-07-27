from setuptools import setup

setup(
    name="CardCheck",
    version="1.0",
    packages=["cardcheck"],
    install_requires=[
        "pillow",
        "tqdm",  # Marked as optional in code
    ],
    entry_points={
        "console_scripts": [
            "cardcheck=cardcheck.main:rename_cards",
        ],
    }
)
