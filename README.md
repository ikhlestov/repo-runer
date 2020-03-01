Small project that may clone repository, build Dockerfile inside it and run that image.

## Installation

To use this script you should have installed in advance:

- Docker
- Git
- Python >= 3.6

To install project execute `pip install git+https://github.com/ikhlestov/repo-runer.git`. Note: as you know it's better to install everything inside virtualenv.

## Usage

- Run `$ repo-runner --help` to see available options
- Run `$ repo-runner` to execute with default parameters

## TODO

- [ ] Check how everything works without Git, Docker or Python
- [ ] Check that docker container is running and respond to requests
- [ ] Provide tests
