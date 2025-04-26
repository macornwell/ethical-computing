#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const glob = require('glob');
const { ArgumentParser } = require('argparse');

/**
 * Parse command line arguments
 */
const parseArguments = () => {
  const parser = new ArgumentParser({
    description: 'Calculate SHA3 hash for trust chain sections'
  });

  parser.add_argument('chain_id', {
    help: 'Trust chain ID (e.g., tc-1)',
    type: 'str'
  });

  parser.add_argument('node_id', {
    help: 'Link ID within the trust chain (e.g., 0.1, Purpose)',
    type: 'str'
  });

  return parser.parse_args();
};

/**
 * Find trust chain file path based on chainId
 */
const findTrustChainPath = (chainId) => {
  const trustChainDir = path.join(__dirname, '..', 'src', 'trust-chain', 'chains');
  const files = glob.sync(path.join(trustChainDir, `${chainId}*.md`));
  
  if (files.length === 0) {
    throw new Error(`No trust chain file found for chain ID "${chainId}"`);
  }
  
  return files[0];
};

/**
 * Read file content
 */
const readFileContent = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * Parse markdown content into sections based on headers
 */
const parseMarkdownSections = (content) => {
  const lines = content.split('\n');
  const sections = [];
  let currentSection = null;
  let currentTitle = null;
  let sectionContent = '';
  
  const isNumberedSectionHeader = (line) => {
    return line.startsWith('### ') && (
      line.includes(' 0.') || 
      line.includes(' 1.') || 
      line.includes(' 2.') || 
      line.includes(' 3.') || 
      line.includes(' 4.') || 
      line.includes(' 5.') || 
      line.includes(' 6.') || 
      line.includes(' 7.') || 
      line.includes(' 8.') || 
      line.includes(' 9.') || 
      line.includes(' 10.') || 
      line.includes(' 11.') || 
      line.includes(' 12.')
    );
  };
  
  const extractSectionId = (line) => {
    const match = line.match(/### (\d+(\.\d+)?)/);
    return match ? match[1] : null;
  };
  
  const extractTitle = (line) => line.substring(4).trim();
  
  const addSectionIfExists = () => {
    if (currentSection) {
      sections.push({
        id: currentSection,
        title: currentTitle,
        content: sectionContent.trim()
      });
    }
  };
  
  lines.forEach(line => {
    if (isNumberedSectionHeader(line)) {
      addSectionIfExists();
      
      currentSection = extractSectionId(line);
      currentTitle = extractTitle(line);
      sectionContent = line + '\n';
    } else if (line.startsWith('## Purpose')) {
      addSectionIfExists();
      
      currentSection = 'Purpose';
      currentTitle = 'Purpose';
      sectionContent = line + '\n';
    } else if (currentSection) {
      sectionContent += line + '\n';
    }
  });
  
  addSectionIfExists();
  
  return sections;
};

/**
 * Find a section by its ID
 */
const findSection = (sections, nodeId) => {
  const normalizedNodeId = nodeId === '0' ? '0.0' : nodeId;
  
  return sections.find(section => {
    if (section.id === normalizedNodeId) return true;
    if (normalizedNodeId.toLowerCase() === 'purpose' && section.id === 'Purpose') return true;
    return false;
  });
};

/**
 * Extract content for hashing (up to but not including the Section Hash)
 */
const extractContentForHashing = (content) => {
  const merkleMetadataStart = content.indexOf('*Merkle Tree Metadata:*');
  if (merkleMetadataStart === -1) return content;
  
  const lines = content.split('\n');
  let hashableContent = [];
  let inMetadata = false;
  let foundSectionHash = false;
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    
    if (line.includes('*Merkle Tree Metadata:*')) {
      inMetadata = true;
      hashableContent.push(line);
    } else if (inMetadata) {
      if (line.includes('**Parent Hash**:')) {
        hashableContent.push(line);
      } else if (line.includes('**Section Hash**:')) {
        // Found the section hash line - don't include it or anything after it
        foundSectionHash = true;
        break;
      } else if (line.trim() === '') {
        // Empty line after metadata
        inMetadata = false;
        hashableContent.push(line);
      } else if (!line.startsWith('-')) {
        // Not a metadata line anymore
        inMetadata = false;
        hashableContent.push(line);
      }
    } else {
      hashableContent.push(line);
    }
  }
  
  // If we never found the section hash, return everything
  if (!foundSectionHash) {
    return content;
  }
  
  return hashableContent.join('\n');
};

/**
 * Extract hash metadata from content
 */
const extractHashMetadata = (content) => {
  const lines = content.split('\n');
  let parentHash = null;
  let sectionHash = null;
  
  for (const line of lines) {
    if (line.includes('**Parent Hash**:')) {
      const match = line.match(/`([a-f0-9]+)`/);
      parentHash = match ? match[1] : null;
    } else if (line.includes('**Section Hash**:')) {
      const match = line.match(/`([a-f0-9]+)`/);
      sectionHash = match ? match[1] : null;
    }
  }
  
  return { parentHash, sectionHash };
};

/**
 * Calculate SHA3-256 hash of the content
 */
const calculateSHA3 = (content) => 
  crypto.createHash('sha3-256').update(content).digest('hex');

/**
 * Format and display the results
 */
const displayResults = (chainId, section, contentToHash, hash, parentHash, sectionHash) => {
  console.info(`\nChain: ${chainId}`);
  console.info(`Node: ${section.title} (${section.id})`);
  console.info(`\nContent for hashing (${contentToHash.length} bytes):\n${contentToHash.substring(0, 300)}${contentToHash.length > 300 ? '...' : ''}`);
  console.info(`\nParent Hash: ${parentHash || 'None'}`);
  console.info(`SHA3-256 Calculated Hash: ${hash}`);
  
  if (sectionHash) {
    console.info(`Section Hash in Metadata: ${sectionHash}`);
    console.info(`Hashes ${hash === sectionHash ? 'MATCH ✓' : 'DO NOT MATCH ✗'}`);
    
    if (hash !== sectionHash) {
      console.info(`\nTo update the section hash in the document, replace:\n${sectionHash}\nwith:\n${hash}`);
    }
  }
};

/**
 * Main function that composes all operations
 */
const main = () => {
  try {
    const args = parseArguments();
    const trustChainPath = findTrustChainPath(args.chain_id);
    const content = readFileContent(trustChainPath);
    const sections = parseMarkdownSections(content);
    const section = findSection(sections, args.node_id);
    
    if (!section) {
      throw new Error(`Link ID "${args.node_id}" not found in chain "${args.chain_id}"`);
    }
    
    // Extract hashes from metadata
    const { parentHash, sectionHash } = extractHashMetadata(section.content);
    
    // Prepare content for hashing (including all content up to but not including the Section Hash)
    const contentToHash = extractContentForHashing(section.content);
    
    // Calculate hash
    const hash = calculateSHA3(contentToHash);
    
    // Display results
    displayResults(args.chain_id, section, contentToHash, hash, parentHash, sectionHash);
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
};

// Execute the main function
main(); 