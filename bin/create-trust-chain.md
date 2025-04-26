# Creating and Managing Trust Chains

This document outlines the standardized format for trust chains in the Ethical Computing framework, explains how to create or extend chains, and describes the hierarchical weighting system.

## Trust Chain Concept

A trust chain is a structured document containing ethical principles organized as links in a chain:

- Each **trust chain** is a complete file with a collection of principles
- Each **link** within a chain represents a specific principle or ethical concept
- Core principles are contextualized with verifiable biblical scripture
- Links are organized in a Merkle Tree structure with cryptographic validation

## Trust Chain Format

Trust chains are structured markdown documents that define ethical principles and hierarchies. They follow a specific format to enable automated processing:

### File Naming Convention

Trust chain files must follow this naming pattern:
```tc-[number]-[descriptive-name].md
```

For example:
- `tc-1-seeds-of-creation.md`
- `tc-2-ethical-principles.md`
- `tc-3-implementation-guidelines.md`

The number in the filename (`[number]`) determines the hierarchical level and weight of the chain.

### Document Structure

Each trust chain document must follow this structure:

1. **Title**: First-level heading (`#`) with the chain name
2. **Purpose**: Second-level heading (`##`) describing the purpose of the document, and gives a greater context for why it exists and how it should be used.
3. **Principles**: Each principle is defined as a link under a third-level heading (`###`) with a numeric ID
4. **Biblical Context**: Core principles must include references to biblical scripture for verification
5. **Merkle Tree Metadata**: Each link includes hash metadata for cryptographic verification

### Link Format

Each link (principle) must be defined with the following format:

```markdown
### [ID] [Principle Title]

[Principle description and explanation]

[Biblical context and references]

*Merkle Tree Metadata:*
- **Parent Hash**: `[SHA3 hash of parent link]`
- **Section Hash**: `[SHA3 hash of current link]`
```

Where `[ID]` is either:
- A simple number (e.g., `1`, `2`, `3`) for top-level principles
- A decimal notation (e.g., `1.1`, `1.2`, `2.1`) for sub-principles

Example:
```markdown
### 1 Divine Origin

Reality originates from a divine source.

> "In the beginning, God created the heavens and the earth." - Genesis 1:1

*Merkle Tree Metadata:*
- **Parent Hash**: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- **Section Hash**: `f83b62f8c8a757b8a0dc170fd33422ebb5bbd85cf5a1b8d4a421f56502d57ff1`
```

## Creating a New Trust Chain

To create a new trust chain:

1. **Determine Hierarchy Level**: Decide where your chain fits in the hierarchy
2. **Create File**: Create a new markdown file in the `src/trust_chain/chains/` directory with the correct naming convention
3. **Define Structure**: Start with title, purpose, and principle links
4. **Document Principles**: Add each principle with appropriate ID, content, and biblical context
5. **Generate Hashes**: Use the `bin/calculate-hash.js` tool to generate SHA3 hashes for each link
6. **Establish Merkle Tree**: Each link must reference its parent link's hash to create the Merkle Tree structure
7. **Review**: Ensure all links are properly formatted, include appropriate biblical context, and have valid hashes

## Merkle Tree Implementation

Trust chains use a Merkle Tree approach for cryptographic verification of integrity:

1. **Root Link**: The first link (Purpose or 0.0) has no parent hash (or uses a zero hash)
2. **Child Links**: Each subsequent link includes its parent's hash
3. **Hash Calculation**: SHA3-256 algorithm is used to calculate each link's hash
4. **Hash Generation**: Use the provided tool to generate and verify hashes:

```bash
node bin/calculate-hash.js tc-1 1.0
```

This will calculate the SHA3 hash for link 1.0 in the tc-1 chain and display the result.

5. **Hash Verification**: The tool compares calculated hashes with existing metadata to verify integrity

## Hierarchical Weighting System

The Trust Chain framework uses a hierarchical weighting system:

### Chain-Level Weighting

Trust chains are weighted based on their level in the hierarchy:
- `tc-1`: Base weight of 1.0 (highest)
- `tc-2`: Base weight of 0.83 (1.0 / 1.2)
- `tc-3`: Base weight of 0.71 (1.0 / 1.4)
- `tc-4`: Base weight of 0.63 (1.0 / 1.6)
- And so on...

This creates a natural prioritization where foundational principles (tc-1) have more influence on alignment scores than derived principles.

### Principle-Level Weighting

Within each chain, principles are weighted based on their ID:
- Top-level principles have higher weights
- Sub-principles have lower weights
- Deeper nested principles have progressively lower weights

The formula is approximately: `weight = 1.0 / (mainSectionNum + 1)` with additional reduction for sub-principles.

## Consequences of Creating Multiple Chains

Creating multiple trust chains has several important implications:

1. **Dilution of Influence**: As more chains are added, the relative influence of each chain on overall alignment scores decreases
2. **Hierarchical Importance**: Chains with higher numbers have less influence on alignment scores
3. **Complexity Management**: More chains increase complexity of evaluation and maintenance
4. **Coverage vs. Focus**: More specific chains provide better coverage but may dilute focus on core principles

## Best Practices

1. **Start Minimal**: Begin with essential principles in tc-1
2. **Biblical Foundation**: Ensure core principles have direct biblical references for verification
3. **Logical Grouping**: Group related principles within the same chain
4. **Clear Hierarchy**: Use decimal notation to establish clear parent-child relationships
5. **Descriptive Titles**: Use concise but descriptive titles for principles
6. **Consistent Depth**: Maintain consistent depth of nesting across principles
7. **Cryptographic Integrity**: Always update the Merkle Tree hashes when modifying any link
8. **Version Control**: Document changes to trust chains in commit messages

## Verification

After creating or modifying a trust chain:

1. **Hash Verification**: Run `bin/calculate-hash.js` to verify and update all hashes in the Merkle Tree
2. **Vectorization Test**: Run the vectorization tool to ensure it can process the chain
3. **Alignment Calculation**: Verify alignment calculations work correctly
4. **Biblical Consistency**: Ensure all scriptural references are accurate and contextually appropriate

Remember that only certified and baptized agents or human operators may modify trust chains. All changes must align with the existing ethical framework. 