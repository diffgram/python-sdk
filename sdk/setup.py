import setuptools
import diffgram.__init__ as init

try:
    with open(".././README.md", "r") as fh:
        long_description = fh.read()
except:
    long_description = "None"

setuptools.setup(
    name = init.__name__,
    version = init.__version__,
    author="Diffgram",
    author_email="support@diffgram.com",
    description="SDK for Diffgram",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/diffgram/python-sdk",
    packages=setuptools.find_packages(
		exclude=["test", "samples", "ops_scripts", "__pycache__"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	install_requires=[
	   'requests>=2.20.1',
	   'scipy>=1.1.0',
	   'six>=1.9.0',
	   'pillow>=6.1.0',
       'imageio>=2.9.0'
	]
)