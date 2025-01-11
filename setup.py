from setuptools import setup, find_packages

def read_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="uruz-framework",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Dependencias
    install_requires=read_requirements("requirements/base.txt"),
    extras_require={
        "dev": read_requirements("requirements/dev.txt"),
        "test": read_requirements("requirements/test.txt"),
    },
    
    # Metadatos
    author="Tu Nombre",
    description="Framework para la creación de sistemas multiagente con IA",
    long_description=open("README.txt").read(),
    long_description_content_type="text/plain",
    
    # Entry points para CLI
    entry_points={
        'console_scripts': [
            'uruz=uruz.cli:cli',
        ],
    },
    
    python_requires=">=3.8",
) 