# 2023-01-23-10-18-46 Rationale for a SQLite Database

Created: 2023-01-23 10:18:46

- simple to interface with in R/Python
- contain all data in a single file
  - don't need to read in multiple files each time
  - can become confusing quickly when there is a separate CSV file for virtual fences, virtual-herds, collars, etc
- can grow to very large size ~281 terabytes
- manage relationships, such as which cow has which collar

Why put together a standardized database?

- consistent data formats and meanings will make sharing analyses and collaboration MUCH easier
- much more conducive to a meta-analysis across institutions
- avoid having each research group 'reinvent the wheel' to develop one-off or proprietary data storage formats
- share analysis code that works (because data is in a standardized format)

Ultimately, we share similar processing steps and data storage problems, and where we can collaborate on these shared processing steps, we all are likely to benefit. Research goals for each individual or institution may differ, and the researcher will still have to figure out how to get their data into a format to answer their research question. But we can potentially speed up that process by providing a shared set of common processing steps that handle the data management and cleaning, and get you to analyzing the data more rapidly.

## Tags

## References

1.
