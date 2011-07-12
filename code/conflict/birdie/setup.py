import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'repoze.zodbconn',
    'repoze.tm2>=1.0b1', # default_commit_veto
    'repoze.retry',
    'ZODB3',
    'appendonly',
    'cryptacular',
    'WebError',
    ]

setup(name='birdie',
      version='0.9',
      description='A simple twitter clone using Pyramid',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Carlos de la Guardia',
      author_email='carlos.delaguardia@gmail.com',
      url='',
      keywords='web pylons pyramid twitter',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires = requires,
      tests_require= requires,
      test_suite="birdie",
      entry_points = """\
      [paste.app_factory]
      main = birdie:main
      """,
      paster_plugins=['pyramid'],
      )

