# fEMR-OnChain
![Python application](https://github.com/FEMR/fEMR-OnChain-Core/workflows/Python%20application/badge.svg)

**Make sure you run `git submodule init; git submodule update` prior to building the repository.**

The fastest way to get a running version of fEMR OnChain is to install Docker, then to run `docker compose up`.

If the Docker image throws an error telling you that `appMR.urls` can't be resolved, check in with issue #541 to see if it might apply to your experience.

Before contributing, check our [CONTRIBUTING.md](CONTRIBUTING.md) file to ensure you're following our workflow.

## Documentation
Documentation is rebuilt periodically and hosted at https://femr.github.io/fEMR-OnChain-Core/

The RESTful API Swagger is hosted at https://chain.teamfemr.org/swagger and is kept updated as changes are made.
A slightly more interactive version is hosted at http://chain.teamfemr.org/redoc/.
Both of these are also accessible on the Docker image at `/swagger` and `/redoc`.