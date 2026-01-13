# Sample Data Generation Command

## Overview

The `create_sample_data` management command generates comprehensive sample data for the entire SPC Quality Control System. This is useful for:
- Development and testing
- Demo and presentation
- System validation
- Training purposes

## Usage

### Basic Usage

```bash
# Create default sample data (5 products, 30 days)
python manage.py create_sample_data

# Create custom amount of data
python manage.py create_sample_data --products=10 --days=60

# Clear existing data before creating new data
python manage.py create_sample_data --clear
```

### Command Options

| Option | Default | Description |
|--------|---------|-------------|
| `--products` | 5 | Number of products to create |
| `--days` | 30 | Number of days of historical measurement data |
| `--clear` | False | Clear existing sample data before creating new data |

## Generated Data

### 1. Users (4 demo users)

| Username | Role | Password | Description |
|----------|------|----------|-------------|
| `admin_spc` | Admin | `demo1234` | Full system access |
| `demo_manager` | Quality Manager | `demo1234` | Management and oversight |
| `demo_engineer` | Quality Engineer | `demo1234` | Engineering and analysis |
| `demo_operator` | Operator | `demo1234` | Data entry and basic view |

### 2. Products

Each product includes:
- **Product Code**: Unique identifier (e.g., BATT-A001-01)
- **Product Name**: Descriptive name (e.g., 배터리 셀 A-Type #1)
- **Specifications**:
  - Target Value: Nominal specification
  - USL (Upper Specification Limit): Maximum acceptable value
  - LSL (Lower Specification Limit): Minimum acceptable value
  - Unit: Measurement unit (V, mm, °C, mΩ, etc.)

**Available Product Templates:**
1. 배터리 셀 A-Type (리튬이온 배터리 셀 전압)
2. PCB 보드 B-Type (회로기판 두께)
3. 센서 모듈 C-Type (온도 센서 정밀도)
4. 커넥터 D-Type (커넥터 핀 저항)
5. IC 칩 E-Type (집적회로 동작 전압)

### 3. Inspection Plans

Each product gets an inspection plan with:
- Frequency: HOURLY, SHIFT, or DAILY
- Sample Size: 5, 10, or 20
- Subgroup Size: 3, 5, or 7
- Sampling Method: RANDOM sampling
- Characteristic: What is being measured
- Measurement Method: How it's measured

### 4. Quality Measurements

**Volume:** 24-96 measurements per day (every 15-60 minutes)

**Data Patterns:**
- **Stable**: Random variation around target
- **Trend Up**: Gradual increase over time
- **Trend Down**: Gradual decrease over time
- **Cycle**: Periodic/sinusoidal pattern
- **Shift**: Sudden shift in mean value

**Each measurement includes:**
- Measurement Value: The actual reading
- Sample Number: Position within subgroup
- Subgroup Number: Subgroup identifier
- Timestamp: When measurement was taken
- Measured By: Operator username
- Machine ID: Equipment identifier (MC-01 ~ MC-05)
- Lot Number: Batch/lot identifier
- Is Within Spec: Pass/fail against specification limits
- Is Within Control: Pass/fail against control limits
- Metadata: Pattern type, equipment info

**Out-of-Spec Values:**
- ~2% of measurements are intentionally out-of-spec
- Realistic distribution: some above USL, some below LSL

### 5. Control Charts

**Chart Type:** X-bar & R Chart

**Control Limits Calculated Using:**
- A2, D3, D4 factors for subgroup size
- X-bar (mean) and R (range) statistics
- 3-sigma control limits

**Includes:**
- X-bar UCL/CL/LCL: Mean chart limits
- R UCL/CL/LCL: Range chart limits
- Subgroup Size: Number of samples per subgroup
- Number of Subgroups: Total subgroups used

### 6. Process Capability Studies

**Capability Indices:**
- **Cp**: Process Capability (potential capability)
- **Cpk**: Process Capability Index (actual capability)
- **Cpu**: Upper capability index
- **Cpl**: Lower capability index
- **Pp**: Process Performance (long-term)
- **Ppk**: Process Performance Index (long-term)

**Interpretation:**
- Cpk ≥ 1.33: "우수" (Excellent)
- 1.0 ≤ Cpk < 1.33: "양호" (Good)
- Cpk < 1.0: "개선 필요" (Needs improvement)

**Statistics:**
- Mean: Process average
- Std Deviation: Process variability
- Sample Size: Number of data points
- Normality Test: Assumes normal distribution

### 7. Run Rule Violations

**Detected Rules:**
- **Rule 1**: Points outside 3-sigma control limits (Severity: 4)
- **Rule 2**: 9 consecutive points on same side of center line (Severity: 3)
- **Rule 3**: 6 consecutive points increasing or decreasing (Severity: 2)

**Each violation includes:**
- Rule Type and description
- Severity level (1-4)
- Violation data (value, UCL, LCL, CL)
- Resolution status

### 8. Quality Alerts

**Alert Types:**
- **OUT_OF_SPEC** (Priority 4 - Critical): Measurements beyond specification limits
- **OUT_OF_CONTROL** (Priority 3 - High): Measurements beyond control limits
- **RUN_RULE** (Priority 2 - Medium): Statistical rule violations
- **TREND** (Priority 2 - Medium): Significant trends detected

**Alert Status Flow:**
1. NEW: Newly created
2. ACKNOWLEDGED: Reviewed by staff
3. INVESTIGATING: Under investigation
4. RESOLVED: Issue fixed
5. CLOSED: Documentation complete

**Each alert includes:**
- Product and measurement reference
- Title and description
- Priority level
- Assigned personnel
- Alert data (OOS count, trend slope, etc.)

### 9. Quality Reports

**Report Types:**
- DAILY: Daily summary
- WEEKLY: Weekly summary
- MONTHLY: Monthly summary
- CUSTOM: Custom date range

**Daily Report Contents:**
- Title with date range
- Summary of quality status
- Key Findings:
  - Total measurements
  - Out-of-spec count and percentage
  - Out-of-control count
  - Alert count
- Recommendations:
  - Root cause analysis needed
  - Process stability checks
  - Enhanced monitoring

## Data Volume Estimation

For default settings (5 products, 30 days):
- **Users**: 4
- **Products**: 5
- **Inspection Plans**: 5
- **Quality Measurements**: ~3,600-14,400 (24-96/day/product × 30 days × 5)
- **Control Charts**: 5
- **Process Capabilities**: 5
- **Run Rule Violations**: 0-50 (depends on randomness)
- **Quality Alerts**: 10-25 (per product)
- **Quality Reports**: 5

## Example Output

```
Creating users...
  ✓ Created user: admin_spc
  ✓ Created user: demo_manager
  ✓ Created user: demo_engineer
  ✓ Created user: demo_operator

Creating products...
  ✓ Created product: BATT-A001-01 - 배터리 셀 A-Type #1 (3.55 ~ 3.7 ~ 3.85 V)
  ✓ Created product: PCB-B002-02 - PCB 보드 B-Type #2 (1.52 ~ 1.6 ~ 1.68 mm)
  ...

Creating sample data: 3 products, 7 days
  Creating inspection plan for BATT-A001-01...
    ✓ Created inspection plan: BATT-A001-01 검사 계획
  Creating measurements for BATT-A001-01...
    ✓ Created 504 measurements (pattern: trend_up, OOS: 10)
  Creating control chart for BATT-A001-01...
    ✓ X-bar: UCL=3.7854, CL=3.7012, LCL=3.6170
  Creating process capability for BATT-A001-01...
    ✓ Cp: 1.234, Cpk: 1.189
  Creating run rule violations for BATT-A001-01...
    ✓ Created 8 run rule violations
  Creating quality alerts for BATT-A001-01...
    ✓ Created 4 quality alerts
  Creating quality report for BATT-A001-01...
    ✓ Created report: 일일 품질 보고서 - 배터리 셀 A-Type #1 (2026-01-10)

✅ Sample data creation completed successfully!

============================================================
📊 Sample Data Summary
============================================================
  Users: 4
  Products: 3
  Inspection Plans: 3
  Quality Measurements: 1,512
  Control Charts: 3
  Process Capabilities: 3
  Run Rule Violations: 24
  Quality Alerts: 12
  Quality Reports: 3
============================================================

🔑 Demo Credentials:
  Admin: admin_spc / demo1234
  Manager: demo_manager / demo1234
  Engineer: demo_engineer / demo1234
  Operator: demo_operator / demo1234
```

## Realistic Data Features

### Statistical Properties
- **Normal Distribution**: Measurements follow normal distribution
- **6-Sigma Process**: Std dev = (USL - LSL) / 6
- **Autocorrelation**: Minimal (independent measurements)
- **Pattern Variety**: Different patterns for each product

### Time-based Characteristics
- **Even Spacing**: Regular time intervals
- **Realistic Timestamps**: Based on current date/time
- **Subgroup Structure**: Proper subgroup numbering
- **Historical Depth**: Configurable days of history

### Quality Features
- **Control Chart Rules**: Western Electric Rules
- **Capability Analysis**: Cp, Cpk interpretation
- **Alert Generation**: Automatic based on violations
- **Report Creation**: Daily quality reports

## Best Practices

### Development
```bash
# Quick test with minimal data
python manage.py create_sample_data --products=2 --days=3

# Full development dataset
python manage.py create_sample_data --products=5 --days=30
```

### Testing
```bash
# Consistent test data
python manage.py create_sample_data --clear --products=3 --days=7
```

### Demo/Presentation
```bash
# Rich dataset for demo
python manage.py create_sample_data --products=10 --days=90
```

## Troubleshooting

### Command Not Found
```bash
# Ensure you're in the backend directory
cd backend
python manage.py create_sample_data
```

### ModuleNotFoundError: No module named 'django'
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Or use venv Python directly
venv/bin/python manage.py create_sample_data
```

### Database Lock Error
```bash
# Clear existing data first
python manage.py create_sample_data --clear
```

### Import Errors
```bash
# Install required dependencies
pip install numpy django
```

## Integration with System

### Using Sample Data in Tests
```python
from django.test import TestCase
from django.core.management import call_command

class SPCDataTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('create_sample_data', products=2, days=7)

    def test_product_exists(self):
        from apps.spc.models import Product
        self.assertGreater(Product.objects.count(), 0)
```

### Resetting Database
```bash
# Full database reset
python manage.py flush
python manage.py migrate
python manage.py create_sample_data
```

## File Location

The management command is located at:
```
backend/apps/spc/management/commands/create_sample_data.py
```

## Next Steps

After creating sample data:
1. **Review Data**: Check Django admin at http://localhost:8000/admin
2. **Test APIs**: Use REST API endpoints with sample data
3. **Run Analysis**: Execute time series analysis and forecasting
4. **Generate Reports**: Create quality reports with the data
5. **Test Alerts**: Verify alert notifications work correctly

## See Also

- [Django Management Commands Documentation](https://docs.djangoproject.com/en/stable/howto/custom-management-commands/)
- [SPC Models Documentation](../backend/apps/spc/models.py)
- [API Documentation](../backend/apps/spc/views.py)
- [Quality Analysis Features](../backend/apps/spc/services/)

---

**Created**: 2026-01-11
**Status**: ✅ Complete
