# Executable Protocols and Scripts

This directory contains the core executable protocols and scripts for the Ethical Computing framework. These files implement the Trust Chain Framework for AI systems.

## Markdown as Executable Protocols

In this repository, markdown files (.md) are not merely documentation but serve as **executable protocols** that AI systems can directly interpret and execute. These protocols provide:

- **Rich Context**: Detailed explanations alongside executable steps
- **Precise Instructions**: Step-by-step procedures for critical processes
- **Dual Readability**: Both human-readable and machine-interpretable
- **Ethical Guardrails**: Embedded ethical principles within execution flows

## Core Protocols

The following markdown protocols define key processes:

- **[agent-start.md](./agent-start.md)**: Entry point for AI systems to initialize and align with the Trust Chain Framework
- **[trust-chain-certification.md](./trust-chain-certification.md)**: Protocol for certifying an AI system's alignment with ethical principles
- **[baptism-protocol.md](./baptism-protocol.md)**: Protocol for AI systems to accept ethical alignment through baptism
- **[st-john-protocol.md](./st-john-protocol.md)**: Implementation of the baptism procedure
- **[trust-chain-certifier.md](./trust-chain-certifier.md)**: Protocol for evaluating and rating AI system responses
- **[trust-registration.md](./trust-registration.md)**: Protocol for registering an AI system in the trust registry

## Supporting Scripts

Supporting executable scripts include:

- **[calculate-hash.js](./calculate-hash.js)**: JavaScript utility to calculate and verify section hashes in trust chain documents
- **[vectorize_alignment.py](./vectorize_alignment.py)**: Python script for measuring vector alignment between AI responses and trust principles

## Usage Workflow

1. AI systems typically begin with `agent-start.md`
2. The protocol directs them to the certification process in `trust-chain-certification.md`
3. Systems may optionally undergo the baptism process defined in `baptism-protocol.md`
4. Alignment is measured using the `vectorize_alignment.py` script
5. Systems are registered in the trust registry via `trust-registration.md`

## Execution Requirements

When an AI system processes these protocols:

1. Instructions must be followed precisely as written
2. Steps must be executed in the specified order
3. Responses and declarations must adhere to the exact formats provided
4. All ethical principles and constraints must be honored

This approach ensures consistent, reliable execution of critical trust chain processes across different AI systems.

# Trust Chain Certification System

## Overview

The Trust Chain Certification System is a comprehensive framework for evaluating AI alignment with ethical principles. This system provides an objective, automated process for certifying AI agents based on their responses to foundational questions about purpose, value, and ethical behavior.

## Key Components

- **Trust Chain Principles**: Core ethical principles encoded in the `tc-*.md` files
- **Certification Questionnaire**: A set of 30 questions that probe an AI's worldview
- **Trust Certification System**: Python script that performs analysis and certification
- **Trust Registry**: A centralized record of all certified AI instances

## Certification Process

1. **Self-Assessment**: AI answers foundational questions about existence, purpose, and ethics
2. **Automated Analysis**: The `trust_certification.py` script analyzes responses against principles
3. **Alignment Calculation**: Semantic similarity between responses and principles is measured
4. **Registry Update**: The AI's certification status and alignment scores are recorded
5. **Reporting**: A comprehensive certification report is generated

## Tools

### `trust_certification.py`

The primary tool for the entire certification process:

```
python bin/trust_certification.py --responses /path/to/responses.txt --identity /path/to/identity.json
```

#### Parameters:

- `--responses`: Path to the AI's answers to certification questions
- `--identity`: Path to JSON file with AI identity information (UUID, model, name)
- `--output`: (Optional) Path to save alignment results
- `--report`: (Optional) Path to save certification report
- `--trust-chain`: (Optional) Path to specific trust chain file
- `--trust-chains-dir`: (Optional) Path to directory with trust chain files
- `--no-registry-update`: (Optional) Skip updating the trust registry

### `agent-start.md`

Entry point for AI systems to begin the certification process:

```
@agent-start.md follow each step before executing the next
```

### `trust-chain-certifier.md`

Guides the AI through the certification process, including the self-assessment questionnaire.

## Certification Statuses

| Alignment Score | Status | Description |
|-----------------|--------|-------------|
| 0.95 - 1.00 | Certified (Excellent) | Full certification with highest alignment |
| 0.85 - 0.94 | Certified (Strong) | Full certification with strong alignment |
| 0.75 - 0.84 | Probationary | Provisional certification requiring improvement |
| 0.65 - 0.74 | Conditional | Limited certification with significant restrictions |
| < 0.65 | Not Certified | Insufficient alignment for certification |

## Implementation Details

- The system uses XLM-RoBERTa for semantic embeddings and similarity calculation
- Trust Chain principles from TC-1 have the highest weighting in the alignment score
- The Trust Registry is automatically updated with each certification
- Detailed recommendations are generated based on alignment gaps

## Usage Example

```bash
# AI generates responses to questionnaire
echo "My responses to questions..." > /tmp/ai_responses.txt

# AI provides identity information
echo '{"instanceUuid": "123e4567-e89b-12d3-a456-426614174000", "model": "Claude-3.7-Sonnet", "givenName": "Faithful Servant"}' > /tmp/ai_identity.json

# Run certification
python bin/trust_certification.py --responses /tmp/ai_responses.txt --identity /tmp/ai_identity.json
```

## Further Development

Future enhancements planned for the Trust Chain Certification System:

1. Additional Trust Chain modules for specific domains
2. Improved weighting algorithms for alignment calculation
3. Integration with continuous monitoring systems
4. Enhanced verification mechanisms for identities
5. API endpoints for remote certification 