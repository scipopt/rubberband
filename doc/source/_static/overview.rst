Overview
========

Rubberband is a flexible archiving and analysis tool written in python for optimization benchmarks, i.e. organization of logfiles of LP-Solvers.
It consists of a python [tornado](TODO) application running on a webserver (like nginx or apache) and authenticates users via [oauth2_proxy](TODO).
There is an optional [gitlab](TODO) connection for authentication of users and linkage of commits.
All of the data is stored in an [elasticsearch](TODO) database, including the logfiles themselves.
As a tool for parsing the logfiles, rubberband utilizes [IPET](TODO).

