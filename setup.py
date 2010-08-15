from distutils.core import setup

setup(
    name = "loft",
    version = "0.3",
    author = "Tim Fletcher",
    author_email = "tim@timothyfletcher.com",
    description = "The Loft blogging application",
    license = "BSD",
    url = "http://github.com/timfletcher/loft",
    packages = [
        "loft",
        "loft.templatetags",
    ],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ]
)