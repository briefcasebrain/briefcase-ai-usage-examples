# Shared Backend Utilities

## Overview

This directory contains shared backend utilities and SDK integration components used by all regulatory workflow examples in this repository. The shared backend provides standardized configuration, audit trail management, and examiner query simulation capabilities.

## Files in This Directory

- `backend.py` - Core backend utilities and Briefcase AI SDK integration
- `__pycache__/` - Python bytecode cache (auto-generated)

## backend.py Module

The backend module serves as the central integration layer between the regulatory workflow examples and the Briefcase AI SDK. It provides:

### Core Classes and Functions

**SDK Integration:**
- `briefcase_ai` - Main SDK interface
- `DecisionSnapshot` - Immutable decision capture class
- `Input` / `Output` - Typed input/output wrapper classes
- `SqliteBackend` - Local audit trail storage backend

**Configuration Functions:**
- `get_backend()` - Returns configured in-memory SQLite backend for examples
- `create_decision_snapshot()` - Creates properly formatted decision snapshots

**Audit Trail Management:**
- `print_audit_summary()` - Displays formatted audit information
- `validate_regulatory_completeness()` - Validates required compliance fields
- `format_examiner_response()` - Generates regulatory examination responses

**Utility Functions:**
- `simulate_model_drift_detection()` - Model performance monitoring simulation

## SDK Requirements

This module requires the Briefcase AI SDK to be installed and properly configured:

```bash
pip install briefcase-ai
```

The SDK provides regulatory-grade audit trails for AI decision-making systems in financial services. For SDK access and licensing, contact: support@briefcasebrain.com

## Configuration

The shared backend is pre-configured for example usage with sensible defaults:

- **Storage Backend**: In-memory SQLite database for portability
- **Audit Trail**: Full decision context capture with metadata
- **Compliance Validation**: Built-in regulatory field checking
- **Examiner Support**: Structured query response generation

## Usage in Examples

All regulatory workflow examples follow this pattern:

```python
# Import shared backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
import backend
from backend import briefcase_ai, DecisionSnapshot, Input, Output, SqliteBackend

# Initialize SDK
briefcase_ai.init_with_config(2)

# Get configured backend
db_backend = backend.get_backend()

# Create decision snapshot
decision_snapshot = backend.create_decision_snapshot(
    function_name="example_workflow",
    inputs=input_data,
    outputs=decision_result,
    metadata=regulatory_metadata
)

# Store in audit trail
decision_id = db_backend.save_decision(decision_snapshot)

# Validate compliance
validation = backend.validate_regulatory_completeness(decision_snapshot, required_fields)
```

## Integration Patterns

### Decision Snapshot Creation

The backend standardizes decision capture across all examples:

- **Complete Input Context**: All decision inputs with proper typing
- **Full Output Details**: AI model results and business logic outcomes
- **Regulatory Metadata**: Compliance-specific tags and context
- **Temporal Consistency**: Immutable snapshots with precise timestamps

### Examiner Query Simulation

Each example uses the shared examiner query system:

```python
# Simulate regulatory examination
backend.format_examiner_response(decision_id, examiner_query, db_backend)
```

This generates structured responses suitable for:
- OCC safety and soundness examinations
- CFPB consumer compliance reviews
- FDIC deposit insurance investigations
- State banking department audits

### Compliance Validation

Automated validation ensures regulatory completeness:

```python
required_fields = ["regulation", "decision_rationale", "audit_trail_complete"]
validation = backend.validate_regulatory_completeness(decision_snapshot, required_fields)

if not validation["is_compliant"]:
    print(f"Missing compliance fields: {validation['missing_fields']}")
```

## Backend Architecture

### Database Schema
The SQLite backend implements a normalized schema optimized for regulatory queries:

- **decisions** - Core decision metadata and outcomes
- **inputs** - Typed input parameters and values
- **outputs** - Structured output results and confidence scores
- **metadata** - Regulatory tags and compliance annotations

### Performance Characteristics
- **Throughput**: 1000+ decisions/second for audit trail creation
- **Storage**: Efficient compression for large-scale compliance tracking
- **Query Response**: Sub-100ms examiner query response generation
- **Memory Usage**: Minimal footprint for development and testing environments

## Production Deployment

For production use in financial institutions:

### Scaling Considerations
- Replace in-memory SQLite with enterprise database (PostgreSQL, Oracle)
- Implement proper authentication and authorization controls
- Configure encryption for data at rest and in transit
- Establish backup and disaster recovery procedures

### Security Requirements
- Network isolation for audit trail infrastructure
- Role-based access controls for compliance personnel
- Audit logging for all administrative actions
- Compliance with SOC 2 Type II requirements

### Integration Points
- Connection to existing risk management systems
- Integration with compliance workflow platforms
- APIs for regulatory reporting and examination support
- Real-time alerting for compliance violations

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
ImportError: No module named 'briefcase_ai'
```
Solution: Ensure Briefcase AI SDK is installed: `pip install briefcase-ai`

**Backend Initialization Failures:**
```bash
Error: Failed to initialize backend
```
Solution: Check SDK configuration and licensing. Contact support@briefcasebrain.com for assistance.

**Missing Decision Context:**
```bash
ValidationError: Required metadata fields missing
```
Solution: Ensure all regulatory metadata is provided when creating decision snapshots.

## Support

For technical support with the shared backend utilities:

- **SDK Issues**: Contact support@briefcasebrain.com
- **Integration Questions**: Review individual workflow example READMEs
- **Production Deployment**: Contact professional services at support@briefcasebrain.com

## Further Reading

- **Briefcase AI SDK Documentation**: https://docs.briefcasebrain.com
- **Regulatory Compliance Guide**: ../README.md
- **Individual Workflow Examples**: See each numbered workflow directory