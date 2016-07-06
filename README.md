# tutu

Tutu is a python web interface for managing a server

![Build Status](https://circleci.com/gh/tutu-management/tutu.svg?style=shield&circle-token=27776cd6fddab4e3325515b139065c197e9d3c3b)

## Setup
At the moment, tutu only manages BIND DNS, and a limited subset of features.

Within tutu.cfg (see testing/tutu.cfg for an example), set the location of your database,
and the three secrets within the main section


### BIND

- Within tutu.cfg, set the location of your zone files.
- Split out your zone declarations into a separate config file (tutu currently
  doesn't understand anything other than zone declarations)
- Point tutu to your named.conf that contains your zone information

## Starting tutu
Currently, there are no instructions for this.