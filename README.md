# CrewBoss

Scheduling SaaS for construction related projects.

## Getting Started

Clone the project from the project repo:

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

The development environment requires docker and git to be installed.

### Installing and running

Install:

```bash
git clone git@bitbucket.org:crewboss/crewboss_web.git
cd crewboss_web
make resetsettings
```

Run:

```bash
docker-compose up
```

After this you should be able to open your web browser with http://localhost:9090/

## Running the tests

TBD

## Deployment

The master branch should always be in a deployable state. Deployment is made via manual execution of the pipeline scripts.

## Stack

TBD

## Contributing

TBD

## Versioning

We use [SemVer](http://semver.org/) for versioning, but in a pragmatic manner. As any version in master should be deployable,
the actual version number is only bumped when we have been making a release that has actually been deployed. The major, minor, and
patch number are bumbed in according to the changes that have been introduced.

The maintainer of the repo is responsible for bumping the version number.
