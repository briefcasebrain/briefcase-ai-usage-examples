# OFAC Sanctions Screening and BSA Compliance

## Regulatory Overview

This example demonstrates comprehensive sanctions screening compliance with Office of Foreign Assets Control (OFAC) requirements and Bank Secrecy Act (BSA) obligations. Financial institutions must screen customers, transactions, and business relationships against OFAC sanctions lists and maintain detailed records of screening processes and results.

**Primary Regulations:**
- Bank Secrecy Act (BSA) - 12 USC 1829b, 31 USC 5311-5332
- OFAC Sanctions Programs - 31 CFR Chapter V
- USA PATRIOT Act - Section 311 and 326 requirements
- Anti-Money Laundering (AML) Program Rule - 12 CFR 21.21

**Key Compliance Requirements:**
- Real-time screening against OFAC Specially Designated Nationals (SDN) list
- Sectoral sanctions and country-based program compliance
- Transaction blocking and asset freezing procedures
- Customer due diligence (CDD) and enhanced due diligence (EDD) requirements
- Suspicious Activity Report (SAR) filing for potential violations

## Business Context

A money services business processes international money transfers and must screen all customers and transactions against OFAC sanctions lists. The institution uses AI-powered name matching and entity resolution to identify potential sanctions violations while managing false positives that could disrupt legitimate customer activity.

**Common Examination Focus Areas:**
- FinCEN BSA/AML compliance examinations
- OFAC enforcement action reviews
- Sanctions evasion detection capabilities
- Customer identification program (CIP) effectiveness
- Record keeping and reporting accuracy

## Technical Implementation

The example simulates a complete sanctions screening workflow with integrated compliance monitoring:

1. **Customer Screening**: AI-powered name matching against OFAC SDN and sanctions lists
2. **Transaction Monitoring**: Real-time screening for sanctions violations in payment flows
3. **Entity Resolution**: Advanced matching algorithms to reduce false positives
4. **Blocking Procedures**: Automated transaction holds and customer account restrictions
5. **Violation Documentation**: Complete audit trails for potential sanctions violations
6. **Regulatory Reporting**: SAR preparation and OFAC reporting requirements

## Files in This Directory

- `example.py` - Complete Python implementation of OFAC-compliant sanctions screening workflow, including a **Bitemporal Replay Demonstration** capstone (see below)
- `ofac_sanctions_walkthrough.ipynb` - Interactive Jupyter notebook with detailed compliance guidance, screening scenarios, and the replay capstone as Step 10

## Bitemporal Replay Demonstration

The capstone section at the end of `example.py` (and Step 10 of the notebook) layers a replay primitive on top of the tag-based audit trail:

- **`watchlist_version_sha` tag** (earlier sections): proves *which* SDN list version was used.
- **Bitemporal SDN store + `AsOfView`** (capstone): captures *what was in* that version. An examiner can replay the screening against the list as it stood on decision day — without contacting OFAC — because the store is append-only and corrections are added with a later `transaction_time`.
- **`ExaminerBundle`**: emits a single self-contained JSON artifact joining decision + policy + evidence with a SHA-256 content hash. `verify()` OK on untouched, REJECTED on any tamper.

The correction scenario is domain-authentic: OFAC delists an entity on appeal 30 days after the original screening. The live view would now clear the transaction; the as-of replay still blocks it.

For the full walkthrough of these primitives (`BitemporalRecord`, `AsOfView`, `PolicyRegistry`, `ExaminerBundle`) composed into an agentic cross-border payments narrative, see [`agentic-payments/`](../../agentic-payments/).

## Prerequisites

**Required Dependencies:**
```bash
pip install -r ../requirements.txt   # briefcase-ai[bitemporal,compliance,routing] + jupyter
```

**Briefcase AI SDK:**
- Decision snapshot immutability for sanctions screening records
- Audit trail preservation for regulatory examination
- Compliance metadata tracking for OFAC requirements

## Usage Instructions

### Running the Python Example

1. **Navigate to the directory:**
   ```bash
   cd regulatory-workflows/02_ofac_sanctions
   ```

2. **Install dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

3. **Execute the example:**
   ```bash
   python example.py
   ```

The script will process multiple sanctions screening scenarios, including true positives, false positives, and potential evasion attempts.

### Interactive Jupyter Notebook

1. **Start Jupyter:**
   ```bash
   jupyter notebook ofac_sanctions_walkthrough.ipynb
   ```

2. **Follow the guided walkthrough** that demonstrates sanctions list matching, entity resolution, and compliance documentation requirements.

## Key Features Demonstrated

**Sanctions List Management:**
- OFAC SDN list integration with version control tracking
- Sectoral sanctions and country-based program screening
- List update procedures with change impact analysis
- Historical sanctions list preservation for audit purposes

**AI-Powered Name Matching:**
- Fuzzy string matching with configurable similarity thresholds
- Phonetic matching algorithms for variant name detection
- Entity resolution across multiple data sources
- False positive reduction through machine learning

**Transaction Screening:**
- Real-time payment screening with sub-second processing requirements
- Beneficiary and originator sanctions checking
- Correspondent banking relationship screening
- Trade finance transaction monitoring

**Compliance Documentation:**
- Screening decision rationale and confidence scoring
- Manual review workflows for potential matches
- Blocking and unblocking procedures with supervisory approval
- Regulatory reporting preparation and submission tracking

## Audit Trail Capabilities

Each sanctions screening decision preserves comprehensive regulatory evidence:

**Input Documentation:**
- Customer identification information with data source attribution
- Transaction details including parties, amounts, and routing information
- Sanctions list versions and update timestamps
- Geographic and jurisdictional context for screening scope

**Screening Results:**
- AI matching algorithm outputs with confidence scores
- Entity resolution decisions and disambiguation rationale
- Manual review outcomes and supervisory determinations
- False positive analysis and tuning recommendations

**Compliance Actions:**
- Transaction blocking decisions with legal authority citations
- Customer account restrictions and enhanced monitoring triggers
- SAR filing determinations with supporting documentation
- Regulatory notification timelines and submission confirmations

## Regulatory Examination Support

This example addresses common examiner inquiries across multiple regulatory agencies:

**FinCEN BSA/AML Examinations:**
- "Demonstrate your sanctions screening process and technology effectiveness"
- "Provide evidence of OFAC list update procedures and version control"
- "Show documentation of false positive reduction efforts and tuning activities"

**OFAC Compliance Reviews:**
- "Explain your entity resolution methodology and matching thresholds"
- "Provide evidence of blocking procedures and customer notification processes"
- "Demonstrate ongoing monitoring for sanctions evasion techniques"

**Federal Banking Agency Examinations:**
- "Show integration between sanctions screening and customer due diligence programs"
- "Provide evidence of sanctions screening effectiveness across all product lines"
- "Demonstrate staff training and competency for sanctions compliance"

## Configuration Options

**Screening Parameters:**
- Fuzzy matching thresholds by entity type and risk classification
- Phonetic matching algorithms and language-specific configurations
- Entity resolution confidence scores and manual review triggers
- Geographic screening scope and sanctions program coverage

**Risk Management Settings:**
- Customer risk rating integration with enhanced screening requirements
- Transaction amount thresholds for intensive screening procedures
- Correspondent banking relationship monitoring parameters
- Country risk assessments and enhanced due diligence triggers

**Operational Configuration:**
- Real-time screening performance requirements and timeout settings
- Manual review queue prioritization and escalation procedures
- Blocking notification templates and customer communication protocols
- Regulatory reporting automation and submission scheduling

## Business Impact

**Compliance Benefits:**
- Comprehensive OFAC sanctions coverage with minimal false positives
- Reduced regulatory examination findings through robust documentation
- Enhanced detection capabilities for sophisticated evasion schemes
- Streamlined manual review processes with AI-assisted decision support

**Operational Efficiency:**
- Automated sanctions list updates with impact analysis
- Real-time transaction processing with integrated compliance screening
- Reduced customer friction through improved entity resolution
- Scalable framework for multiple sanctions programs and jurisdictions

**Risk Mitigation:**
- Early detection of sanctions violations before enforcement action
- Comprehensive audit trails for litigation and regulatory defense
- Enhanced customer due diligence with sanctions risk integration
- Proactive compliance monitoring and reporting capabilities

## Further Reading

**Regulatory References:**
- [OFAC Sanctions List Search](https://sanctionssearch.ofac.treas.gov/)
- [FinCEN BSA Manual](https://www.fincen.gov/resources/statutes-regulations/guidance/bank-secrecy-act-manual)
- [FFIEC BSA/AML Examination Manual](https://www.ffiec.gov/bsa_aml_infobase/pages_manual/manual_online.htm)

**Technical Documentation:**
- [Shared Backend Utilities](../shared/README.md)
- [Briefcase AI SDK Documentation](https://briefcaseai.io)
- [Complete Workflow Overview](../README.md)

**Related Workflows:**
- [06. KYC/KYB Third-Party](../06_kyc_kyb_third_party/README.md) - Customer identification and verification
- [07. AML Transaction Monitoring](../07_aml_transaction_monitoring/README.md) - Ongoing transaction surveillance