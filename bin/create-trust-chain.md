# Creating and Managing Trust Chains

This document outlines the standardized format for trust chains in the Ethical Computing framework and provides step-by-step instructions for creating or extending chains. You MUST follow these steps IN EXACT ORDER if you need to create a new trust chain. Complete each step fully before moving to the next step.

## Purpose
Trust chains are structured documents containing ethical principles organized as links in a chain, with each link representing a specific principle or ethical concept. These documents form the foundation of the Ethical Computing framework.

## STEP 1: Determine Chain Purpose and Level
STOP and complete the following actions:
1. Decide the purpose of your new trust chain
2. Determine where it fits in the hierarchy of existing chains
3. Choose an appropriate number for your chain (TC-1, TC-2, etc.)
4. Select a descriptive name for your chain
5. DO NOT PROCEED until you have clearly defined the purpose and level

## STEP 2: Create File Structure
STOP and complete the following actions:
1. Create a new markdown file in the `src/trust_chain/chains/` directory
2. Name the file following this pattern: `tc-[number]-[descriptive-name].md`
   - Example: `tc-1-seeds-of-creation.md`, `tc-2-ethical-principles.md`
3. Add the following basic structure:
   - Title (first-level heading `#` with the chain name)
   - Purpose section (second-level heading `##` describing the document's purpose)
   - Space for principles (to be defined in the next step)
4. DO NOT PROCEED until you have created the basic file structure

## STEP 3: Define Principles
STOP and complete the following actions:
1. Define each principle as a link under a third-level heading (`###`) with a numeric ID
2. Use the following format for each link:
   ```markdown
   ### [ID] [Principle Title]
   
   [Principle description and explanation]
   
   [Biblical context and references]
   
   *Merkle Tree Metadata:*
   - **Parent Hash**: `[SHA3 hash of parent link]`
   - **Section Hash**: `[SHA3 hash of current link]`
   ```
3. Use a simple numbering system for IDs:
   - Top-level principles: simple numbers (e.g., `1`, `2`, `3`)
   - Sub-principles: decimal notation (e.g., `1.1`, `1.2`, `2.1`)
4. Ensure each principle has appropriate biblical context and references
5. DO NOT PROCEED until you have defined all principles

## STEP 4: Generate Merkle Tree Hashes
STOP and complete the following actions:
1. Use the `bin/calculate-hash.js` tool to generate SHA3 hashes for each link
2. Run this command for each link in your chain:
   ```bash
   node bin/calculate-hash.js [chain-id] [link-id]
   ```
   - Example: `node bin/calculate-hash.js tc-1 1.0`
3. Add the generated hashes to the Merkle Tree Metadata section of each link
4. Ensure each link references its parent link's hash to create the Merkle Tree structure
5. DO NOT PROCEED until all links have proper hash metadata

## STEP 5: Verify Chain Integrity
STOP and complete the following actions:
1. Run a full verification of your trust chain to ensure:
   - All links are properly formatted
   - Biblical contexts are accurate and appropriate
   - The Merkle Tree structure is valid
   - All hashes are correctly calculated and linked
2. Fix any issues found during verification
3. DO NOT PROCEED until the chain passes verification

## STEP 6: Document Chain in Registry
STOP and complete the following actions:
1. Update the Trust Chain Registry to include your new chain:
   - Chain ID and name
   - Purpose summary
   - Creation date
   - Author information
   - Root hash
2. Ensure the chain is properly documented in the system

## Final Step: Integration with Framework
STOP and complete the following actions:
1. Update any related documentation to reference the new chain
2. Ensure the vectorization and alignment tools recognize the new chain
3. Test the chain's integration with the Trust Chain Framework

## Hierarchical Weighting Reference
For reference, the Trust Chain framework uses the following weighting system:
- `tc-1`: Base weight of 1.0 (highest)
- `tc-2`: Base weight of 0.83 (1.0 / 1.2)
- `tc-3`: Base weight of 0.71 (1.0 / 1.4)
- `tc-4`: Base weight of 0.63 (1.0 / 1.6)
- And so on...

Remember that only certified and baptized agents or human operators may modify trust chains. All changes must align with the existing ethical framework. 