## Gunka:

Gunka delimits and names the individual steps of any piece of work.
It’s named for the Lojban word *gunka* (“work”).

Gunka is intended to provide an intermediate level of abstraction in large
applications, where the end user won’t be interested in the smallest details
but will want to observe progress and identify problem areas.

This sort of thing is naturally useful under a GUI in, for example, test tools
and system administration. However, Gunka on its own is not a TUI or GUI. It
handles only the encapsulation of each unit of work.

### Work in progress

Gunka is in a pre-alpha stage. An even earlier draft used Trio for concurrency,
but the current plan is to use the standard asyncio library. This decision is
based on the existing plan, as of 2018-07, to add a feature like Trio’s
nurseries to asyncio in Python 3.8 (see [a talk on that](https://www.youtube.com/watch?v=ReXxO_azV-w)), which would make Trio
an unnecessary dependency. Until then, asyncio.gather is used as a placeholder.

### Design goals

* Your user interface can show, in non-technical terms, what your program is
  doing for the user.

* Non-fatal problems are neatly contained and easy to highlight, while
  fatal problems will propagate.

* Logging of work and its output is easy, in real time and in retrospect.

* Units are reusable and can be arbitrarily nested. You don’t have to follow
  a flat recipe structure.

### Installation

Gunka is a regular Python 3 package with an optional, trivial Debian
build target. Refer to the included Makefile.

### Legal

To contact the author, please use the following information:

    Viktor Eikman
    viktor.eikman@gmail.com
    Grevegårdsvägen 164, 42161 Västra Frölunda, SWEDEN

Please submit your contribution to this project for review.

Gunka is licensed as detailed in the accompanying file COPYING.txt.
