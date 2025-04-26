# Ethical Computing Architecture Guide

## Layered Architecture Overview

This project follows a layered architecture pattern to organize code in a way that promotes separation of concerns, maintainability, and testability. The code is organized into three main layers:

```
bin/
└── Entry point scripts that parse command line arguments and call features

src/
└── domain/
    ├── features/  - High-level business capabilities
    ├── services/  - External system interactions
    └── libs/      - Domain-specific business logic
```

### Layers Explained

#### 1. Entry Points (`bin/`)

Entry point scripts are the command-line interfaces to our application. They:
- Parse command-line arguments
- Call appropriate features
- Format and display results
- **Should only call features, not services or libs directly**

#### 2. Features Layer (`src/domain/features/`)

Features represent high-level capabilities of the system. They:
- Implement multi-step business processes
- Orchestrate calls to services and libs
- Handle the main business workflows
- Are focused on "what" the system does

#### 3. Services Layer (`src/domain/services/`)

Services handle all external system interactions. They:
- Provide interfaces to external systems (file system, databases, APIs)
- Handle I/O operations
- Manage external resources
- Abstract away the "how" of external interactions

#### 4. Libs Layer (`src/domain/libs/`)

Libs contain pure business logic functions. They:
- Have no direct external dependencies
- Don't access file systems, databases, or external APIs directly
- Perform calculations, transformations, and business rule evaluations
- Are highly testable with unit tests

## Dependency Rules

The architecture follows these dependency rules:

1. Entry points can call features
2. Features can call services and libs
3. Services can call other services and libs
4. Libs can call other libs
5. **Lower layers should not depend on higher layers**

```
Entry Points → Features → Services → Libs
                 ↓          ↓
                 └──────────→ Libs
```

## Example: Trust Chain Certification

In the trust chain certification system:

1. **Entry Point** (`bin/trust_certification.py`):
   - Parses command-line arguments
   - Calls the trust certification feature

2. **Feature** (`src/trust_chain/features/certification.py`):
   - Orchestrates the complete certification process
   - Calls services to find files, read content, and update registry
   - Calls libs to determine certification status and process node content

3. **Services** (`src/trust_chain/services/`):
   - `file_services.py`: Handles file reading/writing
   - `embedding_services.py`: Manages embedding model interactions
   - `registry_services.py`: Manages trust registry operations

4. **Libs** (`src/trust_chain/libs/`):
   - `certification.py`: Contains certification status determination logic
   - `enhanced_analysis.py`: Implements analysis algorithms for response patterns

## Best Practices

1. Keep dependencies flowing downward
2. Services should encapsulate all I/O operations
3. Libs should be pure functions without side effects
4. Features should orchestrate the business process
5. Each layer should have a clear responsibility 