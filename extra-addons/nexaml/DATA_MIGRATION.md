# NexAML Data Migration Plan

## Overview

This document outlines the process for migrating existing customer data when deploying NexAML to a production environment with existing res.partner records.

## Pre-Migration Assessment

### 1. Data Inventory

```python
# Run in Odoo shell
env = api.Environment(cr, SUPERUSER_ID, {})

# Count existing customers
customers = env['res.partner'].search([('customer_rank', '>', 0)])
print(f"Total customers: {len(customers)}")

# Count companies vs individuals
companies = customers.filtered(lambda p: p.is_company)
individuals = customers.filtered(lambda p: not p.is_company)
print(f"Companies: {len(companies)}")
print(f"Individuals: {len(individuals)}")

# Count by country
countries = {}
for partner in customers:
    country = partner.country_id.name or 'Unknown'
    countries[country] = countries.get(country, 0) + 1
print("By country:", countries)
```

### 2. Backup

```bash
# Create full database backup
pg_dump -Fc production_db > backup_before_migration_$(date +%Y%m%d).dump

# Export customer data to CSV (optional)
psql -d production_db -c "COPY (SELECT id, name, country_id, is_company FROM res_partner WHERE customer_rank > 0) TO '/tmp/customers_export.csv' CSV HEADER;"
```

## Migration Steps

### Step 1: Install Module (Without Auto-Screening)

Before installation, ensure auto-screening is disabled:

```python
# Set in database before installing module
INSERT INTO ir_config_parameter (key, value, create_date, write_date, create_uid, write_uid)
VALUES ('nexaml.auto_screen_on_create', 'False', NOW(), NOW(), 1, 1)
ON CONFLICT (key) DO UPDATE SET value='False';
```

Then install the module normally.

### Step 2: Assign Default Risk Factors

Create migration script: `migrate_customer_risk.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate_customer_risk(env):
    """Assign default risk factors to existing customers."""

    Partner = env['res.partner']

    # Get all customers without risk assessment
    customers = Partner.search([
        ('customer_rank', '>', 0),
        ('customer_risk', '=', False)
    ])

    _logger.info(f"Migrating {len(customers)} customers...")

    # Define default risk factors by country
    high_risk_countries = ['AF', 'BY', 'CD', 'CU', 'IR', 'KP', 'MM', 'RU', 'SD', 'SY', 'VE', 'YE', 'ZW']
    medium_risk_countries = ['CN', 'PK', 'UA', 'NG', 'KE']

    batch_size = 100
    updated = 0

    for i in range(0, len(customers), batch_size):
        batch = customers[i:i+batch_size]

        for partner in batch:
            # Determine geography risk based on country
            country_code = partner.country_id.code if partner.country_id else None

            if country_code in high_risk_countries:
                geography_risk = '3'
            elif country_code in medium_risk_countries:
                geography_risk = '2'
            else:
                geography_risk = '1'

            # Default risk factors
            # Adjust these based on your business model
            partner.write({
                'customer_risk': '2',  # Medium by default
                'geography_risk': geography_risk,
                'product_risk': '2',  # Medium by default
                'channel_risk': '1',  # Low (assuming existing business)
            })

            updated += 1

            if updated % 100 == 0:
                _logger.info(f"Updated {updated}/{len(customers)} customers")
                env.cr.commit()  # Commit in batches

    env.cr.commit()
    _logger.info(f"Migration complete. Updated {updated} customers.")

    # Calculate risks
    _logger.info("Calculating risk levels...")
    customers._compute_risk()
    env.cr.commit()

    # Report summary
    high_risk = Partner.search_count([('customer_rank', '>', 0), ('risk_level', '=', 'high')])
    medium_risk = Partner.search_count([('customer_rank', '>', 0), ('risk_level', '=', 'medium')])
    low_risk = Partner.search_count([('customer_rank', '>', 0), ('risk_level', '=', 'low')])

    _logger.info(f"Risk distribution: High={high_risk}, Medium={medium_risk}, Low={low_risk}")

    return {
        'total': updated,
        'high_risk': high_risk,
        'medium_risk': medium_risk,
        'low_risk': low_risk,
    }

# Run migration
if __name__ == '__main__':
    with api.Environment.manage():
        registry = odoo.registry(dbname)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            result = migrate_customer_risk(env)
            print(f"Migration complete: {result}")
```

Run migration:
```bash
python3 migrate_customer_risk.py
```

### Step 3: Bulk Screening (High-Risk Only)

To avoid overwhelming the API, screen only high-risk customers initially:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def bulk_screen_customers(env, risk_levels=['high']):
    """Screen customers in batches."""

    Partner = env['res.partner']

    # Get high-risk customers without screening
    domain = [
        ('customer_rank', '>', 0),
        ('risk_level', 'in', risk_levels),
        ('sanctions_status', '=', 'not_screened')
    ]

    customers = Partner.search(domain)
    _logger.info(f"Screening {len(customers)} customers...")

    batch_size = 50  # API rate limiting
    screened = 0
    errors = 0

    for i in range(0, len(customers), batch_size):
        batch = customers[i:i+batch_size]

        for partner in batch:
            try:
                partner.action_screen_sanctions()
                screened += 1

                # Rate limiting (adjust based on API limits)
                time.sleep(0.5)

                if screened % 10 == 0:
                    _logger.info(f"Screened {screened}/{len(customers)} customers")
                    env.cr.commit()

            except Exception as e:
                _logger.error(f"Error screening {partner.name}: {e}")
                errors += 1

        # Pause between batches
        time.sleep(5)

    env.cr.commit()

    # Report results
    matches = env['aml.screening'].search_count([
        ('partner_id', 'in', customers.ids),
        ('status', '=', 'match')
    ])

    _logger.info(f"Screening complete. Screened={screened}, Errors={errors}, Matches={matches}")

    return {
        'screened': screened,
        'errors': errors,
        'matches': matches,
    }

# Run screening
if __name__ == '__main__':
    with api.Environment.manage():
        registry = odoo.registry(dbname)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            result = bulk_screen_customers(env, risk_levels=['high', 'medium'])
            print(f"Screening complete: {result}")
```

Run screening:
```bash
# Screen high-risk only
python3 bulk_screen_customers.py

# Or via Odoo shell
odoo-bin shell -d production_db -c /etc/odoo/odoo.conf
>>> env['res.partner'].search([('risk_level', '=', 'high')]).action_screen_sanctions()
```

### Step 4: Data Quality Verification

```python
def verify_migration(env):
    """Verify migration data quality."""

    Partner = env['res.partner']
    issues = []

    # Check 1: All customers have risk factors
    missing_risk = Partner.search([
        ('customer_rank', '>', 0),
        '|', ('customer_risk', '=', False),
        '|', ('geography_risk', '=', False),
        '|', ('product_risk', '=', False),
        ('channel_risk', '=', False)
    ])
    if missing_risk:
        issues.append(f"WARN: {len(missing_risk)} customers missing risk factors")

    # Check 2: Risk calculations completed
    missing_level = Partner.search([
        ('customer_rank', '>', 0),
        ('risk_level', '=', False)
    ])
    if missing_level:
        issues.append(f"ERROR: {len(missing_level)} customers missing risk level")

    # Check 3: High-risk customers screened
    high_risk_not_screened = Partner.search([
        ('customer_rank', '>', 0),
        ('risk_level', '=', 'high'),
        ('sanctions_status', '=', 'not_screened')
    ])
    if high_risk_not_screened:
        issues.append(f"WARN: {len(high_risk_not_screened)} high-risk customers not screened")

    # Check 4: Screening matches reviewed
    unreviewed_matches = env['aml.screening'].search([
        ('status', '=', 'match'),
        ('reviewed_by', '=', False)
    ])
    if unreviewed_matches:
        issues.append(f"ACTION: {len(unreviewed_matches)} screening matches need review")

    # Print report
    if not issues:
        print("✓ Migration verification passed!")
    else:
        print("Migration verification issues:")
        for issue in issues:
            print(f"  - {issue}")

    return len([i for i in issues if i.startswith('ERROR')]) == 0

# Run verification
verify_migration(env)
```

### Step 5: Review Screening Matches

1. Navigate to **NexAML → Operations → Screenings**
2. Filter by **Status = Match**
3. Review each match:
   - Check match score and details
   - Research if it's a true positive
   - Mark false positives
   - Escalate true matches to cases

### Step 6: Enable Auto-Screening

Once existing data is migrated:

```python
env['ir.config_parameter'].sudo().set_param('nexaml.auto_screen_on_create', 'True')
```

## Post-Migration Tasks

### 1. Product & Control Assignment

Manually assign products and controls to key customers:

1. Identify customers using high-risk products
2. Navigate to customer record → NexAML tab
3. Add products to **Products** field
4. Add controls to **Controls** field
5. Click **Assess Risk** to recalculate

### 2. EDD Flag Review

Review customers flagged for EDD:

```python
edd_required = env['res.partner'].search([
    ('customer_rank', '>', 0),
    ('edd_required', '=', True)
])
print(f"{len(edd_required)} customers require EDD")
```

Assign activities for EDD review.

### 3. Next Review Dates

Set next review dates for high-risk customers:

```python
from datetime import timedelta

high_risk = env['res.partner'].search([
    ('customer_rank', '>', 0),
    ('risk_level', '=', 'high')
])

for partner in high_risk:
    # Review in 6 months
    partner.next_review_date = fields.Date.today() + timedelta(days=180)
```

### 4. Historical Data

Consider whether to:
- Screen historical transactions (typically not required)
- Create cases for past suspicious activity (if identified)
- Document pre-migration compliance state

## Rollback Procedure

If migration has issues:

```sql
-- Rollback risk factors
UPDATE res_partner
SET customer_risk = NULL,
    geography_risk = NULL,
    product_risk = NULL,
    channel_risk = NULL,
    risk_level = NULL,
    inherent_risk = 0,
    residual_risk = 0
WHERE customer_rank > 0;

-- Delete screening records
DELETE FROM aml_screening;

-- Reset sanctions status
UPDATE res_partner
SET sanctions_status = 'not_screened'
WHERE customer_rank > 0;

-- Commit
COMMIT;
```

Then restore from backup if needed.

## Migration Timeline

**Recommended schedule for 10,000 customers:**

- **Day 1 (2 hours)**: Install module, run risk migration script
- **Day 2 (4 hours)**: Screen high-risk customers (assuming ~500)
- **Day 3 (4 hours)**: Review screening matches
- **Day 4 (2 hours)**: Screen medium-risk customers (if time permits)
- **Day 5 (1 hour)**: Verification and cleanup
- **Day 6+**: Ongoing - screen low-risk customers in batches

## Support During Migration

- Database administrator on standby
- Compliance team available for match review
- API rate limits monitored
- Server resources monitored
- Backup strategy verified

## Sign-Off

Migration plan reviewed by: _____________________ Date: __________

Migration executed by: _____________________ Date: __________

Verification completed by: _____________________ Date: __________
