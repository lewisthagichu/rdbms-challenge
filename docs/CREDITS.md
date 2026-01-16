# Credits & Attribution

Complete attribution of all resources, libraries, and assistance used in building MyDB.

---

## Libraries & Dependencies

### Python Libraries

#### sqlparse (0.4.4)

- **Purpose**: SQL tokenization and parsing
- **License**: BSD 3-Clause
- **Author**: Andi Albrecht
- **URL**: https://github.com/andialbrecht/sqlparse
- **Documentation**: https://sqlparse.readthedocs.io/
- **Usage**: Converts SQL strings into structured tokens that we can traverse and extract information from
- **Why Essential**: Writing a full SQL parser from scratch would take months. sqlparse handles the complex tokenization and lets us focus on extraction logic.

#### FastAPI (0.104.1)

- **Purpose**: Web framework for REST API
- **License**: MIT
- **Author**: Sebastián Ramírez (@tiangolo)
- **URL**: https://fastapi.tiangolo.com/
- **Usage**: Powers our REST API endpoints, handles request/response validation, generates automatic documentation
- **Why Chosen**: Modern, fast, automatic data validation, excellent documentation

#### Pydantic (2.5.0)

- **Purpose**: Data validation using Python type hints
- **License**: MIT
- **Author**: Samuel Colvin
- **URL**: https://pydantic.dev/
- **Usage**: Validates request/response data in FastAPI
- **Came with**: FastAPI dependency

#### Uvicorn (0.24.0)

- **Purpose**: ASGI server for running FastAPI
- **License**: BSD
- **Author**: Tom Christie
- **URL**: https://www.uvicorn.org/
- **Usage**: Runs the FastAPI application
- **Why Chosen**: FastAPI's recommended server, supports async

#### python-multipart (0.0.6)

- **Purpose**: Form data parsing
- **License**: Apache 2.0
- **Usage**: Handles multipart form data in FastAPI
- **Came with**: FastAPI dependency

### JavaScript Libraries

#### React (18.2.0)

- **Purpose**: UI library
- **License**: MIT
- **Author**: Meta/Facebook
- **URL**: https://react.dev/
- **Usage**: Frontend web interface components
- **Why Chosen**: Industry standard, component-based architecture, great ecosystem

#### Vite (5.0.0)

- **Purpose**: Build tool and development server
- **License**: MIT
- **Author**: Evan You
- **URL**: https://vitejs.dev/
- **Usage**: Bundles React application, provides hot module replacement
- **Why Chosen**: Faster than Create React App, modern tooling

---

## AI Assistance

### Claude (Anthropic)

**Primary Development Assistant**

**Usage Breakdown**:

- Code Generation: ~60%
- Explanations & Documentation: 100%
- Debugging Assistance: ~40%
- Architecture Guidance: ~50%

**How AI Was Used Responsibly**:

- ✅ Reviewed and understood all generated code
- ✅ Modified code to match specific project needs
- ✅ Used as a learning tool, not just copy-paste
- ✅ Asked "why" questions to understand decisions
- ✅ Attributed AI assistance clearly in documentation
- ✅ Made final architectural decisions myself
- ✅ Tested all code thoroughly

**What I Did Independently**:

- Research and self-study
- Final design decisions
- Integration of components
- Testing and validation
- Project structure
- Requirements gathering
- Feature prioritization

---

## Learning Resources

### Books

#### 1. "Database Internals" by Alex Petrov

- **Publisher**: O'Reilly Media
- **ISBN**: 978-1492040347
- **URL**: https://www.databass.dev/
- **Chapters Used**: 1-5 (Storage Engines, Indexing, B-Trees, Hash Tables)
- **What I Learned**:
  - How databases organize data on disk
  - Why B+ trees are used for indexes
  - Buffer pool management
  - Page layouts and file formats
- **Impact**: Influenced storage layer design, understanding of index structures

#### 2. "Designing Data-Intensive Applications" by Martin Kleppmann

- **Publisher**: O'Reilly Media
- **ISBN**: 978-1449373320
- **URL**: https://dataintensive.net/
- **Chapters Used**: 2-3 (Data Models, Storage and Retrieval)
- **What I Learned**:
  - Trade-offs in database design
  - OLTP vs OLAP systems
  - Hash indexes vs SSTable indexes
  - Transaction isolation levels
- **Impact**: Helped understand high-level architecture decisions

#### 3. "SQL Performance Explained" by Markus Winand

- **URL**: https://sql-performance-explained.com/
- **Chapters Used**: Index basics
- **What I Learned**:
  - How databases use indexes
  - Query execution plans
  - When indexes help vs hurt
- **Impact**: Influenced index design decisions

### Online Courses

#### 1. CMU 15-445: Database Systems (Fall 2023)

- **Instructor**: Andy Pavlo
- **Institution**: Carnegie Mellon University
- **URL**: https://15445.courses.cs.cmu.edu/
- **YouTube**: https://youtube.com/playlist?list=PLSE8ODhjZXjbohkNBWQs_otTrBTrjyohi
- **Lectures Watched**: 1-10
- **Topics**:
  - Storage managers and file organization
  - Buffer pool management
  - Hash tables
  - B+ trees
  - Index concurrency control
- **What I Learned**:
  - Internal workings of storage engines
  - How buffer pools manage memory
  - Different index structures and their trade-offs
- **Impact**: ⭐⭐⭐⭐⭐ **Highly influential** - Best resource for understanding database internals

#### 2. Stanford CS145: Data Management and Data Systems

- **Institution**: Stanford University
- **URL**: https://cs145-fa19.github.io/
- **Topics**:
  - Relational model
  - SQL semantics
  - Query processing
- **What I Learned**:
  - SQL language design
  - Relational algebra
  - Query optimization basics
- **Impact**: Helped understand SQL execution

#### 3. MIT 6.830: Database Systems

- **Institution**: Massachusetts Institute of Technology
- **URL**: http://db.csail.mit.edu/6.830/
- **Lab**: SimpleDB implementation
- **What I Learned**:
  - Step-by-step database construction
  - Buffer pool implementation
  - Join algorithms
- **Impact**: Provided implementation roadmap

### Documentation

#### 1. SQLite Architecture Documentation

- **URL**: https://www.sqlite.org/arch.html
- **Sections Read**: All
- **What I Learned**:
  - Query compilation pipeline
  - Virtual machine execution
  - Component interaction
- **Impact**: ⭐⭐⭐⭐⭐ Excellent overview of production database architecture
- **Diagrams Used**: Referenced architecture diagrams for my own design

#### 2. PostgreSQL Documentation

- **URL**: https://www.postgresql.org/docs/current/
- **Sections Read**:
  - Chapter 11: Indexes
  - Chapter 14: Performance Tips
  - Chapter 50: System Catalogs
- **What I Learned**:
  - Real-world index types (B-tree, Hash, GiST, GIN)
  - EXPLAIN output interpretation
  - How metadata is stored
- **Impact**: Influenced schema manager design

#### 3. FastAPI Documentation

- **URL**: https://fastapi.tiangolo.com/tutorial/
- **Sections Read**: Full tutorial
- **What I Learned**:
  - Request validation with Pydantic
  - Automatic API documentation
  - CORS configuration
- **Impact**: Enabled rapid API development

#### 4. React Documentation

- **URL**: https://react.dev/
- **Sections Read**: Learn React section
- **What I Learned**:
  - Hooks (useState, useEffect)
  - Component composition
  - State management
- **Impact**: Frontend implementation

### Tutorials & Articles

#### 1. "Let's Build a Simple Database" by cstack

- **URL**: https://cstack.github.io/db_tutorial/
- **Format**: Multi-part tutorial
- **What I Learned**:
  - Step-by-step database implementation in C
  - B+ tree implementation details
  - REPL interface design
- **Impact**: ⭐⭐⭐⭐⭐ Excellent hands-on tutorial
- **Code Inspiration**: REPL multi-line input handling

#### 2. "How Does a Database Work?" by Coding Horror

- **Author**: Jeff Atwood
- **URL**: https://blog.codinghorror.com/
- **What I Learned**:
  - High-level database concepts
  - Common pitfalls
- **Impact**: Big-picture understanding

#### 3. "B-Trees and B+ Trees" (Wikipedia)

- **URL**: https://en.wikipedia.org/wiki/B-tree
- **What I Learned**:
  - B+ tree structure and properties
  - Why databases prefer B+ trees
  - Comparison with binary trees
- **Impact**: Understanding of production index structures

#### 4. Real Python Articles

- **URL**: https://realpython.com/
- **Articles Read**:
  - "Python Virtual Environments: A Primer"
  - "Working with JSON Data in Python"
  - "Using FastAPI to Build Python Web APIs"
- **What I Learned**:
  - Python best practices
  - JSON serialization
  - Web API patterns
- **Impact**: Python implementation details

### Stack Overflow

**Key Questions Referenced**:

1. "How does database indexing work?"

   - URL: https://stackoverflow.com/questions/1108/how-does-database-indexing-work
   - Used for: Understanding B-tree vs hash indexes

2. "How does SQL JOIN work?"

   - URL: https://stackoverflow.com/questions/38549/how-does-join-work
   - Used for: JOIN algorithm implementation

3. "SQL parsing in Python"

   - URL: https://stackoverflow.com/questions/5064169/python-sql-query-parser
   - Used for: Choosing sqlparse library

4. "Hash index vs B-tree index"
   - Used for: Index design decisions

### YouTube Videos

#### 1. "Database Indexing Explained" by Hussein Nasser

- **Channel**: Hussein Nasser
- **What I Learned**: Visual explanation of how indexes work
- **Impact**: Helped visualize index structures

#### 2. "How Database JOIN Works" by Computerphile

- **Channel**: Computerphile
- **What I Learned**: Nested loop vs hash join algorithms
- **Impact**: JOIN implementation understanding

#### 3. Various Python/React tutorials

- **Topics**: FastAPI basics, React hooks, async/await
- **Impact**: Implementation details

---

## Code Snippets & Inspiration

### 1. SimpleDB (MIT 6.830 Lab)

- **Language**: Java
- **URL**: http://db.csail.mit.edu/6.830/
- **Inspired**: Storage engine structure, buffer pool concept
- **Modified**: Adapted from Java to Python, simplified for in-memory storage
- **No Direct Copy**: Just architectural inspiration

### 2. cstack's "Let's Build a Database"

- **Language**: C
- **URL**: https://cstack.github.io/db_tutorial/
- **Inspired**: REPL interface design, multi-line input
- **Adapted**: Python implementation, added special commands
- **No Direct Copy**: Conceptual guidance only

### 3. SQLite Source Code

- **Language**: C
- **URL**: https://sqlite.org/src/doc/trunk/README.md
- **Studied**: Parser structure, query execution flow
- **Not Copied**: Read for understanding, not implementation
- **Impact**: High-level architecture understanding

---

## Design & UI Inspiration

### 1. PostgreSQL psql

- **Inspired**: REPL commands (\tables, \describe, \q)
- **Why**: Industry-standard interface, familiar to users
- **Modified**: Simplified output format

### 2. MongoDB Compass

- **Inspired**: Three-panel layout (tables, query, results)
- **Adapted**: For SQL instead of NoSQL
- **Modified**: Simpler, educational focus

### 3. TablePlus

- **Inspired**: Query panel with sample queries
- **Why**: Great for learning and quick testing
- **Modified**: Tailored to MyDB's feature set

---

## Communities & Forums

### Reddit

- **r/Database** - General database discussions
- **r/learnprogramming** - Learning resources
- **r/Python** - Python best practices

### Stack Overflow

- **Tags followed**: python, database, sql, fastapi, react
- **Questions asked**: 2
- **Questions answered**: 0 (still learning!)

### Discord/Slack

- Various programming communities for Python/React help

---

## Acknowledgments

### Pesapal

- For creating an inspiring and challenging technical assessment
- For valuing clear thinking over perfect solutions
- For encouraging the use of AI tools

### Anthropic

- For Claude AI, an invaluable learning and development partner
- For making AI assistance accessible and useful

### Educators

- **Andy Pavlo** (CMU) - Excellent database lectures
- **Joe Hellerstein** (Berkeley) - Database systems course
- **Martin Kleppmann** - DDIA book
- **Alex Petrov** - Database Internals book

### Open Source Community

- **Andi Albrecht** - sqlparse library
- **Sebastián Ramírez** - FastAPI framework
- **Evan You** - Vite and Vue (inspiration)
- **Meta/Facebook** - React library
- All contributors to the libraries used

### Online Resources

- Stack Overflow contributors
- Technical blog authors
- YouTube educators
- Documentation writers

---

## Declaration

I, Lewis Thagichu, declare that:

1. ✅ I understand all code in this project
2. ✅ I have properly attributed all external resources
3. ✅ AI-generated code was reviewed and modified as needed
4. ✅ Learning resources are accurately cited
5. ✅ No code was copied without attribution
6. ✅ Design decisions were made by me, informed by research

**AI Assistance**: ~60% code generation, 100% documentation
**My Contribution**: 40% code generation, Architecture, integration, testing, learning

---

## License Compliance

All dependencies used are under permissive licenses (MIT, BSD, Apache 2.0) that allow:

- Commercial use
- Modification
- Distribution
- Private use

No GPL or other copyleft licenses used (which would require this project to be GPL).

---
