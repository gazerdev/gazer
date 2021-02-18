from setuptools import setup, find_packages
try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements

reqs = parse_requirements('./requirements.txt', session=False)
try:
    requirements = [str(ir.req) for ir in reqs]
except:
    requirements = [str(ir.requirement) for ir in reqs]

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='gazer',
      version='0.1',
      description='Experimental Local Booru and Booru Client',
      long_description=readme(),
      url='http://github.com/gazerdev/gazer',
      author='gazerdev',
      author_email='gazerdev@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=requirements,
      zip_safe=False)
