# ATPESC-2013

Welcome to the student-contributed repository for the [Argonne Extreme
Training Program in 2013](http://extremecomputingtraining.anl.gov/),
hosted by [Paul
Messina](https://www.alcf.anl.gov/staff-directory/paul-c-messina) and
the [Argonne Leadership Computing Facility](http://www.alcf.anl.gov/).

You should head to the [official web
site](http://extremecomputingtraining.anl.gov/) for lecture materials,
agenda, and the official participant list.

We're hosting a very informal "competition" based on the Game of Life
slides presented by Bill Gropp, and we'll be running the competition
on two different architectures:

* Cray XK6 (Titan)
* BlueGene/Q (Vesta)
* (other architectures and machines, if available)

We're welcoming code submissions from all students, and the final
evaluation will be performed by a "blue-ribbon" panel selected from
whoever we can find on Thursday, August 8th, at lunch time.

We're still in the process of designing the competition, anybody with
ideas or code to contribute is welcome to submit a [pull
request](https://help.github.com/articles/using-pull-requests). 

You are free to work as individuals or in teams, but at least one
person on the team must be an ASPEC student.  All submissions will be
due Thursday at 8:00 AM, local time.

You may work in any language or environment with your code, but it
*must* pass all of our verification tests to be considered.  We are
currently considering three prizes:

### Performance
### Elegance
### Special Prize

You should be able to get started and test some of the existing code
in the repository with the following commands:

```
git clone git://github.com/ahmadia/atpesc-2013.git
cd atpesc-2013/challenge
python setup.py build_ext -i
python test_life.py
python bench_life.py
```