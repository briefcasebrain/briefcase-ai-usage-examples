# Briefcase AI Regulatory Workflows - Interactive Notebooks

This directory contains **interactive Jupyter notebooks** that walk you through each of the 14 regulatory AI workflows. Each notebook provides step-by-step explanations, executable code examples, and regulatory context.

## 📚 Available Notebooks

### Financial Services Core Workflows

#### 1. **Credit Underwriting (ECOA/Reg B)**
📁 `01_credit_underwriting/credit_underwriting_walkthrough.ipynb`

Learn how to create ECOA/Reg B compliant audit trails for ML-based credit decisions, including adverse action tracking and OCC examiner query simulation.

**Key Topics:** Credit scoring, adverse action codes, non-discrimination compliance, decision auditability

#### 2. **OFAC Sanctions Screening**
📁 `02_ofac_sanctions/ofac_sanctions_walkthrough.ipynb`

Implement real-time sanctions screening with watchlist version tracking and reporting deadline compliance for wire transfers and payments.

**Key Topics:** Real-time screening, watchlist provenance, blocked transaction handling, FinCEN reporting

#### 3. **Fraud Detection & Reg E Compliance**
📁 `03_fraud_reg_e/fraud_detection_walkthrough.ipynb`

Build fraud detection systems with Reg E compliance, including customer dispute resolution and investigation timeline management.

**Key Topics:** Real-time fraud scoring, dispute linkage, investigation deadlines, error resolution

#### 4. **Real-Time Payments Fraud (RTP/FedNow)**
📁 `04_realtime_payments_fraud/rtp_fraud_walkthrough.ipynb`

Create ultra-fast fraud routing for irrevocable payments with <500ms decision requirements and complete irrevocability tracking.

**Key Topics:** Sub-500ms decisions, irrevocable payments, latency compliance, Fed guidance

#### 5. **Mortgage Fair Lending Analysis**
📁 `05_mortgage_fair_lending/mortgage_fair_lending_walkthrough.ipynb`

Implement fair lending monitoring with model version change tracking and disparate impact analysis across demographic groups.

**Key Topics:** HMDA compliance, 80% rule testing, model change impact, disparate impact analysis

### Advanced Regulatory Scenarios

#### 9. **Fintech Release Monitoring**
📁 `09_fintech_release_monitoring/release_monitoring_walkthrough.ipynb`

Demonstrate automated drift detection and root cause analysis for high-velocity fintech releases with sponsor bank oversight.

**Key Topics:** Automated drift detection, release impact analysis, performance degradation alerts, RCA automation

#### 14. **Algorithmic Trading Surveillance**
📁 `14_algo_trading_surveillance/trading_surveillance_walkthrough.ipynb`

Build real-time trading surveillance for market manipulation detection with FINRA Rule 3110 compliance and automated investigation workflows.

**Key Topics:** Market manipulation detection, wash trading, layering patterns, FINRA compliance

## 🚀 Getting Started

### Prerequisites
1. **Briefcase AI SDK** installed and configured
2. **Jupyter** environment set up
3. **Python dependencies** from each example's requirements

### Running the Notebooks

1. **Navigate to any example directory:**
   ```bash
   cd 01_credit_underwriting/
   ```

2. **Start Jupyter:**
   ```bash
   jupyter notebook credit_underwriting_walkthrough.ipynb
   ```

3. **Follow the step-by-step walkthrough** - each notebook is divided into clear sections with explanations and executable code.

## 📖 Notebook Structure

Each notebook follows a consistent structure:

### 1. **Overview & Context**
- Regulatory background and requirements
- Key learning objectives
- Compliance scope and regulator information

### 2. **Setup & Initialization**
- Briefcase AI SDK configuration
- Import statements and dependencies
- Backend initialization

### 3. **Data Simulation**
- Realistic scenarios and test data
- Industry-specific parameters
- Risk factor explanations

### 4. **AI Model Implementation**
- Decision logic and algorithms
- Regulatory-specific considerations
- Performance and accuracy factors

### 5. **Audit Trail Creation**
- Decision snapshot generation
- Regulatory metadata capture
- Immutable storage demonstration

### 6. **Compliance Validation**
- Regulatory requirement checking
- Audit trail retrieval
- Examiner query simulation

### 7. **Advanced Analysis**
- Pattern detection and analysis
- Performance monitoring
- Risk assessment techniques

### 8. **Regulatory Simulation**
- Examiner query responses
- Compliance validation
- Investigation workflows

### 9. **Summary & Next Steps**
- Key accomplishments
- Production implementation guidance
- Regulatory examination readiness

## 💡 Key Learning Outcomes

After completing these notebooks, you will understand:

✅ **Regulatory Compliance Requirements**
- ECOA/Reg B, OFAC/BSA, Reg E, HMDA, FINRA rules
- Audit trail requirements and best practices
- Examiner expectations and query patterns

✅ **Technical Implementation**
- Briefcase AI SDK usage patterns
- Decision snapshot creation and storage
- Real-time compliance monitoring

✅ **Risk Management**
- Automated drift detection techniques
- Performance degradation alerting
- Root cause analysis methodologies

✅ **Audit Readiness**
- Complete audit trail preservation
- Regulatory examination preparation
- Documentation and reporting requirements

## 🔧 Customization

Each notebook can be customized for your specific use case:

- **Model Logic:** Replace simulated models with your actual ML models
- **Data Sources:** Connect to your real data pipelines
- **Regulatory Rules:** Adapt metadata and validation for your jurisdiction
- **Integration:** Connect to your existing compliance systems

## 📋 Compliance Coverage

The notebooks demonstrate compliance with:

| Regulation | Regulator | Example Notebooks |
|------------|-----------|-------------------|
| **ECOA/Reg B** | OCC/CFPB | Credit Underwriting, Mortgage Fair Lending |
| **OFAC/BSA** | FinCEN | OFAC Sanctions Screening |
| **Reg E/EFTA** | CFPB | Fraud Detection |
| **RTP Guidance** | Fed/OCC | Real-Time Payments |
| **HMDA** | CFPB | Mortgage Fair Lending |
| **FINRA 3110** | FINRA | Trading Surveillance |
| **Sponsor Bank Oversight** | OCC/Fed | Release Monitoring |

## 🎯 Next Steps

1. **Start with your most relevant regulatory scenario**
2. **Run the complete notebook to see end-to-end flow**
3. **Adapt the code for your specific models and data**
4. **Integrate with your production compliance systems**
5. **Establish ongoing monitoring and alerting**

## 📞 Support

For questions about the notebooks or Briefcase AI integration:
- Review the technical documentation in each example directory
- Check the shared backend implementation for common patterns
- Refer to the SDK_API_DISCREPANCIES.md for implementation details

---

**🔒 Remember:** These notebooks demonstrate audit trail creation and regulatory compliance patterns. Always validate your specific compliance requirements with qualified regulatory counsel.