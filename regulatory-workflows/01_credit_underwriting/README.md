# Credit Underwriting with ECOA/Reg B Compliance

## Regulatory Overview

This example demonstrates AI-powered credit underwriting compliance with the Equal Credit Opportunity Act (ECOA) and Federal Reserve Regulation B. These regulations prohibit creditors from discriminating against credit applicants on the basis of race, color, religion, national origin, sex, marital status, age, or because an applicant receives income from a public assistance program.

**Primary Regulations:**
- Equal Credit Opportunity Act (ECOA) - 15 USC 1691
- Federal Reserve Regulation B - 12 CFR Part 1002
- Consumer Financial Protection Bureau (CFPB) supervision requirements

**Key Compliance Requirements:**
- Adverse action notice requirements for declined or unfavorable credit decisions
- Prohibited basis tracking and monitoring for fair lending analysis
- Reason code documentation for all credit decisions
- Record retention requirements (25 months for consumer credit, 12 months for business credit)

## Business Context

A federally regulated bank uses machine learning models to evaluate consumer credit applications. The bank must ensure that credit decisions comply with fair lending requirements while maintaining comprehensive audit trails for regulatory examination. When applicants are denied credit or offered less favorable terms, the bank must provide specific adverse action notices with reason codes explaining the decision.

**Common Examination Focus Areas:**
- OCC safety and soundness examinations
- CFPB consumer compliance reviews
- Fair lending statistical analysis and testing
- Adverse action notice adequacy and timing

## Technical Implementation

The example simulates a complete credit underwriting workflow with integrated compliance controls:

1. **Application Processing**: Captures complete applicant information with appropriate data categorization
2. **AI Model Decision**: Simulates machine learning credit scoring with explainable outputs
3. **Adverse Action Analysis**: Automatically generates compliant reason codes for declined applications
4. **Audit Trail Creation**: Stores immutable decision records with full regulatory context
5. **Examiner Query Simulation**: Demonstrates response capabilities for regulatory examination requests

## Files in This Directory

- `example.py` - Complete Python implementation of ECOA-compliant credit underwriting workflow
- `credit_underwriting_walkthrough.ipynb` - Interactive Jupyter notebook with step-by-step explanation and educational content

## Prerequisites

**Required Dependencies:**
```bash
pip install briefcase-ai
pip install jupyter  # For notebook usage
```

**Briefcase AI SDK:**
- Regulatory-grade audit trail capabilities
- Decision snapshot immutability
- Compliance metadata tracking

## Usage Instructions

### Running the Python Example

1. **Navigate to the directory:**
   ```bash
   cd regulatory-workflows/01_credit_underwriting
   ```

2. **Install dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

3. **Execute the example:**
   ```bash
   python example.py
   ```

The script will process multiple credit applications across different scenarios, demonstrating both approved and declined cases with proper adverse action handling.

### Interactive Jupyter Notebook

1. **Start Jupyter:**
   ```bash
   jupyter notebook credit_underwriting_walkthrough.ipynb
   ```

2. **Follow the guided walkthrough** that explains each step of the compliance workflow with detailed regulatory context.

## Key Features Demonstrated

**Credit Decision Processing:**
- Multi-factor credit scoring with income, employment, and credit history analysis
- Debt-to-income ratio calculations with regulatory thresholds
- Credit utilization analysis with risk-based pricing
- Employment verification and income stability assessment

**ECOA/Reg B Compliance:**
- Prohibited basis monitoring (race, gender, age, etc.) without discriminatory usage
- Fair lending statistical tracking across demographic groups
- Adverse action reason code generation (income insufficient, credit history, DTI ratio)
- Timing requirements for adverse action notices

**Audit Trail Capabilities:**
- Complete decision input preservation with sensitive data handling
- Model version and configuration tracking for reproducibility
- Reason code justification and regulatory citation linkage
- Examiner query response preparation

## Audit Trail Capabilities

Each credit decision captures comprehensive regulatory context:

**Input Preservation:**
- Applicant financial information with appropriate privacy protections
- Credit report data and scoring factors
- Income verification documentation references
- Collateral information and property valuations

**Decision Documentation:**
- AI model outputs and confidence scores
- Business rule applications and override justifications
- Risk-based pricing determinations
- Adverse action trigger analysis

**Compliance Metadata:**
- ECOA prohibited basis monitoring tags
- Fair lending statistical classification
- Adverse action requirement flags
- Record retention schedule adherence

## Regulatory Examination Support

This example prepares responses for common examiner inquiries:

**OCC Safety and Soundness:**
- "Demonstrate your credit risk management process and AI model governance"
- "Provide evidence of model validation and performance monitoring"
- "Show documentation of credit policy adherence and exception tracking"

**CFPB Consumer Compliance:**
- "Explain your adverse action notice process and reason code accuracy"
- "Provide fair lending analysis across prohibited basis categories"
- "Demonstrate ECOA compliance in automated underwriting decisions"

**Fair Lending Analysis:**
- "Show statistical analysis of approval rates across demographic groups"
- "Provide evidence of disparate impact testing and remediation"
- "Demonstrate ongoing monitoring for fair lending compliance"

## Configuration Options

**Credit Policy Parameters:**
- Maximum debt-to-income ratios by product type
- Minimum credit score thresholds with override criteria
- Income verification requirements and employment history minimums
- Collateral valuation and loan-to-value ratio limits

**Compliance Settings:**
- Adverse action reason code mappings and priority ordering
- Fair lending monitoring categories and statistical thresholds
- Record retention schedules and audit trail preservation periods
- Examiner query response templates and formatting

**AI Model Configuration:**
- Credit scoring model version and feature selection
- Explainability requirements and reason code generation
- Performance monitoring thresholds and drift detection
- Bias testing parameters and fairness constraint implementation

## Business Impact

**Risk Management Benefits:**
- Consistent credit risk assessment with quantifiable decision criteria
- Reduced regulatory examination findings through comprehensive documentation
- Improved fair lending compliance with automated monitoring
- Enhanced audit trail capabilities for litigation defense

**Operational Efficiency:**
- Automated adverse action notice generation with accurate reason codes
- Streamlined examiner query response with pre-formatted documentation
- Reduced manual compliance review through built-in regulatory checks
- Scalable framework for multiple credit product lines

## Further Reading

**Regulatory References:**
- [CFPB ECOA Examination Procedures](https://www.consumerfinance.gov/compliance/supervision-examination-manuals/)
- [Federal Reserve Regulation B Commentary](https://www.federalreserve.gov/boarddocs/supmanual/cch/fair_lend_reg_b.pdf)
- [OCC Interagency Fair Lending Examination Procedures](https://www.occ.gov/publications-and-resources/publications/comptrollers-handbook/files/fair-lending/index-fair-lending.html)

**Technical Documentation:**
- [Shared Backend Utilities](../shared/README.md)
- [Briefcase AI SDK Documentation](https://docs.briefcasebrain.com)
- [Complete Workflow Overview](../README.md)

**Related Workflows:**
- [05. Mortgage Fair Lending](../05_mortgage_fair_lending/README.md) - HMDA-specific fair lending analysis
- [10. Collections & Debt Management](../10_collections_debt/README.md) - Post-origination compliance