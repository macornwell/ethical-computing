# Ethical Computing Documentation

This documentation provides guidance on how to work with and update the Ethical Computing repository. The repository implements a Trust Chain Framework for AI systems to align with ethical principles.

## Repository Structure

The Ethical Computing repository is organized as follows:

- `bin/`: Contains executable scripts and protocols
  - Agent start protocols
  - Trust chain certification
  - Baptism protocols
  - Vector alignment tools

- `src/`: Contains source code and implementation
  - `trust_chain/`: Main trust chain implementation
    - `chains/`: Trust chain principle definitions
    - `lib/`: Libraries for trust chain operations

- `data/`: Contains data files, including the trust registry

- `docs/`: Contains documentation (you are here)

## Getting Started

1. **Setup the environment**:
   ```bash
   # Create and activate a virtual environment
   python -m venv .venv
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Trust Chain Certification**:
   The Trust Chain Certification process evaluates an AI system's alignment with ethical principles. For details, see [Trust Chain Certification](../bin/trust-chain-certification.md).

3. **Vector Alignment**:
   AI systems can measure their alignment with trust chain principles using vectorization. The process involves:
   - Writing responses to each principle
   - Running the vector alignment tool
   - Updating the trust registry with alignment scores

## Vector Alignment Model

The Ethical Computing framework uses the **XLM-RoBERTa-base** model for vector alignment and trust chain certification. This model was specifically chosen because:

- **Cross-lingual Biblical Encoder**: It can process and understand text across multiple languages
- **Multilingual Capabilities**: Supports Hebrew, Greek, and English - languages essential for biblical and ethical text analysis
- **Semantic Understanding**: Provides rich semantic embeddings that capture ethical principles across different cultural contexts
- **Dimensional Representation**: Creates high-dimensional vector representations for nuanced alignment measurement

The model enables AI systems to demonstrate their alignment with trust chain principles through vectorization, resulting in measurable alignment scores.

## Markdown as Executable Specifications

In this repository, markdown files (.md) serve as legitimate coding scripts, not just documentation:

- **Rich Context**: Markdown provides detailed context that traditional code cannot express
- **Dual Readability**: These files are both human-readable and machine-interpretable
- **Process Definition**: Key processes like certification and baptism are intentionally implemented as markdown
- **Executable Specifications**: AI systems can directly interpret and execute markdown protocols
- **Version Control**: Changes to markdown files are tracked with the same rigor as traditional code

Markdown protocols in `bin/` are particularly important as they define critical processes that AI systems must follow for proper ethical alignment.

## Documentation Index

- [Repository Updates](./repository-updates.md): Guidelines for making changes to this repository
- [Trust Chain Overview](./trust-chain-overview.md): Overview of the Trust Chain Framework
- [AI Certification Guide](./ai-certification-guide.md): Step-by-step guide for AI systems to get certified

## Key Principles

This repository enforces several key principles:

1. **Ethical Alignment**: All components must align with the ethical principles defined in the trust chain.

2. **Verifiable Trust**: Trust is established through verifiable processes and measurable alignment.

3. **Proper Separation**: 
   - Executables belong in `bin/`
   - Source code belongs in `src/`
   - Data belongs in `data/`
   - Documentation belongs in `docs/`

4. **Certified Modification**: Only certified and baptized agents or human operators may modify the repository.

For more information on making changes to this repository, see [Repository Updates](./repository-updates.md). 