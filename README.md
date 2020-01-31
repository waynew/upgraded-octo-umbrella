Git Scraper (this name is rubbish)
==================================

The goal of this project is to be able to scrape issues from GitHub to learn
interesting things about them. In particular, things like lead time,
throughput, cycle time, and capacity. Possibly also bottlenecks? Anyway, here's
a description of what these things mean.


Lead Time
=========

This is the time between when an issue comes in and the issue is closed (if
possible, the associated PR is merged). Technically the lead time would be when
the next release is actually made on the project, but in lieu of that... when
the issue is actually closed is close enough.


Throughput
==========

This is the number of issues that can be closed within a certain time frame.
For instance, we'll figure it out for the last 1 month, 6 months, 12 months,
and all time. Issues with a 'duplicate' label will be excluded from this
figure.


Cycle Time
==========

This is basically the Lead Time in our case.


Capacity
========

Given a unit of time, how many issues can we expect to close? We can look at
this as a function of issues across all time, or only issues opened and/or
closed within that time period.

We'll automatically give it to you for the last 1, 6, 12 months, and all time.


---


Quickstart
==========

Cache the issues (this may take a while):

    git-scrape cache

<!-- might not be accurate to say we'll saturate... -->
Go make a sammich or a cup of beverage. It may be a while. We'll pretty much
saturate your network connection as much as possible. But it'll be a while.

    git-scrape report

This will print out a report of the above. Maybe we'll also have

    git-scrape report --start=<date> --end=<date>

Where both start and end are inclusive. :shrug: But not positive about that one
yet. We'll see how much we get done.
