# NexAML - Anti-Money Laundering Compliance for Odoo

Comprehensive AML compliance solution for Odoo 19.0, providing customer risk assessment, sanctions screening, transaction monitoring, and regulatory reporting.

## Features

- **Customer Risk Assessment (CRA)**: Automated risk scoring based on weighted factors
- **Sanctions Screening**: Integration with OpenSanctions/Yente API for sanctions and PEP screening
- **Transaction Monitoring**: Configurable rules for detecting suspicious patterns
- **Case Management**: Full workflow for investigating and resolving AML cases
- **Alert Management**: Triage and escalation of transaction monitoring alerts
- **Regulatory Reporting**: SAR/STR reports with goAML XML export

## Installation

### Requirements

- Odoo 19.0
- Python 3.10+
- Dependencies: `requests`, `xlsxwriter` (optional, for Excel exports)

### Install Module

1. Copy the `nexaml` directory to your Odoo addons path:
   ```bash
   cp -r nexaml /path/to/odoo/addons/
   ```

2. Restart Odoo server:
   ```bash
   ./odoo-bin --addons-path=/path/to/odoo/addons
   ```

3. Update apps list in Odoo (Apps → Update Apps List)

4. Install NexAML module (Apps → Search "NexAML" → Install)

## Configuration

### Initial Setup

1. Navigate to **Settings → General Settings → NexAML** section

2. Configure **Sanctions Screening**:
   - **Yente API URL**: Default is `https://demo-yente.opensanctions.org`
   - **API Key**: Optional, leave blank for demo URL
   - **Match Threshold**: Default 70% (adjust based on your risk tolerance)
   - **Auto-Screen**: Enable to automatically screen new customers

3. Configure **Risk Assessment**:
   - **EDD Threshold**: Choose when Enhanced Due Diligence is required
   - Options: Medium Risk and Above, or High Risk Only

4. Configure **Transaction Monitoring**:
   - Enable monitoring for invoices and/or payments
   - Default transaction rules are pre-configured

### Transaction Rules

Five default rules are provided:
- **HIGH_VALUE**: Triggers for transactions > $50,000
- **VELOCITY**: Detects 10+ transactions in 1 day
- **RAPID_VELOCITY**: Detects 5+ transactions in 1 hour
- **HIGH_RISK_LARGE**: High-risk customers with large transactions
- **ROUND_AMOUNT**: Detects suspiciously round amounts

Access rules via **NexAML → Configuration → Transaction Rules**

## Usage

### Customer Risk Assessment

1. Open customer record (Contacts → Customers)
2. Navigate to **NexAML** tab
3. Set risk factors:
   - Customer Risk (1-3)
   - Geography Risk (1-3)
   - Product Risk (1-3)
   - Channel Risk (1-3)
4. Click **Assess Risk** to calculate
5. View calculated **Inherent Risk** and **Risk Level**
6. Apply **Controls** to reduce **Residual Risk**

Risk Formula: `(Customer × 0.30) + (Geography × 0.20) + (Product × 0.30) + (Channel × 0.20)`

### Sanctions Screening

**Manual Screening:**
1. Open customer record
2. Navigate to **NexAML** tab → Sanctions Screening section
3. Click **Screen Now**
4. Review results in **Screenings** smart button

**Automatic Screening:**
- Enable in Settings → NexAML → Auto-Screen New Customers
- All new customers will be automatically screened on creation

**Handle Matches:**
- Review match details in screening record
- If false positive, click **Mark as False Positive**
- Add review notes for audit trail

### Transaction Monitoring

**Automatic Monitoring:**
- Enabled by default for invoices and payments
- Rules evaluate automatically when transactions are posted
- Alerts are created when rules trigger

**Review Alerts:**
1. Navigate to **NexAML → Operations → Alerts**
2. Filter by **New Alerts** or **High Severity**
3. Open alert to review details
4. Actions:
   - **Investigate**: Mark as under investigation
   - **Close**: No action required
   - **Escalate to Case**: Create investigation case

### Case Management

**Create Case:**
- Escalate from alert, or
- Create manually: **NexAML → Operations → Cases → Create**

**Case Workflow:**
1. **Open**: Initial state
2. **Investigating**: Actively reviewing
3. **Review**: Under management review
4. **Resolved**: Decision made
5. **Closed**: Case finalized

**Case Actions:**
- Link related alerts and transactions
- Add investigation notes (rich text)
- Assign to team member
- Schedule activities
- Track resolution (SAR filed, no action, etc.)

### Reporting

**Generate Reports:**
1. Navigate to **NexAML → Reporting → Generate Report**
2. Select report type:
   - **SAR**: Suspicious Activity Report
   - **STR**: Suspicious Transaction Report
   - **Periodic Summary**: Compliance overview
   - **Risk Summary**: Customer risk analysis
3. Set date range and filters
4. Choose output format (PDF, Excel, goAML XML)
5. Click **Generate Report**

**Report Formats:**
- **PDF**: Formatted reports for management/regulators
- **Excel**: Data analysis and record keeping
- **goAML XML**: Regulatory submission format

## Architecture

### Models

- `res.partner`: Extended with AML risk assessment fields
- `aml.product`: Product risk classifications
- `aml.control`: Risk mitigation controls
- `aml.screening`: Sanctions screening results
- `aml.transaction.rule`: Transaction monitoring rules
- `aml.alert`: Transaction monitoring alerts
- `aml.case`: AML investigation cases
- `account.move`: Extended with monitoring fields
- `res.config.settings`: NexAML configuration
- `report.wizard`: Report generation wizard

### Model Relationships

```
res.partner
  ├── aml.product (Many2many)
  ├── aml.control (Many2many)
  ├── aml.screening (One2many)
  └── aml.alert (One2many)

aml.case
  ├── res.partner (Many2one)
  ├── aml.alert (Many2many)
  └── account.move (Many2many)

aml.alert
  ├── res.partner (Many2one)
  ├── account.move (Many2one)
  ├── aml.transaction.rule (Many2one)
  └── aml.case (Many2one)

account.move
  └── aml.alert (One2many)
```

### API Integration

**Yente API (OpenSanctions):**
- Endpoint: `POST /search`
- Authentication: API key (optional for demo URL)
- Request format: JSON with entity details
- Response: Match results with confidence scores

Example payload:
```python
{
    "schema": "Person",  # or "Company"
    "properties": {
        "name": ["John Doe"],
        "birthDate": ["1980-01-01"],
        "country": ["US"]
    }
}
```

### Security

**Multi-Company:**
- Record rules ensure company-specific data access
- Partners inherit base Odoo company rules
- Cases, alerts, screenings filtered by company

**Access Rights:**
- All models accessible to `base.group_user`
- Settings restricted to `base.group_system`
- No custom security groups required

## Testing

### Run Unit Tests

```bash
./odoo-bin -d test_db -i nexaml --test-tags=nexaml --stop-after-init
```

### Run Integration Tests

```bash
./odoo-bin -d test_db -i nexaml --test-tags=nexaml,integration --stop-after-init
```

### Test Coverage

```bash
coverage run --source=addons/nexaml ./odoo-bin -d test_db -i nexaml --test-tags=nexaml --stop-after-init
coverage report
```

## Customization

### Add Custom Transaction Rule

```python
rule = env['aml.transaction.rule'].create({
    'name': 'Custom Rule',
    'code': 'CUSTOM_001',
    'rule_type': 'threshold',
    'amount_threshold': 100000,
    'currency_id': env.ref('base.USD').id,
    'applies_to_risk_level': 'high',
    'alert_severity': 'critical',
    'active': True,
})
```

### Extend Risk Calculation

Override `_compute_risk()` in `res.partner`:

```python
@api.depends('customer_risk', 'geography_risk', 'product_risk', 'channel_risk')
def _compute_risk(self):
    super()._compute_risk()
    # Add custom logic
    for partner in self:
        if partner.country_id.code == 'XX':
            partner.inherent_risk *= 1.5
```

### Custom Report Template

Create QWeb template in `reports/` directory:

```xml
<template id="custom_report_template">
    <t t-call="web.html_container">
        <!-- Custom report content -->
    </t>
</template>
```

## Performance

### Optimization Tips

1. **Screening**:
   - Use cron job for batch rescreening
   - Limit auto-screening to main contacts only
   - Cache API responses (not implemented)

2. **Transaction Monitoring**:
   - Keep active rules count reasonable (< 20)
   - Use risk level filtering to reduce evaluations
   - Index monitored field on account.move

3. **Reports**:
   - Generate reports during off-peak hours
   - Use date range filters to limit data
   - Cache periodic summaries

### Expected Performance

- Risk calculation: < 100ms per partner
- Screening API call: 1-3 seconds per partner
- Rule evaluation: < 500ms per transaction
- Report generation: 2-10 seconds depending on data

## Troubleshooting

### Screening API Errors

**Issue**: "Yente API URL not configured"
- **Solution**: Set URL in Settings → NexAML

**Issue**: API timeout or connection error
- **Solution**: Check network connectivity, verify URL, try demo URL

### Transaction Monitoring Not Working

**Issue**: Alerts not created for transactions
- **Solution**:
  - Verify monitoring enabled in settings
  - Check rules are active
  - Confirm transaction is posted
  - Review logs for errors

### Report Generation Fails

**Issue**: PDF generation error
- **Solution**: Check wkhtmltopdf installation

**Issue**: Excel export fails
- **Solution**: Install xlsxwriter: `pip install xlsxwriter`

## Support

- **Documentation**: See `USER_GUIDE.md` for detailed user instructions
- **Issue Tracker**: Report bugs on GitHub
- **Email**: support@nexaml.com

## License

LGPL-3

## Credits

Developed by NexAML Team
