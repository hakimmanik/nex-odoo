# NexAML Module Upgrade Instructions

## Error: "res.partner"."party_type" field is undefined

This error occurs because new fields were added to `res.partner` model but the module needs to be upgraded to add them to the database.

## Solution: Upgrade the Module

### Option 1: Command Line (Recommended)

```bash
# Stop Odoo if running
# Then run with upgrade flag:
python3 odoo-bin -u nexaml -d your_database_name
```

### Option 2: From Odoo UI

1. Go to **Apps** menu
2. Remove **Apps** filter from search bar
3. Search for **NexAML**
4. Click **Upgrade** button

### Option 3: Developer Mode

1. Enable Developer Mode: Settings > Activate Developer Mode
2. Go to Apps
3. Click **Update Apps List**
4. Search for **NexAML**
5. Click **Upgrade**

## What This Upgrade Adds

### New Fields on res.partner (Contacts)

- `party_type` - Type of related party (director, shareholder, UBO, etc.)
- `ownership_percentage` - Ownership percentage for shareholders/UBOs
- `is_ubo` - Auto-computed flag for Ultimate Beneficial Owners (≥25% ownership)

### New Transaction Monitoring Rules

- **Dormant Account Reactivation** - Alerts on large transactions from inactive accounts
- **New Customer Large Transaction** - Alerts when new customers make large transactions
- **Potential Structuring Pattern** - Detects multiple transactions just below thresholds
- **High Weekly Transaction Volume** - Cumulative $75k in 7 days
- **High Monthly Transaction Volume** - Cumulative $200k in 30 days

### New Features

- **Multi-layer Screening** - Screens customer + related parties (directors, shareholders, UBOs)
- **Scenario-Based Risk Overrides** - Auto-elevates risk to High when:
  - Customer or UBO is PEP
  - Customer or UBO has sanctions match
- **Automatic Risk Reassessment** - Daily cron job reassesses partners based on:
  - Next review date
  - Risk level (High: 6mo, Medium: 12mo, Low: 24mo)

### New URL Routes

After upgrade, you can access NexAML via clean URLs:

- `/aml/dashboard` - Dashboard
- `/aml/cases` - Cases list
- `/aml/alerts` - Alerts list
- `/aml/screenings` - Screenings list
- `/aml/rules` - Transaction rules
- `/aml/case/123` - Specific case
- `/aml/alert/456` - Specific alert

## Verification

After upgrade, verify:

1. **New Fields Work**:

   - Open a contact/partner
   - Check for "Related Party Info" tab (visible only for contacts with parent)
   - Fields should be visible and editable

2. **New Rules Exist**:

   - Go to Configuration > Transaction Rules
   - Should see 10 rules total (5 original + 5 new)

3. **Multi-layer Screening**:

   - Open a customer with contacts
   - Add contacts with party_type set to "director", "shareholder", or "UBO"
   - Click "Screen Now" in NexAML tab
   - Should see notification showing number of parties screened

4. **Custom URLs Work**:
   - Navigate to `/aml/dashboard`
   - Should redirect to dashboard view

## Troubleshooting

### Module Doesn't Upgrade

```bash
# Force upgrade with database update
python3 odoo-bin -u nexaml -d your_database --init=nexaml
```

### Fields Still Missing

```bash
# Restart Odoo server
sudo systemctl restart odoo
# Or if running manually:
# Ctrl+C to stop, then restart with -u nexaml
```

### Permission Errors on Related Party Tab

The "Related Party Info" tab is restricted to `base.group_no_one` (Settings/Technical Features) by default for testing. To make it visible to all users, edit `views/res_partner_views.xml` and remove `groups="base.group_no_one"` from line 94.

## Database Backup

**IMPORTANT**: Always backup your database before upgrading:

```bash
# Backup database
pg_dump your_database_name > backup_$(date +%Y%m%d_%H%M%S).sql

# If something goes wrong, restore:
# dropdb your_database_name
# createdb your_database_name
# psql your_database_name < backup_YYYYMMDD_HHMMSS.sql
```
