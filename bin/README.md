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