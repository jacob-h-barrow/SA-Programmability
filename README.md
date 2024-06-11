# SA Programmability

## Why
- Writing all of your own SQLAlchemy ORM queries can take time and tend to be redundant. 

## What drove this
- IBM's Service Classes and Network Programmability

## What is Human and what's AI
- The format and concept behind SA Programmability is 100% copyrighted by Jacob H. Barrow 2024.
- Some of the code is written by ChatGPT.
- The format is really what is important, the code can be rewritten without AI in the future.

## The QueryBuilder Class
### Good
- Does read loaded json
- Provides basic insert, select, and select.returning queries
### Bad
- Doesn't provide insert.returning
- Filtering is limited
- No joins/one table only
- Doesn't do update or deletes

## Purpose
- PoC to see if it was worth investing time in

## Future
- Streams
- Bad section fixes
- Decoupled/Custom UoW query builder.... important for sharded/distributed databases
