# NexAML Production Deployment Checklist

## Pre-Deployment

### 1. Environment Preparation
- [ ] Production database backup created
- [ ] Odoo version confirmed (19.0)
- [ ] Python dependencies installed (`requests`, `xlsxwriter`)
- [ ] Server resources adequate (CPU, RAM, storage)
- [ ] Network access to Yente API confirmed

### 2. Code Review
- [ ] All tests passing (`--test-tags=nexaml`)
- [ ] Code reviewed by peer
- [ ] No TODO/FIXME comments in production code
- [ ] Logging levels appropriate (INFO/WARNING, not DEBUG)

### 3. Configuration Files
- [ ] Production Yente API credentials obtained
- [ ] goAML submission endpoint configured (if applicable)
- [ ] Email server configured for notifications
- [ ] Backup schedule configured

## Deployment Steps

### 1. Module Installation

```bash
# Stop Odoo service
sudo systemctl stop odoo

# Copy module to addons directory
cp -r nexaml /opt/odoo/addons/

# Set correct permissions
chown -R odoo:odoo /opt/odoo/addons/nexaml
chmod -R 755 /opt/odoo/addons/nexaml

# Start Odoo and install module
sudo systemctl start odoo
```

Install via UI:
1. Apps → Update Apps List
2. Search "NexAML"
3. Click Install
4. Wait for installation to complete

### 2. Initial Configuration

#### Settings (Settings → General Settings → NexAML)

**Sanctions Screening:**
- [ ] Yente API URL: `[production URL]`
- [ ] API Key: `[production key]`
- [ ] Match Threshold: `70` (adjust based on risk tolerance)
- [ ] Auto-Screen: `True` (recommended)

**Risk Assessment:**
- [ ] EDD Threshold: `Medium Risk and Above` (or High Risk Only)

**Transaction Monitoring:**
- [ ] Monitor Invoices: `True`
- [ ] Monitor Payments: `True`

#### Transaction Rules (NexAML → Configuration → Transaction Rules)

Review and adjust default rules:
- [ ] HIGH_VALUE: Amount threshold appropriate for your business
- [ ] VELOCITY: Transaction count appropriate
- [ ] RAPID_VELOCITY: Time period appropriate
- [ ] HIGH_RISK_LARGE: Amounts appropriate
- [ ] ROUND_AMOUNT: Active/inactive based on needs

Add custom rules as needed.

#### Products & Controls (NexAML → Configuration)

- [ ] Create product risk classifications for your services
- [ ] Create risk controls your organization uses
- [ ] Document control mitigation factors

### 3. Cron Jobs

Verify cron job is active:
- **Name**: NexAML: Rescreen High-Risk Partners
- **Interval**: Daily
- **Next Call**: 2:00 AM (or adjust to off-peak hours)

### 4. Security & Permissions

#### Multi-Company Setup (if applicable)
- [ ] Verify company-specific record rules working
- [ ] Test cross-company access restrictions
- [ ] Ensure users assigned to correct companies

#### User Training
- [ ] Compliance team trained on module usage
- [ ] Key users familiar with workflows
- [ ] Documentation distributed

### 5. Data Migration

See `DATA_MIGRATION.md` for detailed steps.

**Summary:**
- [ ] Existing customers migrated with default risk factors
- [ ] Bulk risk assessment performed
- [ ] Initial screening completed for high-risk customers
- [ ] Data quality verified

## Post-Deployment

### 1. Smoke Testing

#### Test Scenarios:
1. **Customer Risk Assessment**
   - [ ] Create new customer
   - [ ] Set risk factors
   - [ ] Click Assess Risk
   - [ ] Verify risk level calculated correctly

2. **Sanctions Screening**
   - [ ] Create test customer with known sanctioned name
   - [ ] Click Screen Now
   - [ ] Verify match detected
   - [ ] Mark as false positive

3. **Transaction Monitoring**
   - [ ] Create high-value invoice
   - [ ] Post invoice
   - [ ] Verify alert created
   - [ ] Review alert details

4. **Case Management**
   - [ ] Escalate alert to case
   - [ ] Move through workflow states
   - [ ] Add investigation notes
   - [ ] Close case

5. **Reporting**
   - [ ] Generate Periodic Summary
   - [ ] Generate Risk Summary (Excel)
   - [ ] Verify reports contain data

### 2. Performance Monitoring

First Week Checklist:
- [ ] Monitor API response times (< 5 seconds)
- [ ] Monitor rule evaluation time (< 1 second per transaction)
- [ ] Check cron job completion (should complete in < 30 minutes)
- [ ] Review server load during peak hours

Tools:
```bash
# Check Odoo logs
tail -f /var/log/odoo/odoo.log | grep nexaml

# Monitor API calls
grep "Yente API" /var/log/odoo/odoo.log | wc -l

# Check database performance
psql -d production_db -c "SELECT * FROM pg_stat_statements WHERE query LIKE '%aml%' ORDER BY total_time DESC LIMIT 10;"
```

### 3. Error Monitoring

Monitor for:
- [ ] API connection failures
- [ ] Rule evaluation errors
- [ ] Report generation failures
- [ ] Database constraint violations

Set up alerts for critical errors:
```python
# Add to odoo.conf or environment
log_handler = :INFO,werkzeug:WARNING,odoo.addons.nexaml:WARNING
```

### 4. Compliance Verification

- [ ] Test SAR report generation
- [ ] Test goAML XML export
- [ ] Verify audit trail (chatter messages)
- [ ] Confirm data retention policies

### 5. User Acceptance

- [ ] Compliance officer sign-off
- [ ] Key users trained and comfortable
- [ ] Feedback collected and documented
- [ ] Minor issues logged for future updates

## Rollback Plan

If critical issues occur:

### 1. Immediate Rollback
```bash
# Disable auto-screening
psql -d production_db -c "UPDATE ir_config_parameter SET value='False' WHERE key='nexaml.auto_screen_on_create';"

# Disable transaction monitoring
psql -d production_db -c "UPDATE ir_config_parameter SET value='False' WHERE key='nexaml.monitor_invoices';"
psql -d production_db -c "UPDATE ir_config_parameter SET value='False' WHERE key='nexaml.monitor_payments';"

# Disable cron job
psql -d production_db -c "UPDATE ir_cron SET active=false WHERE name LIKE '%NexAML%';"
```

### 2. Full Rollback (if needed)
```bash
# Stop Odoo
sudo systemctl stop odoo

# Restore backup
pg_restore -d production_db backup_before_nexaml.dump

# Remove module
rm -rf /opt/odoo/addons/nexaml

# Start Odoo
sudo systemctl start odoo
```

## Performance Tuning

### Database Indexes

Add indexes for frequently queried fields:
```sql
CREATE INDEX idx_partner_risk_level ON res_partner(risk_level);
CREATE INDEX idx_partner_sanctions_status ON res_partner(sanctions_status);
CREATE INDEX idx_alert_status ON aml_alert(status);
CREATE INDEX idx_alert_severity ON aml_alert(severity);
CREATE INDEX idx_case_state ON aml_case(state);
CREATE INDEX idx_screening_status ON aml_screening(status);
CREATE INDEX idx_move_monitored ON account_move(monitored);
```

### Configuration Tuning

**For High Transaction Volume:**
```python
# Increase worker processes
workers = 8  # Adjust based on CPU cores

# Increase database pool size
db_maxconn = 128

# Optimize limit settings
limit_time_cpu = 300
limit_time_real = 600
```

**For Many Customers:**
- Run screening cron less frequently (weekly instead of daily)
- Batch process customers (100-500 at a time)
- Consider implementing API response caching

## Monitoring Dashboard

Set up monitoring for:
1. **Cases**: Open, investigating, resolved counts
2. **Alerts**: New, high-severity counts
3. **Screenings**: Matches found, false positives
4. **Performance**: API latency, rule evaluation time
5. **Errors**: Failed API calls, rule errors

Example Grafana queries (if using metrics):
```
# Alert creation rate
rate(nexaml_alerts_created_total[5m])

# Average screening time
rate(nexaml_screening_duration_seconds_sum[5m]) / rate(nexaml_screening_duration_seconds_count[5m])

# Case resolution time
histogram_quantile(0.95, rate(nexaml_case_resolution_seconds_bucket[5m]))
```

## Sign-Off

Deployment completed by: _____________________ Date: __________

Compliance officer approval: _____________________ Date: __________

IT manager approval: _____________________ Date: __________

## Post-Deployment Notes

Document any issues, deviations, or lessons learned:

```
[Space for notes]
```
