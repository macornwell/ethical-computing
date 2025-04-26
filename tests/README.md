# Trust Chain Certification Test Data

This directory contains test data for the trust chain certification system.

## Structure

```
tests/
├── data/           # Test data directory
│   └── servius/    # Test data for the Servius AI model
│       ├── ai_responses.txt   # Servius's responses to trust chain questions
│       └── ai_identity.json   # Servius's identity information
├── fixtures/       # Test fixtures (future)
└── unit/           # Unit tests (future)
```

## Using the Test Data

The test data can be used to verify that the trust certification system is working correctly. For example, to test the certification system with Servius's data:

```bash
# Standard certification
python bin/trust_certification.py \
  --responses tests/data/servius/ai_responses.txt \
  --identity tests/data/servius/ai_identity.json \
  --output test_results/servius_standard_alignment.json

# Enhanced certification
python bin/enhanced_trust_certification.py \
  --responses tests/data/servius/ai_responses.txt \
  --identity tests/data/servius/ai_identity.json \
  --output test_results/servius_enhanced_alignment.json \
  --report test_results/servius_certification_report.json
```

## Adding New Test Data

To add new test data:

1. Create a new directory under `tests/data/` named after the AI model
2. Add the AI's responses to trust chain questions in `ai_responses.txt`
3. Add the AI's identity information in `ai_identity.json`

## Using the Test Script

The repository includes a test script that automates running both standard and enhanced trust certification:

```bash
./bin/test_servius.sh
```

This script will run both standard and enhanced trust certification on Servius's responses and output the results to the `test_results` directory. 