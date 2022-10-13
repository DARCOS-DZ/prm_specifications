from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in prm_specifications/__init__.py
from prm_specifications import __version__ as version

setup(
	name="prm_specifications",
	version=version,
	description="PRM customisations",
	author="SARL Darcos",
	author_email="contact@darcos.dz",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
