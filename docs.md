# TECHNICAL REQUIREMENTS DOCUMENT (TRD)

# AML Compliance System - Nex Systems

---

## DOCUMENT CONTROL

| Field                | Details                                                 |
| -------------------- | ------------------------------------------------------- |
| **Document Title**   | Technical Requirements Document - AML Compliance System |
| **Project Name**     | Nex Systems - Enterprise Business Management Platform   |
| **Document Version** | 1.0                                                     |
| **Date**             | 2025-11-13                                              |
| **Status**           | Draft                                                   |
| **Author**           | Technical Team                                          |
| **Classification**   | Internal - Confidential                                 |

### REVISION HISTORY

| Version | Date       | Author         | Description          |
| ------- | ---------- | -------------- | -------------------- |
| 1.0     | 2025-11-13 | Technical Team | Initial TRD creation |

### DOCUMENT APPROVAL

| Role               | Name | Signature | Date |
| ------------------ | ---- | --------- | ---- |
| Product Owner      |      |           |      |
| Technical Lead     |      |           |      |
| Compliance Officer |      |           |      |
| Project Manager    |      |           |      |

---

## TABLE OF CONTENTS

1. [Document Information](#1-document-information)
2. [Customer Risk Assessment (CRA)](#2-customer-risk-assessment-cra)
3. [Sanctions Screening](#3-sanctions-screening)
4. [Transaction Monitoring](#4-transaction-monitoring)
5. [Case Management](#5-case-management)
6. [Alert Management](#6-alert-management)
7. [Reporting & Compliance](#7-reporting--compliance)
8. [Configuration & Settings](#8-configuration--settings)
9. [API Specifications](#9-api-specifications)
10. [Database Schema](#10-database-schema)
11. [Integration & Architecture](#11-integration--architecture)
12. [Non-Functional Requirements](#12-non-functional-requirements)

---

## 1. DOCUMENT INFORMATION

### 1.1 PURPOSE

This Technical Requirements Document (TRD) defines the technical specifications, architecture, and implementation details for the Anti-Money Laundering (AML) Compliance System within the Nex Systems platform. It serves as the authoritative technical reference for developers, architects, and compliance teams.

**Primary Objectives:**

- Define technical architecture and design patterns for AML features
- Specify functional requirements with mathematical precision
- Document API contracts, data models, and integration points
- Establish performance, security, and compliance standards
- Provide implementation guidelines for development teams

### 1.2 SCOPE

**In Scope:**

- Customer Risk Assessment (CRA) engine and algorithms
- Sanctions screening system with multi-source integration
- Transaction monitoring rules and detection engine
- Case management workflow and lifecycle
- Alert generation and resolution
- Regulatory reporting (SAR/STR/ECDD)
- Configuration and settings management
- API specifications and data models
- Integration architecture

**Out of Scope:**

- General customer management features (covered in separate TRD)
- Payment processing infrastructure
- User authentication and authorization (covered in Auth TRD)
- Infrastructure provisioning and deployment
- Third-party vendor selection and procurement

### 1.3 AUDIENCE

| Audience                | Usage                                                       |
| ----------------------- | ----------------------------------------------------------- |
| **Software Engineers**  | Implementation reference, API integration, algorithm coding |
| **Solution Architects** | System design, integration patterns, scalability planning   |
| **QA Engineers**        | Test case development, acceptance criteria validation       |
| **Product Owners**      | Feature understanding, backlog prioritization               |
| **Compliance Officers** | Regulatory validation, rule configuration                   |
| **DevOps Engineers**    | Deployment planning, monitoring setup                       |
| **Technical Writers**   | User documentation, API documentation                       |

### 1.4 DEFINITIONS & ACRONYMS

| Term               | Definition                                                                     |
| ------------------ | ------------------------------------------------------------------------------ |
| **AML**            | Anti-Money Laundering - regulatory framework to prevent money laundering       |
| **CRA**            | Customer Risk Assessment - methodology to evaluate customer risk               |
| **SAR**            | Suspicious Activity Report - regulatory filing for suspicious activities       |
| **STR**            | Suspicious Transaction Report - report for specific suspicious transactions    |
| **PEP**            | Politically Exposed Person - individual with prominent public position         |
| **UBO**            | Ultimate Beneficial Owner - natural person who ultimately owns/controls entity |
| **KYC**            | Know Your Customer - process of verifying customer identity                    |
| **EDD**            | Enhanced Due Diligence - heightened customer verification for high-risk cases  |
| **goAML**          | Global Anti-Money Laundering - standardized reporting format                   |
| **OFAC**           | Office of Foreign Assets Control - US sanctions authority                      |
| **Sanctions**      | Economic/trade restrictions imposed by governments                             |
| **Fuzzy Matching** | Approximate string matching algorithm                                          |
| **Residual Risk**  | Risk remaining after applying controls/mitigations                             |
| **Inherent Risk**  | Raw risk before any controls are applied                                       |
| **ORPC**           | Type-safe RPC framework used for API layer                                     |
| **Prisma**         | ORM (Object-Relational Mapping) tool for database operations                   |
| **BullMQ**         | Queue system for background job processing                                     |

### 1.5 REFERENCES

| Document            | Description                      | Location                                         |
| ------------------- | -------------------------------- | ------------------------------------------------ |
| CLAUDE.md           | Project coding standards         | `/CLAUDE.md`                                     |
| Prisma Schema       | Database schema definition       | `/prisma/schema.prisma`                          |
| ORPC Router         | API routing configuration        | `/src/infrastructure/api/router.ts`              |
| CRA Calculator      | Risk calculation implementation  | `/src/features/cra/calculator.ts`                |
| Sanctions Service   | Screening service implementation | `/src/features/sanctions/services/`              |
| Transaction Monitor | Monitoring engine                | `/src/features/transaction-monitoring/engine.ts` |
| Case Management     | Case workflow implementation     | `/src/features/cases/`                           |

### 1.6 SYSTEM REQUIREMENTS

**Data Storage:**

- Relational database with ACID compliance
- Support for complex queries and transactions
- JSON/JSONB field support for flexible schema
- Minimum 7-year data retention capability

**Performance Requirements:**

- Synchronous operations: < 3 seconds response time
- Risk calculations: < 2 seconds completion time
- Screening operations: < 5 seconds completion time
- Transaction monitoring: < 1 minute processing latency
- Support for 100+ concurrent users per organization
- Minimum 1000 risk assessments per hour capacity

**Availability:**

- 99.9% uptime for compliance operations
- Zero data loss tolerance for compliance records
- Backup and disaster recovery mechanisms

**Integration Capabilities:**

- RESTful API or equivalent for external integrations
- Webhook support for event notifications
- Bulk data import/export capabilities
- Standard authentication mechanisms (OAuth2, API keys)

### 1.7 SYSTEM CONTEXT

```
┌─────────────────────────────────────────────────────────────┐
│                     NEX SYSTEMS PLATFORM                     │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐    │
│  │   Customer  │  │ Transaction │  │  Organization    │    │
│  │ Management  │  │   System    │  │   Management     │    │
│  └──────┬──────┘  └──────┬──────┘  └────────┬─────────┘    │
│         │                 │                   │              │
│         └─────────────────┼───────────────────┘              │
│                           │                                  │
│         ┌─────────────────▼───────────────────┐             │
│         │                                      │             │
│         │      AML COMPLIANCE SYSTEM           │             │
│         │                                      │             │
│         │  • Risk Assessment (CRA)             │             │
│         │  • Sanctions Screening               │             │
│         │  • Transaction Monitoring            │             │
│         │  • Case Management                   │             │
│         │  • Alert Management                  │             │
│         │  • Regulatory Reporting              │             │
│         │                                      │             │
│         └──────────────────┬───────────────────┘             │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │ OpenSanctions│  │  AI Service  │  │   Document   │
  │    (Yente)   │  │  (Narrative) │  │   Storage    │
  └──────────────┘  └──────────────┘  └──────────────┘
```

### 1.8 ASSUMPTIONS & CONSTRAINTS

**Assumptions:**

1. Database infrastructure available with sufficient capacity for multi-year data retention
2. Caching and queue management infrastructure available for background processing
3. Organization has valid credentials for external screening services
4. Users have appropriate role-based access configured
5. Customer data quality meets minimum standards for risk assessment
6. Network connectivity to external screening services maintained
7. Regulatory requirements align with UAE/MENA region standards

**Constraints:**

1. Must comply with GDPR, UAE AML regulations, and FATF standards
2. API response time < 3 seconds for synchronous operations
3. Screening results must be available within 5 seconds
4. Risk calculations must complete within 2 seconds
5. System must support multi-tenant architecture
6. Audit trail required for all compliance-related actions
7. Data retention: minimum 7 years for compliance records
8. Must support concurrent users per organization: up to 100
9. Transaction monitoring must process real-time (< 1 minute latency)

### 1.9 DEPENDENCIES

**Internal Dependencies:**

- Customer Management module (customer data, parties)
- Transaction System (transaction data, payment processing)
- Organization Management (configuration, settings)
- Authentication & Authorization (user context, permissions)
- Document Management (case attachments, evidence storage)

**External Dependencies:**

- Sanctions screening service (e.g., OpenSanctions, Dow Jones, etc.)
- AI/ML service for narrative generation
- Email/notification service
- Object/file storage for documents and attachments

### 1.10 FUNCTIONAL REQUIREMENTS OVERVIEW

**Risk Assessment:**

- Calculate customer inherent risk using weighted multi-factor methodology
- Apply control mitigations to derive residual risk
- Support scenario-based risk overrides (PEP, sanctions, jurisdictions)
- Risk levels: Low (1.0-1.6), Medium (1.7-2.3), High (2.4-3.0)

**Screening:**

- Screen customers and related parties against sanctions lists
- Support fuzzy matching with configurable thresholds
- Match on name, date of birth, nationality
- Record screening history with audit trail

**Transaction Monitoring:**

- Real-time rule-based transaction analysis
- Detect patterns: high-value, velocity, structuring, layering
- Generate alerts based on configurable thresholds
- Risk score transactions dynamically

**Case Management:**

- Track investigations from creation to resolution
- Support workflow: open → investigating → review → resolved/closed
- Link cases to customers, transactions, alerts
- Document decisions and outcomes
- Maintain complete audit trail

**Reporting:**

- Generate regulatory reports (SAR/STR) in goAML format
- AI-assisted narrative generation
- Export transaction data with risk indicators
- Support multiple report types (ECDD, AIF, Basic)

---

## 2. CUSTOMER RISK ASSESSMENT (CRA)

### 2.1 OVERVIEW

Customer Risk Assessment (CRA) is a systematic methodology to evaluate the money laundering and terrorist financing risk posed by customers. The system calculates both inherent risk (raw risk before controls) and residual risk (risk after applying mitigations).

**Purpose:**

- Assign risk ratings to customers based on multiple risk factors
- Guide Enhanced Due Diligence (EDD) requirements
- Inform transaction monitoring thresholds
- Support regulatory compliance and reporting
- Enable risk-based resource allocation

**Scope:**

- Individual customers (natural persons)
- Legal entity customers (companies, trusts, partnerships)
- Related parties (directors, shareholders, UBOs)
- Periodic reassessment and continuous monitoring

### 2.2 RISK CALCULATION METHODOLOGY

#### 2.2.1 Inherent Risk Formula

Inherent risk is calculated using a weighted composite score across four risk components:

```
Inherent Risk Score = (Customer × 0.30) + (Geography × 0.20) + (Product × 0.30) + (Channel × 0.20)
```

**Component Weights:**

- Customer Component: 30%
- Geography Component: 20%
- Product Component: 30%
- Channel Component: 20%

**Result Range:** 1.0 to 3.0

**Risk Level Mapping:**

- **Low Risk:** 1.0 ≤ score < 1.7
- **Medium Risk:** 1.7 ≤ score < 2.4
- **High Risk:** 2.4 ≤ score ≤ 3.0

#### 2.2.2 Customer Component (30% weight)

The customer component evaluates characteristics specific to the customer entity.

**Sub-factors and Weights:**

| Sub-Factor          | Weight | Values                                      |
| ------------------- | ------ | ------------------------------------------- |
| Customer Type       | 15%    | Individual = 1, Legal Person = 3            |
| Residency Status    | 10%    | Resident = 1, Non-Resident = 3              |
| Country Risk        | 15%    | Low = 1, Medium = 2, High = 3               |
| Registration Type   | 10%    | Mainland = 1, Free Zone = 2, Offshore = 3   |
| Ownership Structure | 10%    | Transparent = 1, Opaque = 3                 |
| Business Sector     | 10%    | Low Risk = 1, Medium = 2, High Risk = 3     |
| PEP Exposure        | 30%    | None = 1, Domestic PEP = 2, Foreign PEP = 3 |

**Calculation:**

```
Customer Score = Σ(sub-factor_value × sub-factor_weight) / Σ(sub-factor_weights)
```

**PEP (Politically Exposed Person) Identification:**

- Direct PEP: Customer themselves is a PEP
- Associated PEP: Close associate of a PEP
- Related PEP: Family member of a PEP
- Higher risk for Foreign PEPs vs Domestic PEPs

**Business Sector Risk Classification:**

**High Risk Sectors (Score = 3):**

- Money services businesses
- Casinos and gaming
- Precious metals/stones dealers
- Real estate
- Legal/accounting services
- Virtual asset service providers (VASPs)

**Medium Risk Sectors (Score = 2):**

- Import/export trading
- Hospitality
- Jewelry retail
- Art dealers

**Low Risk Sectors (Score = 1):**

- Education
- Healthcare
- Manufacturing (non-sensitive)
- Retail (general)

#### 2.2.3 Geography Component (20% weight)

Evaluates risk based on jurisdictions associated with the customer.

**For Legal Entities:**

```
Geography Score = (Incorporation_Country × 0.50) + (Nationality × 0.30) + (UBO_Nationality × 0.20)
```

**For Individuals:**

```
Geography Score = (Nationality × 0.50) + (Residence_Country × 0.50)
```

**Country Risk Classification:**

- **High Risk (3):** FATF blacklist/greylist countries, sanctioned jurisdictions, high corruption index
- **Medium Risk (2):** Countries with moderate AML controls
- **Low Risk (1):** Countries with robust AML frameworks (e.g., FATF member states with strong compliance)

**Key Considerations:**

- Multiple nationalities: use highest risk score
- Multiple UBOs: average their nationality scores
- Incorporation vs operations jurisdiction mismatch = additional risk flag

#### 2.2.4 Product Component (30% weight)

Evaluates risk based on products and services utilized by the customer.

**Product Risk Scores:**

| Product/Service         | Risk Score | Rationale                   |
| ----------------------- | ---------- | --------------------------- |
| Savings Account         | 1.0        | Low liquidity, transparent  |
| Current Account         | 1.5        | Higher transaction velocity |
| International Transfers | 2.5        | Cross-border risk           |
| Cash Services           | 3.0        | Anonymity risk              |
| Cryptocurrency Services | 3.0        | High AML risk               |
| Trade Finance           | 2.0        | Complex transactions        |
| Loans/Credit            | 1.5        | Documented source of funds  |
| Investment Products     | 2.0        | Potential for layering      |

**Aggregation Methods:**

1. **Maximum Method (Default):**

   ```
   Product Score = max(product_scores)
   ```

   - Use highest risk product as overall score
   - Conservative approach

2. **Mean Method (Alternative):**

   ```
   Product Score = Σ(product_scores) / count(products)
   ```

   - Average across all products
   - Use when multiple low-risk products shouldn't be penalized

**Configuration:** Organization can choose aggregation method

#### 2.2.5 Channel Component (20% weight)

Evaluates risk based on customer onboarding and service delivery channels.

**Channel Risk Scores:**

| Channel             | Risk Score | Rationale                    |
| ------------------- | ---------- | ---------------------------- |
| In-Person Branch    | 1.0        | Face-to-face verification    |
| Video KYC           | 1.5        | Remote but verified identity |
| Online Self-Service | 2.5        | Non-face-to-face             |
| Third-Party Agent   | 2.5        | Indirect relationship        |
| Mobile App          | 2.0        | Device-based verification    |

**Calculation:**

```
Channel Score = max(channel_scores)
```

- Uses maximum score if multiple channels used
- Reflects highest risk exposure point

### 2.3 SCENARIO-BASED RISK OVERRIDES

Certain conditions automatically adjust risk levels regardless of calculated score.

#### 2.3.1 Blocking Scenarios (Auto-Decline)

These scenarios result in **immediate rejection** or **maximum risk score (3.0)**:

1. **Confirmed Sanctions Match**

   - Customer or UBO on sanctions list
   - Action: Block onboarding, close existing relationship

2. **FATF High-Risk Jurisdiction**

   - Customer from blacklisted country
   - Configurable: Block or Elevate to High

3. **Opaque Ownership (Legal Entities)**
   - Unable to identify UBOs
   - More than 3 ownership layers without transparency
   - Configurable: Block or Elevate to High

#### 2.3.2 High-Risk Elevation Scenarios

These scenarios elevate risk to **High (3.0)** regardless of calculated score:

1. **PEP Status**

   - Any PEP relationship (direct, associate, family)
   - Action: Elevate to High Risk + require EDD

2. **SAR/STR Filed**

   - Previous suspicious activity report filed for customer
   - Action: Elevate to High Risk + enhanced monitoring

3. **Law Enforcement Enquiry**

   - Active investigation or enquiry received
   - Action: Elevate to High Risk + case created

4. **Adverse Media (Confirmed)**

   - Credible negative media related to financial crime
   - Action: Elevate to High Risk + investigation

5. **High-Risk Jurisdiction**
   - Customer nexus with high-risk country
   - Configurable threshold

#### 2.3.3 Transaction-Based Scenarios

These scenarios trigger risk escalation based on transaction behavior:

1. **High-Value Cash/Crypto Transactions**

   - **Threshold:** Cumulative amount ≥ threshold within 30 days
   - **Default:** 10,000 currency units
   - **Action:** Elevate risk, trigger case review

2. **Exceeds Expected Transaction Volume**

   - **Threshold:** Actual volume > (Expected volume × multiplier)
   - **Default Multiplier:** 1.5x
   - **Action:** Elevate risk, investigate variance

3. **Third-Party Payment Pattern**

   - **Threshold:** Cumulative third-party payments ≥ threshold within 30 days
   - **Default:** 15,000 currency units
   - **Action:** Elevate risk, verify legitimacy

4. **High-Value International Wires**
   - **Threshold:** Cumulative international transfers ≥ threshold within 30 days
   - **Default:** 20,000 currency units
   - **Action:** Enhanced scrutiny

**Evaluation Period:** Scenarios evaluated on rolling 30-day basis

### 2.4 CONTROLS & MITIGATIONS

Controls reduce inherent risk to derive residual risk.

#### 2.4.1 Control Catalog

| Control                       | Risk Reduction | Description                                  |
| ----------------------------- | -------------- | -------------------------------------------- |
| Enhanced Due Diligence (EDD)  | 15%            | Comprehensive verification and documentation |
| Source of Wealth Verification | 10%            | Documentary evidence of wealth accumulation  |
| Source of Funds Verification  | 10%            | Specific transaction fund origin             |
| Adverse Media Screening       | 12%            | Systematic negative news monitoring          |
| UBO Verification              | 15%            | Identification of ultimate beneficial owners |
| Site Visit                    | 20%            | Physical verification of business premises   |
| Financial Statements Review   | 8%             | Analysis of audited financials               |
| Enhanced Monitoring           | 10%            | Increased transaction scrutiny               |

#### 2.4.2 Residual Risk Calculation

```
Total Control Effectiveness = Σ(applied_controls_risk_reduction)

IF Total Control Effectiveness ≥ Minimum Threshold (default 35%):
    Residual Risk = max(1.0, Inherent Risk - Max Reduction)
ELSE:
    Residual Risk = Inherent Risk
```

**Control Parameters:**

- **Maximum Total Reduction:** 70% (cannot reduce inherent score by more than 0.7)
- **Minimum for Downgrade:** 35% (must apply at least 35% controls to reduce risk)
- **Floor:** Residual risk cannot go below 1.0 (Low Risk minimum)

**Example:**

```
Inherent Risk = 2.8 (High)
Applied Controls: EDD (15%) + Source of Wealth (10%) + UBO Verification (15%) = 40%

40% ≥ 35% (meets threshold)
Reduction = min(0.40 × 2.8, 0.7) = min(1.12, 0.7) = 0.7
Residual Risk = max(1.0, 2.8 - 0.7) = 2.1 (Medium)
```

#### 2.4.3 Restrictions on Control Application

Certain scenarios prevent risk downgrade even with controls:

1. **Confirmed Sanctions:** Cannot downgrade
2. **Active SAR/STR:** Cannot downgrade below High
3. **Law Enforcement Investigation:** Cannot downgrade below High
4. **PEP Status:** Can downgrade from 3.0 to 2.4 (High minimum) only with full EDD

### 2.5 RISK REASSESSMENT

#### 2.5.1 Reassessment Triggers

**Periodic Reassessment:**

- **High Risk Customers:** Every 6 months
- **Medium Risk Customers:** Every 12 months
- **Low Risk Customers:** Every 24 months

**Event-Based Reassessment (Immediate):**

1. Material change in customer profile
   - Change in ownership structure
   - Change in business activity
   - Change in jurisdiction
2. Significant transaction variance from expected behavior
3. New sanctions screening match
4. PEP status change
5. Adverse media hit
6. Regulatory event (SAR/STR filing, investigation)
7. KYC document expiry
8. Customer request for risk review

#### 2.5.2 Reassessment Process

1. **Data Collection:** Gather current customer information
2. **Risk Calculation:** Re-run CRA algorithm with updated data
3. **Scenario Evaluation:** Check all override scenarios
4. **Controls Review:** Verify controls still valid and effective
5. **Comparison:** Compare new risk vs. previous risk
6. **Escalation:** If risk increases, trigger case for review
7. **Documentation:** Record reason for reassessment and outcome
8. **Notification:** Alert compliance team if risk level changes

### 2.6 DATA REQUIREMENTS

#### 2.6.1 Customer Data Inputs

**Natural Person:**

- Full legal name
- Date of birth
- Nationality (primary and secondary)
- Residence country
- Occupation/employment
- PEP status and relationship type
- Source of wealth
- Expected transaction volume
- Onboarding channel

**Legal Entity:**

- Legal name and trade name
- Incorporation country and date
- Registration type (mainland/free zone/offshore)
- Business sector/industry
- Ownership structure
- Ultimate beneficial owners (name, DOB, nationality, ownership %)
- Directors and authorized signatories
- Source of funds
- Expected transaction volume
- Products/services to be used
- Onboarding channel

#### 2.6.2 Related Parties

For each party (director, shareholder, UBO):

- Full name
- Date of birth
- Nationality
- Ownership percentage (if applicable)
- PEP status
- Sanctions screening result

**Minimum UBO Threshold:** 25% ownership or control

### 2.7 OUTPUT SPECIFICATIONS

#### 2.7.1 Risk Assessment Result

```
{
  customerId: string
  assessmentDate: datetime
  assessmentType: "initial" | "periodic" | "event_triggered"

  inherentRisk: {
    score: number (1.0 - 3.0)
    level: "low" | "medium" | "high"
    components: {
      customer: { score: number, weight: 0.30 }
      geography: { score: number, weight: 0.20 }
      product: { score: number, weight: 0.30 }
      channel: { score: number, weight: 0.20 }
    }
  }

  scenarios: [
    {
      scenarioId: string
      triggered: boolean
      action: "block" | "elevate_high" | "none"
      description: string
    }
  ]

  controls: [
    {
      controlId: string
      applied: boolean
      riskReduction: number (percentage)
      appliedDate: datetime
    }
  ]

  residualRisk: {
    score: number (1.0 - 3.0)
    level: "low" | "medium" | "high"
    controlEffectiveness: number (percentage)
  }

  finalRisk: {
    score: number (1.0 - 3.0)
    level: "low" | "medium" | "high"
    rationale: string
  }

  eddRequired: boolean
  nextReassessmentDate: datetime
  assessedBy: string
}
```

#### 2.7.2 Risk Level Actions

| Risk Level | Actions Required                                                                                                                                            |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Low**    | - Standard due diligence<br>- Regular monitoring<br>- Reassess every 24 months                                                                              |
| **Medium** | - Enhanced due diligence recommended<br>- Increased monitoring<br>- Reassess every 12 months                                                                |
| **High**   | - Enhanced due diligence mandatory<br>- Senior management approval<br>- Continuous monitoring<br>- Reassess every 6 months<br>- Higher transaction scrutiny |

### 2.8 CONFIGURATION PARAMETERS

#### 2.8.1 Configurable Elements

**Component Weights:**

- Customer component weight (default: 0.30)
- Geography component weight (default: 0.20)
- Product component weight (default: 0.30)
- Channel component weight (default: 0.20)

**Risk Thresholds:**

- Low-Medium threshold (default: 1.7)
- Medium-High threshold (default: 2.4)

**Scenario Settings:**

- Enable/disable each scenario
- Action per scenario (block, elevate_high, monitor)
- Transaction thresholds for transaction-based scenarios
- Time periods for cumulative calculations

**Control Settings:**

- Risk reduction percentage per control
- Maximum total reduction (default: 70%)
- Minimum threshold for downgrade (default: 35%)

**Reassessment Intervals:**

- High risk interval (default: 6 months)
- Medium risk interval (default: 12 months)
- Low risk interval (default: 24 months)

**Product Risk Scores:**

- Customizable catalog of products with risk scores
- Aggregation method (max or mean)

**Channel Risk Scores:**

- Customizable catalog of channels with risk scores

**Jurisdiction Risk:**

- Country risk classifications (low/medium/high)
- Custom high-risk jurisdiction list

#### 2.8.2 Organization-Level Overrides

Organizations can override default configuration at multiple levels:

- Global organization settings
- Customer segment-specific settings
- Product-specific settings

### 2.9 BUSINESS RULES

#### 2.9.1 Validation Rules

1. All mandatory customer data must be present before CRA calculation
2. For legal entities, at least one UBO must be identified (≥25% ownership)
3. Country codes must be valid ISO 3166-1 alpha-3 format
4. Risk scores must be between 1.0 and 3.0 (inclusive)
5. Component weights must sum to 1.0
6. At least one product must be selected
7. At least one channel must be selected
8. PEP relationships must have substantiation/evidence

#### 2.9.2 Exception Handling

**Missing Data:**

- Use conservative defaults (higher risk)
- Flag for data quality review
- Require manual review before finalization

**Conflicting Scenarios:**

- Block takes precedence over Elevate
- Most restrictive action applies
- Document all triggered scenarios

**Edge Cases:**

- Stateless persons: Use residence country for nationality risk
- Multiple jurisdictions: Use highest risk jurisdiction
- Complex ownership: Require manual UBO determination if automated calculation inconclusive

### 2.10 AUDIT & COMPLIANCE

#### 2.10.1 Audit Trail Requirements

Every CRA calculation must log:

- Timestamp of assessment
- User/system initiating assessment
- All input data used (snapshot)
- Calculated scores for each component
- Triggered scenarios
- Applied controls
- Final risk determination
- Any manual overrides with justification
- Approval chain (if required)

**Retention:** Minimum 7 years

#### 2.10.2 Approval Workflow

**High Risk Onboarding:**

- Requires senior compliance officer approval
- Must document rationale for acceptance
- Board notification if above certain threshold (configurable)

**Risk Downgrades:**

- Requires approval if risk reduced by more than one level
- Must document justification and controls applied

**Manual Overrides:**

- Must have documented business justification
- Requires dual approval (maker-checker)
- Subject to periodic review

#### 2.10.3 Reporting

**Management Reports:**

- Risk distribution (low/medium/high) across customer base
- Risk trends over time
- High-risk customer portfolio composition
- Scenario trigger frequency
- Control effectiveness analysis
- Reassessment compliance (on-time vs overdue)

**Regulatory Reports:**

- Risk assessment methodology documentation
- High-risk customer statistics
- EDD completion rates
- Risk-based approach validation

### 2.11 PERFORMANCE REQUIREMENTS

- **Calculation Time:** < 2 seconds per customer assessment
- **Bulk Reassessment:** Support 100+ customers per batch
- **Concurrent Assessments:** Support 50+ simultaneous calculations
- **Historical Data Access:** Query 7+ years of historical risk assessments
- **Report Generation:** < 10 seconds for standard risk reports

---

## 3. SANCTIONS SCREENING

### 3.1 OVERVIEW

Sanctions screening identifies customers, related parties, and transactions that match sanctioned individuals, entities, or jurisdictions. The system screens against multiple international sanctions lists and PEP (Politically Exposed Persons) databases.

**Purpose:**

- Prevent business relationships with sanctioned entities
- Identify PEPs requiring enhanced due diligence
- Comply with international sanctions regulations (OFAC, UN, EU, UK)
- Mitigate financial crime and reputational risk

**Scope:**

- Customer screening (individuals and legal entities)
- Related party screening (directors, shareholders, UBOs)
- Transaction party screening (beneficiaries, senders)
- Ongoing monitoring (periodic rescreening)

### 3.2 SCREENING DATASETS

#### 3.2.1 Sanctions Lists

**International Sanctions:**

- **OFAC SDN** (US Office of Foreign Assets Control - Specially Designated Nationals)
- **UN Security Council** Consolidated List
- **EU Sanctions** List
- **UK HMT** (Her Majesty's Treasury) Sanctions
- **DFAT** (Australian Department of Foreign Affairs and Trade)
- **National Sanctions** (country-specific lists)

**Sanctions Types:**

- Asset freeze
- Travel ban
- Arms embargo
- Trade restrictions
- Financial transaction prohibitions

#### 3.2.2 PEP Databases

**PEP Categories:**

- **Senior Political Figures** - Heads of state, senior government officials
- **Immediate Family Members** - Spouses, children, parents
- **Close Associates** - Business partners, known associates
- **International Organization Leaders** - UN, World Bank, IMF officials

**PEP Classifications:**

- **Foreign PEP** - Political figure from another country (highest risk)
- **Domestic PEP** - Political figure from home country (medium risk)
- **International Organization PEP** - Officials of international bodies

**PEP Status Duration:**

- Active PEPs: Currently in position
- Former PEPs: Retain status for configurable period (default: 12 months post-exit)

#### 3.2.3 Watch Lists

**Additional Sources:**

- **Adverse Media** - Individuals linked to financial crime in credible sources
- **Internal Watch List** - Organization-specific high-risk entities
- **Law Enforcement Databases** - Interpol, national crime agencies (where available)
- **Disqualified Directors** - Barred from company management

### 3.3 SCREENING METHODOLOGY

#### 3.3.1 Subject Types

**Screening Subjects:**

- **Natural Person** - Individual customer or related party
- **Organization** - Legal entity (company, trust, foundation)
- **Vessel** - Ships/aircraft (for trade finance)
- **Address** - Geographic location screening

#### 3.3.2 Matching Algorithm

The system uses multi-stage matching with confidence scoring:

**Stage 1: Exact Match**

```
IF subject_name == entity_name THEN confidence = 1.0
```

**Stage 2: Alias Match**

```
IF subject_name IN entity_aliases THEN confidence = 0.9
```

**Stage 3: Fuzzy Matching**
Uses string similarity algorithms (Levenshtein distance, Jaro-Winkler):

```
similarity_score = calculate_string_similarity(subject_name, entity_name)
IF similarity_score >= threshold THEN match_candidate
```

**Default Fuzzy Threshold:** 0.6 (60% similarity)

**Stage 4: Word-Level Matching**

```
subject_words = tokenize(subject_name)
entity_words = tokenize(entity_name)
overlap = count(common_words) / max(count(subject_words), count(entity_words))
```

#### 3.3.3 Enhanced Scoring

Base match score is enhanced using additional factors:

```
Final Score = Base Score + Date_of_Birth_Bonus + Nationality_Bonus + Document_Bonus

Where:
- Base Score: from name matching (0.0 - 1.0)
- Date_of_Birth_Bonus: +0.06 if DOB matches
- Nationality_Bonus: +0.03 if nationality matches
- Document_Bonus: +0.02 if ID number matches
```

**Match Quality Indicators:**

| Match Type   | Base Score | Enhanced Score Range |
| ------------ | ---------- | -------------------- |
| Exact Name   | 1.0        | 1.0 - 1.11           |
| Alias        | 0.9        | 0.9 - 1.01           |
| Strong Fuzzy | 0.7-0.89   | 0.7 - 1.0            |
| Weak Fuzzy   | 0.6-0.69   | 0.6 - 0.8            |

**Note:** Scores can exceed 1.0 due to enhancement factors

#### 3.3.4 Match Detail Classification

**Name Match Quality:**

- `exact` - Perfect name match
- `alias` - Matches known alias
- `partial` - Significant word overlap (>60%)
- `fuzzy` - String similarity above threshold
- `none` - No name match

**Date of Birth Match:**

- `match` - DOB exactly matches
- `mismatch` - Different DOB
- `unknown` - DOB not available for comparison

**Nationality Match:**

- `match` - Nationality matches
- `mismatch` - Different nationality
- `unknown` - Nationality not available

### 3.4 SCREENING PROCESS

#### 3.4.1 Screening Workflow

1. **Subject Preparation**

   - Normalize name (remove special characters, standardize spacing)
   - Extract matching attributes (DOB, nationality, ID numbers)
   - Determine entity type (person/organization)

2. **Dataset Selection**

   - Select applicable datasets based on screening type
   - For sanctions: all sanctions lists
   - For PEP: PEP databases only
   - For comprehensive: sanctions + PEP + watch lists

3. **Query Execution**

   - Submit subject to screening provider API
   - Apply fuzzy threshold
   - Retrieve potential matches

4. **Match Evaluation**

   - Calculate enhanced scores for each match
   - Filter matches below threshold
   - Classify match details (name, DOB, nationality)
   - Rank matches by confidence score

5. **Result Recording**

   - Store screening event with timestamp
   - Record all match candidates
   - Log screening parameters (datasets, thresholds, algorithm)
   - Capture raw provider response

6. **Decision Support**
   - Present matches to analyst
   - Provide match details and source information
   - Enable true positive/false positive determination

#### 3.4.2 Multi-Layer Screening

For legal entities, screen multiple layers:

**Layer 1: Entity Screening**

- Screen legal entity name
- Screen trade names and aliases

**Layer 2: Directors and Authorized Signatories**

- Screen all directors individually
- Screen authorized signatories

**Layer 3: Shareholders**

- Screen all shareholders above threshold (default 10%)

**Layer 4: Ultimate Beneficial Owners (UBOs)**

- Screen all UBOs (≥25% ownership or control)

**Aggregation:**

```
Overall Result = {
  entity_match: highest_score_from_entity
  director_matches: [highest_score_per_director]
  shareholder_matches: [highest_score_per_shareholder]
  ubo_matches: [highest_score_per_ubo]
  highest_overall_score: max(all_scores)
  has_match: any_score >= threshold
}
```

### 3.5 SCREENING THRESHOLDS

#### 3.5.1 Configurable Thresholds

**Sanctions Screening Threshold:**

- **Default:** 0.6 (60% match confidence)
- **Range:** 0.4 - 0.9
- **Recommendation:** 0.6 balances false positives vs false negatives

**PEP Screening Threshold:**

- **Default:** 0.6 (60% match confidence)
- **Range:** 0.5 - 0.8
- **Recommendation:** Same as sanctions for consistency

#### 3.5.2 Risk-Based Thresholds

Adjust thresholds based on context:

| Context                | Sanctions Threshold | PEP Threshold | Rationale                           |
| ---------------------- | ------------------- | ------------- | ----------------------------------- |
| Customer Onboarding    | 0.6                 | 0.6           | Standard                            |
| High-Value Transaction | 0.5                 | 0.5           | Lower threshold for higher scrutiny |
| Periodic Rescreening   | 0.7                 | 0.7           | Reduce false positives              |
| High-Risk Jurisdiction | 0.5                 | 0.5           | Enhanced screening                  |

### 3.6 SCREENING TRIGGERS

#### 3.6.1 Initial Screening

**Onboarding:**

- New customer application
- New related party added (director, UBO, etc.)
- Account reactivation after dormancy

**Action:** Mandatory before relationship establishment

#### 3.6.2 Ongoing Screening

**Periodic Rescreening:**

- **High Risk Customers:** Every 3 months
- **Medium Risk Customers:** Every 6 months
- **Low Risk Customers:** Every 12 months

**Event-Based Rescreening:**

- Customer data change (name, nationality, DOB)
- Sanctions list update (new entities added)
- PEP database refresh
- Risk level change
- Transaction to high-risk jurisdiction
- Material change in business activity

#### 3.6.3 Transaction Screening

**Real-Time Transaction Screening:**

- Beneficiary name screening before payment execution
- Sender screening for incoming payments
- Screening of related parties in trade finance

**Threshold-Based:**

- All transactions > configurable amount (default: 10,000)
- All international wire transfers
- All transactions to/from high-risk jurisdictions

### 3.7 MATCH RESOLUTION

#### 3.7.1 True Positive Determination

**Factors to Consider:**

- Name similarity strength
- Date of birth match
- Nationality/jurisdiction match
- Aliases and known associates
- Address information
- Identification documents
- Context and relationship

**Resolution Process:**

1. Analyst reviews match details
2. Requests additional information from customer (if needed)
3. Consults source documents (OFAC website, UN list, etc.)
4. Makes determination: True Positive or False Positive
5. Documents rationale
6. Escalates if uncertain

#### 3.7.2 True Positive Actions

**Confirmed Sanctions Match:**

- **Immediate:** Block transaction/relationship
- **Existing Customer:** Freeze account, file SAR, notify authorities
- **Onboarding:** Decline application immediately
- **Case Creation:** Automatic case with "sanctions_match" trigger
- **Senior Management:** Immediate notification

**Confirmed PEP Match:**

- **Action:** Elevate to high risk, require EDD
- **Approval:** Senior compliance officer approval required
- **Enhanced Monitoring:** Ongoing transaction scrutiny
- **Case Creation:** Automatic case with "pep" trigger
- **Documentation:** Source of wealth/funds verification

#### 3.7.3 False Positive Actions

- Mark match as false positive with rationale
- Record analyst decision
- Update internal watch list if frequent false positive
- Consider adding to "cleared names" list
- No further action required
- Retain audit trail of decision

### 3.8 DATA REQUIREMENTS

#### 3.8.1 Input Specifications

**Natural Person Screening:**

```
{
  entity_type: "person"
  name: string (required)
  date_of_birth: date (optional but recommended)
  nationality: string[] (optional)
  id_number: string (optional)
  address: {
    country: string
    city: string
    full_address: string
  } (optional)
}
```

**Organization Screening:**

```
{
  entity_type: "organization"
  name: string (required)
  aliases: string[] (optional)
  incorporation_country: string (optional)
  registration_number: string (optional)
  address: {
    country: string
    city: string
    full_address: string
  } (optional)
}
```

#### 3.8.2 Provider Requirements

**API Integration:**

- RESTful API or SOAP interface
- JSON or XML response format
- Authentication (API key, OAuth)
- Rate limiting compliance
- Timeout handling (max 10 seconds)

**Data Quality:**

- UTF-8 encoding support
- Normalization of special characters
- Case-insensitive matching
- Support for non-Latin scripts (Arabic, Cyrillic, Chinese)

### 3.9 OUTPUT SPECIFICATIONS

#### 3.9.1 Screening Result Structure

```
{
  screening_id: string (unique identifier)
  screening_date: datetime
  subject: {
    type: "customer" | "party" | "transaction_party"
    entity_type: "person" | "organization"
    id: string
    name: string
    date_of_birth: date
    nationality: string[]
  }

  parameters: {
    datasets: string[] (e.g., ["ofac_sdn", "un_consolidated", "eu_sanctions"])
    topics: string[] (e.g., ["sanction", "role.pep"])
    algorithm: string (e.g., "logic-v1", "fuzzy-v2")
    threshold: number (e.g., 0.6)
  }

  matches: [
    {
      match_id: string
      entity_name: string
      aliases: string[]
      score: number (0.0 - 1.0+)

      match_details: {
        name_match: "exact" | "alias" | "partial" | "fuzzy" | "none"
        dob_match: "match" | "mismatch" | "unknown"
        nationality_match: "match" | "mismatch" | "unknown"
      }

      entity_data: {
        entity_type: "person" | "organization"
        date_of_birth: date[]
        nationalities: string[]
        addresses: string[]
        sanctions_lists: string[] (e.g., ["OFAC SDN", "UN"])
        pep_positions: string[]
        sanctions_reasons: string[]
      }

      sources: string[] (e.g., ["us_ofac_sdn", "un_sc_consolidated"])

      analyst_decision: "pending" | "true_positive" | "false_positive"
      decision_rationale: string
      decided_by: string
      decided_at: datetime
    }
  ]

  summary: {
    total_matches: number
    highest_score: number
    has_sanctions_match: boolean
    has_pep_match: boolean
    requires_review: boolean
  }

  provider: string (e.g., "opensanctions", "dow_jones", "refinitiv")
  raw_response: object (original provider response)
}
```

#### 3.9.2 Match Categorization

**By List Type:**

- Sanctions matches (requires_action = true)
- PEP matches (requires_edd = true)
- Watch list matches (requires_investigation = true)
- Adverse media (requires_validation = true)

**By Score Range:**

- **High Confidence (≥0.85):** Likely true positive, immediate review
- **Medium Confidence (0.7-0.84):** Possible match, standard review
- **Low Confidence (threshold-0.69):** Weak match, lower priority review

### 3.10 SCREENING HISTORY

#### 3.10.1 Record Retention

**Screening Events:**

- Store all screening events permanently
- Record parameters, results, and decisions
- Link to customer/party/transaction
- Maintain version history of sanctions lists

**Audit Trail:**

- Who initiated screening
- When screening occurred
- What datasets were used
- What matches were found
- How matches were resolved
- When resolution occurred
- Who made the decision

#### 3.10.2 Historical Analysis

**Capabilities:**

- View all screenings for a customer
- Track screening result changes over time
- Identify when a customer became sanctioned
- Analyze false positive rates by analyst
- Review decision quality

### 3.11 CONFIGURATION

#### 3.11.1 Dataset Configuration

**Dataset Selection:**

```
{
  sanctions_datasets: [
    "us_ofac_sdn",
    "un_sc_consolidated",
    "eu_sanctions",
    "uk_hmt_sanctions"
  ]

  pep_datasets: [
    "opensanctions_peps",
    "worldbank_debarred"
  ]

  watchlist_datasets: [
    "internal_watchlist",
    "adverse_media"
  ]
}
```

**Dataset Priorities:**

- OFAC: Critical (block immediately)
- UN: Critical (block immediately)
- EU: High (block in EU jurisdictions)
- PEP: Medium (require EDD)

#### 3.11.2 Rescreening Configuration

**Frequency by Risk Level:**

```
{
  high_risk: {
    frequency_days: 90,
    auto_trigger: true
  },
  medium_risk: {
    frequency_days: 180,
    auto_trigger: true
  },
  low_risk: {
    frequency_days: 365,
    auto_trigger: true
  }
}
```

**List Update Triggers:**

- Automatic rescreening when sanctions lists updated
- Configurable delay (default: 24 hours after list update)
- Batch processing to avoid system overload

### 3.12 CASE INTEGRATION

#### 3.12.1 Automatic Case Creation

**Sanctions Match:**

```
IF match.score >= sanctions_threshold AND match.source IN sanctions_lists THEN
  CREATE CASE {
    trigger: "sanctions_match"
    priority: "critical"
    status: "investigating"
    customer_id: subject.id
    alerts: [screening_match]
  }
```

**PEP Match:**

```
IF match.score >= pep_threshold AND match.pep_positions NOT EMPTY THEN
  CREATE CASE {
    trigger: "pep"
    priority: "high"
    status: "investigating"
    customer_id: subject.id
    alerts: [pep_match]
  }
```

#### 3.12.2 Case Workflow

1. **Detection:** Screening identifies match above threshold
2. **Case Creation:** System creates case automatically
3. **Assignment:** Route to sanctions/PEP specialist
4. **Investigation:** Analyst reviews match, gathers information
5. **Decision:** True positive or false positive determination
6. **Action:** Block, require EDD, or clear
7. **Documentation:** Record decision and rationale
8. **Closure:** Close case with outcome

### 3.13 REGULATORY COMPLIANCE

#### 3.13.1 Sanctions Compliance

**OFAC Requirements (US):**

- Screen against SDN list
- 50% rule for ownership (screen entities owned 50%+ by sanctioned persons)
- Real-time screening before transaction execution
- Blocking of sanctioned assets
- OFAC reporting within 10 days

**UN Sanctions:**

- Implement UN Security Council sanctions
- Report to national authorities
- Asset freeze compliance

**EU Sanctions:**

- Screen against EU consolidated list
- Report to competent authorities
- No transactions with listed persons/entities

#### 3.13.2 PEP Compliance

**FATF Recommendations:**

- Risk-based approach to PEPs
- Enhanced due diligence for PEPs
- Senior management approval for PEP relationships
- Source of wealth and funds determination
- Enhanced ongoing monitoring

**Regional Requirements:**

- UAE: PEP screening mandatory per CBUAE regulations
- UK: FCA requires PEP identification
- EU: 5AMLD mandates PEP screening

### 3.14 PERFORMANCE REQUIREMENTS

- **Screening Time:** < 5 seconds per subject
- **Multi-Layer Screening:** < 15 seconds for entity with 10 related parties
- **Batch Screening:** 100+ subjects per minute
- **Concurrent Screening:** 50+ simultaneous screening requests
- **List Update Processing:** < 1 hour to update and rescreen active customers
- **API Availability:** 99.5% uptime
- **Timeout Handling:** Graceful degradation if provider unavailable

### 3.15 ERROR HANDLING

**Provider Unavailable:**

- Retry logic (3 attempts with exponential backoff)
- Fall back to cached list if real-time unavailable
- Queue for later processing
- Alert compliance team

**Ambiguous Results:**

- Flag for manual review
- Apply conservative approach (treat as potential match)
- Escalate to senior analyst

**Data Quality Issues:**

- Normalize input data (remove special characters, standardize)
- Handle missing data gracefully
- Use available fields for matching
- Document data quality limitations

---

## 4. TRANSACTION MONITORING

### 4.1 OVERVIEW

Transaction monitoring is a real-time system that analyzes transaction patterns and behaviors to detect potential money laundering, terrorist financing, and other financial crimes. The system applies rule-based scenarios to identify suspicious activities.

**Purpose:**

- Detect unusual transaction patterns and behaviors
- Identify structuring, layering, and integration activities
- Support SAR/STR filing requirements
- Enable risk-based transaction scrutiny
- Comply with regulatory monitoring obligations

**Scope:**

- All customer transactions (deposits, withdrawals, transfers)
- Domestic and international payments
- Cash transactions
- Cryptocurrency transactions
- Third-party payments
- High-value transactions

### 4.2 MONITORING SCENARIOS

#### 4.2.1 Scenario 1: High-Value Single Transaction

Detects individual transactions exceeding a monetary threshold.

**Rule Logic:**

```
IF transaction.amount >= threshold THEN
  TRIGGER ALERT
```

**Configuration:**

- **Default Threshold:** 50,000 (currency units)
- **Adjustable by:** Customer risk level, jurisdiction, product type

**Risk Scoring:**

```
risk_delta = base_risk + (occurrence_multiplier × count)
base_risk = 15
occurrence_multiplier = 5
max_risk_delta = 40

risk_delta = min(15 + (5 × trigger_count), 40)
```

**Example:**

```
Transaction: 75,000
Threshold: 50,000
Result: Alert triggered
Risk Delta: 15 (first occurrence)

If triggered 5 times in period:
Risk Delta: min(15 + (5 × 5), 40) = min(40, 40) = 40
```

**Adjustments:**

- High-risk customers: Lower threshold by 30%
- Low-risk customers: Increase threshold by 50%
- High-risk jurisdictions: Lower threshold by 40%

#### 4.2.2 Scenario 2: High-Value Cumulative Transactions

Detects cumulative transaction volume exceeding threshold within a time period.

**Rule Logic:**

```
cumulative_amount = SUM(transactions) within period
IF cumulative_amount >= threshold THEN
  TRIGGER ALERT
```

**Configuration:**

- **Default Threshold:** 100,000 (monthly)
- **Periods:** Daily, Weekly, Monthly
- **Rolling Window:** Yes (continuous evaluation)

**Risk Scoring:**

```
risk_delta = 15 + (5 × trigger_count)
max_risk_delta = 35
```

**Time Periods:**
| Period | Default Threshold | Typical Use Case |
|--------|------------------|------------------|
| Daily | 30,000 | Rapid accumulation detection |
| Weekly | 75,000 | Short-term pattern detection |
| Monthly | 100,000 | Standard monitoring period |

**Exclusions:**

- Pre-approved large transactions (with documentation)
- Transactions matching expected volume profile
- Intra-account transfers (configurable)

#### 4.2.3 Scenario 3: Dormant Account Reactivation

Detects accounts with prolonged inactivity followed by high-value transactions.

**Rule Logic:**

```
inactivity_period = current_date - last_transaction_date
IF inactivity_period >= dormancy_threshold
   AND transaction.amount >= amount_threshold THEN
  TRIGGER ALERT
```

**Configuration:**

- **Dormancy Threshold:** 90 days (default)
- **Amount Threshold:** 10,000 (default)

**Risk Scoring:**

```
risk_delta = 30 (fixed, high risk)
```

**Rationale:**
Dormant accounts reactivated with large transactions may indicate account takeover or use for money laundering.

**Enhanced Detection:**

```
severity = "critical" IF inactivity > 365 days AND amount > 50,000
severity = "high" IF inactivity > 180 days
severity = "medium" IF inactivity > 90 days
```

#### 4.2.4 Scenario 4: High-Risk Jurisdiction Transaction

Detects transactions to or from high-risk jurisdictions.

**Rule Logic:**

```
IF (transaction.destination_country IN high_risk_countries
    OR transaction.origin_country IN high_risk_countries)
   AND transaction.amount >= threshold THEN
  TRIGGER ALERT
```

**Configuration:**

- **Default Threshold:** 5,000
- **High-Risk Countries:** FATF blacklist/greylist, sanctioned countries
- **Direction:** Inbound, outbound, or both

**Risk Scoring:**

```
risk_delta = 15 + (5 × trigger_count)
max_risk_delta = 35
```

**High-Risk Jurisdiction Categories:**

- FATF blacklist (highest risk)
- FATF greylist (enhanced monitoring)
- Sanctioned countries
- High corruption index countries
- Non-cooperative tax jurisdictions

**Exemptions:**

- Established trade relationships with documentation
- Remittances to family in home country (with proof)
- Business operations in jurisdiction (with justification)

#### 4.2.5 Scenario 5: High-Risk Payment Channel

Detects use of high-risk payment methods exceeding thresholds.

**High-Risk Channels:**

- Cryptocurrency transactions
- International wire transfers
- Cash deposits/withdrawals
- Prepaid cards
- Money service businesses

**Rule Logic:**

```
IF transaction.payment_channel IN high_risk_channels
   AND transaction.amount >= channel_threshold THEN
  TRIGGER ALERT
```

**Configuration:**
| Channel | Default Threshold | Risk Multiplier |
|---------|------------------|-----------------|
| Cryptocurrency | 5,000 | 3.0 |
| International Wire | 20,000 | 2.0 |
| Cash | 10,000 | 2.5 |
| MSB | 15,000 | 2.0 |

**Risk Scoring:**

```
base_risk = 10
volume_multiplier = transaction.amount / threshold
risk_delta = min(base_risk + (2 × volume_multiplier), 30)
```

#### 4.2.6 Scenario 6: New Customer High-Value Activity

Detects high-value transactions from recently onboarded customers.

**Rule Logic:**

```
customer_tenure = current_date - customer.onboarding_date
IF customer_tenure < tenure_threshold
   AND transaction.amount >= amount_threshold THEN
  TRIGGER ALERT
```

**Configuration:**

- **Tenure Threshold:** 6 months (default)
- **Amount Threshold:** 25,000 (default)

**Risk Scoring:**

```
risk_delta = 15 + (5 × trigger_count)
max_risk_delta = 35
```

**Rationale:**
New customers conducting large transactions may indicate account opening for specific money laundering purpose.

**Tenure-Based Thresholds:**
| Customer Tenure | Amount Threshold | Risk Level |
|-----------------|------------------|------------|
| < 1 month | 10,000 | Critical |
| 1-3 months | 20,000 | High |
| 3-6 months | 25,000 | Medium |
| > 6 months | Standard threshold | Standard |

#### 4.2.7 Scenario 7: Third-Party Payment Pattern

Detects frequent or high-value payments to/from third parties.

**Rule Logic:**

```
IF transaction.is_third_party_payment == true
   AND (
     transaction.amount >= single_threshold
     OR cumulative_third_party_amount >= cumulative_threshold
   ) THEN
  TRIGGER ALERT
```

**Configuration:**

- **Single Transaction Threshold:** 15,000
- **Cumulative Threshold:** 30,000 (within 30 days)

**Third-Party Indicators:**

- Payment from account not in customer's name
- Payment to beneficiary unrelated to customer
- Multiple payments to different third parties
- Circular payment patterns

**Risk Scoring:**

```
risk_delta = 20 + (5 × trigger_count / 2)
max_risk_delta = 40
```

#### 4.2.8 Scenario 8: Structuring/Smurfing

Detects multiple transactions below reporting threshold designed to avoid detection.

**Rule Logic:**

```
reporting_threshold = 10,000 (or regulatory threshold)
just_below_threshold = reporting_threshold × 0.9

transactions_below_threshold = COUNT(transactions WHERE
  amount >= just_below_threshold AND
  amount < reporting_threshold
) within period

IF transactions_below_threshold >= frequency_threshold THEN
  TRIGGER ALERT
```

**Configuration:**

- **Reporting Threshold:** 10,000 (configurable by jurisdiction)
- **Just Below Range:** 90% of threshold (9,000-9,999)
- **Frequency:** 3+ transactions within 7 days
- **Period:** Rolling 7-day window

**Risk Scoring:**

```
risk_delta = 35 (high fixed risk - clear structuring indicator)
```

**Enhanced Detection Patterns:**

- Multiple transactions on same day
- Transactions across multiple branches/channels
- Round amounts just below threshold
- Regular timing patterns

#### 4.2.9 Scenario 9: Velocity/Frequency Anomaly

Detects unusual transaction frequency compared to customer's normal behavior.

**Rule Logic:**

```
normal_frequency = AVG(transaction_count_per_period) over baseline_period
current_frequency = transaction_count_current_period

IF current_frequency > (normal_frequency × multiplier) THEN
  TRIGGER ALERT
```

**Configuration:**

- **Baseline Period:** 90 days
- **Evaluation Period:** 7 days
- **Multiplier:** 3x (300% increase)

**Risk Scoring:**

```
velocity_ratio = current_frequency / normal_frequency
risk_delta = min(10 + (5 × velocity_ratio), 30)
```

**Example:**

```
Normal: 5 transactions per week
Current week: 18 transactions
Ratio: 18/5 = 3.6x
Trigger: Yes (exceeds 3x threshold)
Risk Delta: min(10 + (5 × 3.6), 30) = min(28, 30) = 28
```

#### 4.2.10 Scenario 10: Round Amount Pattern

Detects suspicious patterns of round-number transactions.

**Rule Logic:**

```
round_amounts = [10000, 20000, 50000, 100000, etc.]
round_transaction_count = COUNT(transactions WHERE
  amount IN round_amounts OR amount % 10000 == 0
) within period

IF round_transaction_count >= threshold THEN
  TRIGGER ALERT
```

**Configuration:**

- **Period:** 30 days
- **Threshold:** 5 round-amount transactions
- **Round Amounts:** Multiples of 10,000

**Risk Scoring:**

```
risk_delta = 15
```

**Rationale:**
Unusual frequency of round amounts may indicate pre-planned money laundering or placement activity.

#### 4.2.11 Scenario 11: Rapid In-Out (Layering)

Detects funds deposited and quickly withdrawn, indicating layering.

**Rule Logic:**

```
FOR EACH deposit:
  withdrawal_window = deposit.date + window_hours
  matching_withdrawals = SUM(withdrawals) within withdrawal_window

  IF matching_withdrawals >= (deposit.amount × percentage_threshold) THEN
    TRIGGER ALERT
```

**Configuration:**

- **Time Window:** 24-72 hours
- **Percentage Threshold:** 80% of deposit amount
- **Minimum Amount:** 15,000

**Risk Scoring:**

```
risk_delta = 25 (high risk - classic layering)
```

**Patterns:**

- Deposit → immediate withdrawal
- Deposit → transfer to multiple accounts → withdrawal
- Multiple deposits → consolidated withdrawal

#### 4.2.12 Scenario 12: Expected vs Actual Volume Variance

Detects transactions significantly exceeding expected customer profile.

**Rule Logic:**

```
expected_volume = customer.expected_monthly_volume
actual_volume = SUM(transactions.amount) within current_month

variance_ratio = actual_volume / expected_volume

IF variance_ratio > threshold THEN
  TRIGGER ALERT
```

**Configuration:**

- **Threshold:** 1.5x (150% of expected)
- **Period:** Monthly
- **Minimum Variance:** 10,000 absolute difference

**Risk Scoring:**

```
risk_delta = 15 + (5 × (variance_ratio - 1))
max_risk_delta = 35
```

**Example:**

```
Expected: 50,000/month
Actual: 120,000/month
Ratio: 2.4x
Trigger: Yes
Risk Delta: 15 + (5 × 1.4) = 22
```

### 4.3 ALERT GENERATION

#### 4.3.1 Alert Creation Logic

```
FOR EACH transaction:
  triggered_scenarios = []

  FOR EACH enabled_scenario:
    IF scenario.evaluate(transaction, customer) == TRUE THEN
      triggered_scenarios.append(scenario)

  IF triggered_scenarios.length > 0 THEN
    CREATE ALERT {
      transaction_id: transaction.id
      customer_id: transaction.customer_id
      scenarios: triggered_scenarios
      severity: calculate_severity(triggered_scenarios)
      risk_score: calculate_risk_score(triggered_scenarios)
      timestamp: current_time
    }
```

#### 4.3.2 Alert Severity Calculation

```
severity = determine_severity(risk_score, customer_risk_level)

Base Thresholds:
- Critical: risk_score >= 30
- High: risk_score >= 20
- Medium: risk_score >= 10
- Low: risk_score < 10

Adjusted by Customer Risk:
IF customer.risk_level == "high":
  thresholds = thresholds × 0.7 (lower thresholds)
IF customer.risk_level == "low":
  thresholds = thresholds × 1.3 (higher thresholds)
```

#### 4.3.3 Alert Aggregation

**Deduplication:**

- Same scenario triggered multiple times: Aggregate into single alert
- Update trigger count and risk score
- Track individual transactions in alert details

**Related Alerts:**

- Link alerts for same customer within time window
- Identify patterns across multiple scenarios
- Escalate if multiple high-severity alerts

### 4.4 RISK SCORING

#### 4.4.1 Transaction Risk Score Calculation

```
transaction_risk_score = base_score + Σ(scenario_risk_deltas)

Where:
- base_score = customer.risk_level_score (1.0, 2.0, or 3.0)
- scenario_risk_deltas = sum of all triggered scenario risk impacts
```

**Risk Level Mapping:**

```
IF transaction_risk_score < medium_threshold:
  transaction_risk_level = "low"
ELIF transaction_risk_score < high_threshold:
  transaction_risk_level = "medium"
ELSE:
  transaction_risk_level = "high"
```

**Dynamic Thresholds by Customer Risk:**
| Customer Risk | Medium Threshold | High Threshold | Critical Threshold |
|---------------|------------------|----------------|-------------------|
| Low | 15 | 30 | 50 |
| Medium | 12 | 25 | 40 |
| High | 10 | 20 | 30 |

#### 4.4.2 Scenario Weighting

**Scenario Priority:**

- **Critical (3.0x):** Structuring, Layering, Sanctions-related
- **High (2.0x):** Dormant account, Third-party payments
- **Medium (1.5x):** High-risk jurisdiction, Channel risk
- **Standard (1.0x):** Volume variance, Velocity

```
weighted_risk = scenario.base_risk × scenario.weight
```

### 4.5 MONITORING FREQUENCY

#### 4.5.1 Real-Time Monitoring

**Transaction Events:**

- Transaction created
- Transaction submitted
- Payment executed

**Processing:**

- Evaluate all enabled scenarios
- Generate alerts immediately
- Block transaction if critical match (optional)

**Latency Requirement:** < 1 minute from transaction creation to alert generation

#### 4.5.2 Batch Monitoring

**Daily Batch:**

- Cumulative scenario evaluation
- Historical pattern analysis
- Cross-customer pattern detection

**Weekly Batch:**

- Trend analysis
- False positive review
- Scenario effectiveness evaluation

**Monthly Batch:**

- Expected vs actual volume comparison
- Customer behavior profiling update
- Risk model recalibration

### 4.6 ALERT WORKFLOW

#### 4.6.1 Alert States

1. **Generated** - Alert created by system
2. **Assigned** - Routed to analyst
3. **Under Review** - Analyst investigating
4. **Escalated** - Requires senior review
5. **Resolved** - Decision made (cleared or SAR filed)
6. **Closed** - Alert closed with outcome

#### 4.6.2 Alert Routing

**Assignment Rules:**
| Alert Severity | Assigned To | SLA |
|----------------|-------------|-----|
| Critical | Senior Compliance Analyst | 4 hours |
| High | Compliance Analyst | 24 hours |
| Medium | AML Officer | 72 hours |
| Low | AML Operations | 7 days |

**Escalation:**

- Auto-escalate if SLA breached
- Escalate if analyst uncertain
- Escalate if potential SAR filing

#### 4.6.3 Alert Resolution

**Resolution Outcomes:**

- **Cleared** - Transaction legitimate, no action needed
- **Enhanced Monitoring** - Increase scrutiny, no immediate action
- **Request Information** - Contact customer for clarification
- **SAR Filed** - Suspicious activity reported to authorities
- **Relationship Terminated** - Account closed due to unacceptable risk
- **Law Enforcement Referral** - Escalated to authorities

**Documentation Requirements:**

- Investigation summary
- Supporting evidence
- Decision rationale
- Approval chain (if escalated)

### 4.7 CUSTOMER PROFILING

#### 4.7.1 Behavioral Baseline

**Profile Elements:**

- Average transaction amount
- Transaction frequency (daily, weekly, monthly)
- Common transaction types
- Typical counterparties
- Geographic patterns (countries, cities)
- Temporal patterns (day of week, time of day)
- Channel preferences

**Baseline Period:** 90 days (minimum)

#### 4.7.2 Profile Updates

**Trigger Events:**

- Significant behavior change
- New product adoption
- Business activity change
- Quarterly recalibration

**Update Process:**

1. Analyze recent transaction history
2. Compare to existing profile
3. Identify material changes
4. Update expected behavior parameters
5. Adjust monitoring thresholds

### 4.8 CONFIGURATION

#### 4.8.1 Scenario Configuration

**Per Scenario:**

```
{
  scenario_id: string
  enabled: boolean
  thresholds: {
    amount: number
    frequency: number
    period_days: number
  }
  risk_delta: number
  weight: number
  applies_to: {
    customer_types: ["individual", "legal_entity"]
    risk_levels: ["low", "medium", "high"]
    products: string[]
    jurisdictions: string[]
  }
}
```

**Global Configuration:**

```
{
  real_time_monitoring: boolean
  batch_monitoring: boolean
  alert_aggregation_window: number (hours)
  auto_case_creation: boolean
  sla_tracking: boolean
  risk_thresholds: {
    low_medium: number
    medium_high: number
    high_critical: number
  }
}
```

#### 4.8.2 Risk-Based Configuration

**By Customer Risk Level:**

- High-risk customers: Lower thresholds, more scenarios
- Medium-risk customers: Standard thresholds
- Low-risk customers: Higher thresholds, core scenarios only

**By Jurisdiction:**

- High-risk jurisdictions: Enhanced monitoring
- Standard jurisdictions: Regular monitoring
- Low-risk jurisdictions: Baseline monitoring

### 4.9 REPORTING

#### 4.9.1 Management Reports

**Alert Statistics:**

- Alerts generated by scenario
- Alerts by severity
- Alert resolution time (SLA compliance)
- Alert outcomes (cleared, SAR filed, etc.)
- False positive rate by scenario
- Analyst productivity metrics

**Trend Analysis:**

- Alert volume trends
- Scenario effectiveness
- Customer risk distribution
- Geographic risk patterns

#### 4.9.2 Regulatory Reports

**Transaction Monitoring Effectiveness:**

- Number of SARs filed from monitoring
- Coverage statistics (% of transactions monitored)
- Scenario performance metrics
- Model validation results

**Suspicious Activity:**

- Summary of suspicious patterns detected
- SAR filing statistics
- High-risk customer activity

### 4.10 CASE INTEGRATION

#### 4.10.1 Automatic Case Creation

```
IF alert.severity >= case_creation_threshold THEN
  existing_case = find_open_case(customer_id, trigger="transaction_risk")

  IF existing_case EXISTS:
    UPDATE existing_case {
      add_alert(alert)
      update_priority(alert.severity)
    }
  ELSE:
    CREATE CASE {
      customer_id: alert.customer_id
      trigger: "transaction_risk"
      priority: map_severity_to_priority(alert.severity)
      status: "investigating"
      alerts: [alert]
      assigned_to: route_by_severity(alert.severity)
    }
```

**Case Creation Thresholds:**

- Critical alerts: Always create case
- High alerts: Create if 2+ in 30 days
- Medium alerts: Create if 3+ in 60 days

#### 4.10.2 Case Workflow Integration

1. Alert generated → Case created (if threshold met)
2. Analyst reviews transaction(s)
3. Requests additional information if needed
4. Makes determination: legitimate or suspicious
5. If suspicious: Prepare SAR
6. Document decision
7. Close case with outcome

### 4.11 PERFORMANCE REQUIREMENTS

- **Real-Time Processing:** < 1 minute latency from transaction to alert
- **Throughput:** 10,000+ transactions per hour
- **Concurrent Evaluation:** 100+ simultaneous scenario evaluations
- **Historical Analysis:** Query 3+ years of transaction data
- **Report Generation:** < 30 seconds for standard reports
- **Alert Dashboard:** Real-time updates (< 5 seconds refresh)

### 4.12 DATA RETENTION

**Transaction Data:**

- Minimum 7 years retention
- All transaction details and metadata
- Original transaction payload

**Alert Data:**

- Permanent retention
- Alert details and resolution
- Investigation notes
- Supporting documentation

**Audit Trail:**

- All monitoring events
- Configuration changes
- Scenario triggers and evaluations
- Analyst actions and decisions

---

## 5. CASE MANAGEMENT

### 5.1 OVERVIEW

Case management provides a centralized system for tracking, investigating, and resolving compliance-related investigations. Cases aggregate alerts, evidence, decisions, and documentation throughout the investigation lifecycle.

**Purpose:**

- Centralize compliance investigations
- Track alert resolution and decision-making
- Maintain audit trail of investigation activities
- Support SAR/STR filing workflow
- Enable collaboration among compliance team
- Demonstrate regulatory compliance

**Scope:**

- Alert-generated cases
- Manually created investigations
- Customer due diligence reviews
- Transaction investigations
- Sanctions match resolutions
- PEP relationship reviews
- KYC remediation cases

### 5.2 CASE TRIGGERS

#### 5.2.1 Automatic Triggers

Cases are automatically created when:

**1. Sanctions Match**

```
IF screening_result.has_sanctions_match
   AND screening_result.score >= sanctions_threshold THEN
  CREATE CASE {
    trigger: "sanction"
    priority: "critical"
    description: "Sanctions screening match detected"
  }
```

**2. PEP Identification**

```
IF screening_result.has_pep_match
   AND screening_result.score >= pep_threshold THEN
  CREATE CASE {
    trigger: "pep"
    priority: "high"
    description: "PEP relationship identified"
  }
```

**3. Transaction Risk Alert**

```
IF transaction_alert.severity >= "high"
   OR transaction_alert.count >= threshold_for_medium THEN
  CREATE CASE {
    trigger: "transaction_risk"
    priority: map_severity(alert.severity)
    description: "Suspicious transaction pattern detected"
  }
```

**4. Risk Level Escalation**

```
IF customer.risk_level_changed
   AND new_risk_level == "high"
   AND old_risk_level != "high" THEN
  CREATE CASE {
    trigger: "risk_level_change"
    priority: "medium"
    description: "Customer risk level elevated to high"
  }
```

**5. KYC Expiration**

```
IF customer.kyc_expired == true
   AND customer.risk_level IN ["medium", "high"] THEN
  CREATE CASE {
    trigger: "kyc_issue"
    priority: "medium"
    description: "KYC documentation expired"
  }
```

**6. Adverse Media Hit**

```
IF adverse_media_match.confirmed == true THEN
  CREATE CASE {
    trigger: "adverse_media"
    priority: "high"
    description: "Confirmed adverse media match"
  }
```

**7. Internal Watch List Match**

```
IF internal_watchlist_match == true THEN
  CREATE CASE {
    trigger: "internal_watch_list"
    priority: "high"
    description: "Internal watch list match"
  }
```

#### 5.2.2 Manual Triggers

**User-Initiated Cases:**

- Compliance officer discretionary review
- Customer complaint investigation
- Regulator enquiry follow-up
- Internal audit finding
- Relationship manager escalation

**Manual Case Creation:**

```
CREATE CASE {
  trigger: "manual"
  priority: user_specified
  description: user_provided_description
  created_by: user_id
}
```

### 5.3 CASE LIFECYCLE

#### 5.3.1 Case States

**State Definitions:**

1. **Open**

   - Case newly created
   - Awaiting assignment
   - Initial state for all cases

2. **Investigating**

   - Case assigned to analyst
   - Investigation in progress
   - Information gathering phase

3. **Under Review**

   - Investigation complete
   - Awaiting senior review
   - Decision pending

4. **Pending Info**

   - Awaiting customer response
   - External information requested
   - Temporarily paused

5. **Resolved - Approved**

   - Investigation complete
   - Customer/transaction cleared
   - No suspicious activity found

6. **Resolved - Rejected**

   - Investigation complete
   - SAR filed or relationship terminated
   - Suspicious activity confirmed

7. **Closed**
   - Case archived
   - All actions completed
   - Final state

**State Transitions:**

```
Open → Investigating → Under Review → Resolved (Approved/Rejected) → Closed
         ↓                ↑
    Pending Info ←────────┘
```

#### 5.3.2 State Business Rules

**Transition Rules:**

```
Open → Investigating:
  REQUIRES: assigned_to_user_id NOT NULL

Investigating → Under Review:
  REQUIRES: investigation_notes_completed
  REQUIRES: evidence_gathered

Under Review → Resolved:
  REQUIRES: senior_approval (if priority >= "high")
  REQUIRES: decision_recorded
  REQUIRES: decision_rationale_documented

Investigating → Pending Info:
  REQUIRES: information_request_documented

Pending Info → Investigating:
  REQUIRES: information_received OR timeout_expired

Resolved → Closed:
  REQUIRES: all_tasks_completed
  REQUIRES: all_outcomes_documented
  OPTIONAL: cooling_off_period_elapsed (configurable)
```

### 5.4 CASE PRIORITY

#### 5.4.1 Priority Levels

| Priority     | Definition                                | Target Resolution | Escalation |
| ------------ | ----------------------------------------- | ----------------- | ---------- |
| **Critical** | Sanctions match, immediate risk           | 24 hours          | 4 hours    |
| **High**     | PEP, high-risk transaction, adverse media | 72 hours          | 24 hours   |
| **Medium**   | Risk escalation, KYC issues               | 7 days            | 3 days     |
| **Low**      | Routine reviews, low-risk alerts          | 30 days           | 14 days    |

#### 5.4.2 Priority Calculation

```
priority = determine_priority(trigger, customer_risk, alert_severity)

IF trigger == "sanction":
  priority = "critical"
ELIF trigger == "pep":
  priority = "high"
ELIF trigger == "transaction_risk":
  priority = map_severity_to_priority(alert.severity)
ELIF trigger == "adverse_media":
  priority = "high"
ELIF trigger == "risk_level_change" AND new_level == "high":
  priority = "high"
ELSE:
  priority = "medium"

Function map_severity_to_priority(severity):
  IF severity == "critical": RETURN "critical"
  IF severity == "high": RETURN "high"
  IF severity == "medium": RETURN "medium"
  RETURN "low"
```

### 5.5 CASE COMPONENTS

#### 5.5.1 Core Case Data

**Basic Information:**

```
{
  case_id: string (unique identifier)
  public_id: string (human-readable, e.g., "CASE-2024-0001")
  organization_id: string
  customer_id: string (required)
  transaction_id: string (optional)

  trigger: enum [
    "sanction", "pep", "kyc_issue", "risk_level_change",
    "adverse_media", "internal_watch_list", "transaction_risk",
    "manual", "other"
  ]

  source: enum [
    "screening", "transaction_monitoring", "manual",
    "periodic_review", "external_referral"
  ]

  status: enum [
    "open", "investigating", "under_review", "pending_info",
    "resolved_approved", "resolved_rejected", "closed"
  ]

  priority: enum ["low", "medium", "high", "critical"]

  short_description: string (max 200 chars)
  long_description: string (optional, markdown supported)

  created_at: datetime
  updated_at: datetime
  due_at: datetime (calculated from priority SLA)
  closed_at: datetime (nullable)

  created_by_user_id: string
  assigned_to_user_id: string (nullable)

  risk_score: integer (nullable)
  tags: string[] (for categorization/filtering)
}
```

#### 5.5.2 Alerts

**Alert Linking:**

```
{
  case_alerts: [
    {
      alert_id: string
      provider: string (e.g., "yente", "internal", "transaction_monitor")
      rule_id: string (nullable)
      rule_title: string (e.g., "High-Value Transaction")
      score: number (0.0 - 1.0)
      severity: enum ["low", "medium", "high", "critical"]
      payload: object (alert-specific data)
      created_at: datetime
    }
  ]
}
```

**Alert Management:**

- Add alerts to existing case (consolidation)
- Link related alerts
- Track alert resolution individually or collectively
- Update case priority if new high-severity alert added

#### 5.5.3 Notes

**Investigation Notes:**

```
{
  case_notes: [
    {
      note_id: string
      content: string (markdown supported)
      note_type: enum ["investigation", "communication", "decision", "general"]
      is_internal: boolean (hide from customer-facing reports)
      created_by_user_id: string
      created_at: datetime
      updated_at: datetime
    }
  ]
}
```

**Note Types:**

- **Investigation:** Findings, analysis, observations
- **Communication:** Customer interactions, external correspondence
- **Decision:** Decision rationale, approval notes
- **General:** General comments, reminders

#### 5.5.4 Tasks

**Task Management:**

```
{
  case_tasks: [
    {
      task_id: string
      title: string
      description: string (nullable)
      status: enum ["open", "in_progress", "completed", "cancelled"]
      assigned_to_user_id: string (nullable)
      due_at: datetime (nullable)
      completed_at: datetime (nullable)
      created_at: datetime
    }
  ]
}
```

**Common Tasks:**

- Request source of funds documentation
- Verify UBO information
- Conduct enhanced due diligence
- Review transaction history
- Contact customer for clarification
- Prepare SAR/STR report
- Obtain senior management approval
- Update customer risk assessment

#### 5.5.5 Attachments

**Document Attachments:**

```
{
  case_attachments: [
    {
      attachment_id: string
      file_name: string
      file_size: integer (bytes)
      file_type: string (MIME type)
      storage_url: string
      uploaded_by_user_id: string
      uploaded_at: datetime
      description: string (nullable)
      document_type: enum [
        "evidence", "correspondence", "id_document",
        "financial_statement", "sar_report", "other"
      ]
    }
  ]
}
```

**Supported Document Types:**

- PDF documents
- Images (JPG, PNG)
- Email correspondence (EML, MSG)
- Office documents (DOC, XLS)
- Transaction reports (CSV, XLS)

#### 5.5.6 Timeline

**Audit Timeline:**

```
{
  case_timeline: [
    {
      event_id: string
      event_type: enum [
        "case_created", "status_changed", "assigned", "reassigned",
        "note_added", "task_created", "task_completed",
        "alert_added", "attachment_added", "decision_made",
        "approved", "escalated", "closed"
      ]
      description: string (auto-generated or user-provided)
      metadata: object (event-specific data)
      user_id: string (nullable for system events)
      timestamp: datetime
    }
  ]
}
```

**Auto-Generated Events:**

- Case created
- Status transitions
- Assignment changes
- SLA breaches
- Priority changes
- System-generated updates

**User Events:**

- Notes added
- Tasks created/completed
- Attachments uploaded
- Decisions recorded

#### 5.5.7 Decisions

**Decision Recording:**

```
{
  case_decisions: [
    {
      decision_id: string
      decision: enum ["approved", "rejected", "escalated", "requires_info"]
      decision_type: enum [
        "relationship_approval", "transaction_approval",
        "sar_filing", "account_closure", "edd_required",
        "cleared", "escalate_to_law_enforcement"
      ]
      rationale: string (detailed explanation)
      made_by_user_id: string
      approved_by_user_id: string (for escalated decisions)
      made_at: datetime
      supporting_evidence: string[] (attachment IDs)
    }
  ]
}
```

**Decision Requirements:**

- **High Priority Cases:** Senior compliance officer approval required
- **Critical Cases:** MLRO (Money Laundering Reporting Officer) approval required
- **SAR Filing:** Dual approval (maker-checker)
- **Account Closure:** Senior management approval

### 5.6 CASE OUTCOMES

#### 5.6.1 Outcome Types

**Regulatory Actions:**

- `sar_submitted` - Suspicious Activity Report filed
- `str_submitted` - Suspicious Transaction Report filed
- `pnmr_filed` - Politically exposed persons and non-cooperative jurisdictions report
- `law_enforcement_enquiry` - Referred to law enforcement

**Compliance Actions:**

- `adverse_media_confirmed` - Adverse media validated as credible
- `edd_completed_no_action` - EDD performed, no issues found
- `edd_satisfied` - EDD completed, relationship approved
- `sanctions_match_confirmed` - True positive sanctions match
- `sanctions_match_false_positive` - False positive, cleared
- `pep_confirmed_approved` - PEP confirmed, relationship approved with EDD

**Operational Actions:**

- `no_action_needed` - Investigation concluded, no issues
- `enhanced_monitoring` - Ongoing enhanced scrutiny applied
- `relationship_terminated` - Account closed/relationship ended
- `customer_offboarded` - Customer exited

**Multiple Outcomes:**
Cases can have multiple outcomes (e.g., EDD completed + Enhanced monitoring)

#### 5.6.2 Outcome Recording

```
{
  case_outcomes: enum[] [
    "sar_submitted", "str_submitted", "pnmr_filed",
    "law_enforcement_enquiry", "adverse_media_confirmed",
    "edd_completed_no_action", "edd_satisfied",
    "sanctions_match_confirmed", "sanctions_match_false_positive",
    "pep_confirmed_approved", "no_action_needed",
    "enhanced_monitoring", "relationship_terminated",
    "customer_offboarded"
  ]

  outcome_details: {
    sar_reference: string (if SAR filed)
    filing_date: datetime
    regulatory_authority: string
    termination_reason: string (if relationship terminated)
    edd_summary: string
  }
}
```

### 5.7 CASE ASSIGNMENT & ROUTING

#### 5.7.1 Assignment Rules

**Auto-Assignment Logic:**

```
assigned_user = determine_assignment(case)

IF case.trigger == "sanction":
  assigned_user = get_sanctions_specialist()
ELIF case.trigger == "pep":
  assigned_user = get_pep_specialist()
ELIF case.trigger == "transaction_risk":
  assigned_user = get_available_analyst(priority=case.priority)
ELIF case.priority == "critical":
  assigned_user = get_senior_analyst()
ELSE:
  assigned_user = round_robin_assignment()
```

**Workload Balancing:**

- Track open cases per analyst
- Limit concurrent high-priority cases
- Consider analyst specialization (sanctions, PEP, transaction)
- Allow manual reassignment by supervisor

#### 5.7.2 Escalation

**Auto-Escalation Triggers:**

```
IF case.created_at + sla_period < current_time AND case.status NOT IN resolved_states:
  ESCALATE CASE

IF case.priority == "critical" AND case.age > 4 hours:
  ESCALATE CASE

IF case.has_sanctions_match AND case.status != "under_review" AND age > 12 hours:
  ESCALATE CASE
```

**Escalation Actions:**

- Notify assigned analyst
- Notify supervisor
- Increase priority (if applicable)
- Add timeline event
- Send system alert

**Escalation Hierarchy:**

1. Assigned Analyst
2. Team Lead
3. Compliance Manager
4. MLRO (Money Laundering Reporting Officer)
5. Chief Compliance Officer

### 5.8 CASE SEARCH & FILTERING

#### 5.8.1 Search Criteria

**Available Filters:**

```
{
  customer_id: string
  customer_name: string (fuzzy search)
  status: enum[]
  priority: enum[]
  trigger: enum[]
  source: enum[]
  assigned_to: string (user_id)
  created_by: string (user_id)

  date_ranges: {
    created_from: datetime
    created_to: datetime
    due_from: datetime
    due_to: datetime
    closed_from: datetime
    closed_to: datetime
  }

  tags: string[]
  has_overdue_sla: boolean
  risk_score_min: integer
  risk_score_max: integer

  outcomes: enum[]
  has_sar_filed: boolean

  full_text_search: string (search in descriptions, notes)
}
```

#### 5.8.2 Sorting & Pagination

**Sort Options:**

- Created date (newest/oldest)
- Updated date (most/least recently updated)
- Due date (most/least urgent)
- Priority (highest/lowest)
- Status
- Customer name (alphabetical)

**Pagination:**

- Page size: 10, 25, 50, 100 records
- Total count provided
- Cursor-based pagination for large datasets

### 5.9 CASE COLLABORATION

#### 5.9.1 Multi-User Collaboration

**Features:**

- Multiple users can view case simultaneously
- Real-time updates to case data
- Activity feed showing recent actions
- @mention support in notes
- Task assignment to other users
- Comment threads on notes

#### 5.9.2 Approval Workflow

**Maker-Checker Pattern:**

```
1. Analyst completes investigation (Maker)
2. Analyst moves case to "Under Review"
3. Senior officer reviews findings (Checker)
4. Senior officer makes decision (Approve/Reject/Request More Info)
5. If approved: Case moves to Resolved
6. If rejected: Case returns to Investigating with feedback
```

**Approval Requirements by Case Type:**
| Case Type | Level 1 Approval | Level 2 Approval |
|-----------|-----------------|------------------|
| SAR Filing | Compliance Analyst | MLRO |
| Account Closure | Compliance Manager | CCO |
| PEP Approval | Senior Analyst | Compliance Manager |
| High-Risk Onboarding | Senior Analyst | MLRO |
| Sanctions Clear | Sanctions Specialist | Compliance Manager |

### 5.10 SLA MANAGEMENT

#### 5.10.1 SLA Calculation

```
sla_due_date = case.created_at + sla_duration(case.priority)

Function sla_duration(priority):
  IF priority == "critical": RETURN 24 hours
  IF priority == "high": RETURN 72 hours
  IF priority == "medium": RETURN 7 days
  IF priority == "low": RETURN 30 days
```

**Business Hours vs Calendar Hours:**

- Critical: Calendar hours (24/7)
- High: Business hours (excludes weekends/holidays)
- Medium: Business hours
- Low: Business hours

#### 5.10.2 SLA Tracking

**SLA States:**

- **On Time:** Current time < due date
- **At Risk:** (due date - current time) < warning_threshold
- **Breached:** Current time > due date

**Warning Thresholds:**

- Critical: 2 hours before due
- High: 12 hours before due
- Medium: 1 day before due
- Low: 5 days before due

**SLA Pausing:**

- Pause SLA when status = "Pending Info"
- Resume SLA when information received
- Document pause reason and duration

### 5.11 REPORTING & ANALYTICS

#### 5.11.1 Case Metrics

**Volume Metrics:**

- Total cases created (by period)
- Open cases (current)
- Cases by status
- Cases by priority
- Cases by trigger type

**Performance Metrics:**

- Average resolution time (by priority)
- SLA compliance rate
- Cases breached SLA
- Cases at risk of SLA breach
- Escalation rate

**Outcome Metrics:**

- SARs filed
- Relationships terminated
- False positive rate
- True positive rate
- Case clearance rate

**Analyst Metrics:**

- Cases per analyst
- Average resolution time per analyst
- SLA compliance per analyst
- Case backlog per analyst

#### 5.11.2 Management Reports

**Daily Report:**

- New cases created (last 24 hours)
- Critical/high priority open cases
- SLA breaches (last 24 hours)
- Cases requiring escalation

**Weekly Report:**

- Case volume trends
- Resolution time trends
- SLA compliance summary
- Top triggers for cases
- Analyst workload distribution

**Monthly Report:**

- Comprehensive case statistics
- Outcome analysis
- Regulatory filing summary (SARs, STRs)
- Risk trend analysis
- Effectiveness of monitoring scenarios

### 5.12 INTEGRATION POINTS

#### 5.12.1 Customer Integration

**Bidirectional Linking:**

- Case linked to customer record
- Customer record shows all related cases
- Customer risk level updates trigger case creation
- Case outcomes update customer risk profile

#### 5.12.2 Transaction Integration

**Transaction Cases:**

- Case linked to specific transaction(s)
- Transaction history accessible from case
- Transaction alerts consolidated in case
- Case decision may block/approve transaction

#### 5.12.3 Screening Integration

**Screening Events:**

- Screening results trigger case creation
- Screening history visible in case
- Case decision updates screening resolution
- Rescreening events linked to existing case

#### 5.12.4 Reporting Integration

**SAR/STR Generation:**

- Case data populates report templates
- Transaction data auto-extracted
- Customer data auto-populated
- Case timeline provides narrative basis
- Attachments included as evidence

### 5.13 DATA RETENTION

**Case Records:**

- Minimum 7 years retention from case closure
- All case data, notes, attachments preserved
- Timeline immutable after case closed
- Decisions permanently recorded

**Regulatory Requirements:**

- SAR-related cases: 10 years minimum (jurisdiction-dependent)
- Sanctions cases: Permanent retention
- Transaction cases: 7 years minimum

**Archive Policy:**

- Cases closed > 7 years moved to cold storage
- Searchable but read-only
- Retrieval for audits supported

### 5.14 PERMISSIONS & ACCESS CONTROL

#### 5.14.1 Role-Based Access

**Roles:**

- **AML Analyst:** Create, view, update assigned cases; add notes, tasks, attachments
- **Senior Analyst:** All analyst permissions + approve decisions, reassign cases
- **Compliance Manager:** View all cases, approve high-priority decisions, manage team
- **MLRO:** Full access, final approval authority, SAR filing
- **Auditor:** Read-only access to all cases and audit trail
- **System Admin:** Configuration management, no case decision authority

#### 5.14.2 Data Access Rules

**Customer Access:**

- Users can only access cases for customers in their organization
- Multi-tenant isolation enforced

**Case Assignment:**

- Unassigned cases visible to all eligible analysts
- Assigned cases visible to assignee and supervisors
- Closed cases visible to all compliance team members

**Sensitive Cases:**

- Option to mark cases as "Restricted"
- Restricted cases require special permission
- Enhanced audit logging for restricted case access

### 5.15 PERFORMANCE REQUIREMENTS

- **Case Creation:** < 1 second
- **Case Update:** < 500ms
- **Case Search:** < 2 seconds (for 100,000+ cases)
- **Dashboard Load:** < 3 seconds
- **Report Generation:** < 30 seconds
- **Concurrent Users:** Support 50+ simultaneous case views/edits
- **Real-Time Updates:** < 5 seconds for activity feed refresh

---

## 6. ALERT MANAGEMENT

### 6.1 OVERVIEW

Alert management handles the detection, routing, investigation, and resolution of suspicious activity alerts generated by various monitoring systems. Alerts serve as triggers for compliance investigation and potential case creation.

**Purpose:**

- Capture suspicious activities from monitoring engines
- Route alerts to appropriate analysts
- Track alert investigation and resolution
- Support case aggregation and linkage
- Maintain alert audit trail
- Enable alert quality analysis

**Scope:**

- Transaction monitoring alerts
- Screening match alerts
- Risk assessment alerts
- Customer behavior alerts
- System-generated alerts
- Manual alerts

### 6.2 ALERT TYPES

#### 6.2.1 Alert Type Definitions

**Transaction-Based Alerts:**

- `transaction_risk` - Transaction monitoring scenario triggered
- `high_value_transaction` - Single transaction exceeds threshold
- `cumulative_volume` - Aggregate volume threshold breached
- `structuring` - Pattern suggesting transaction structuring
- `layering` - Rapid in-out transaction pattern
- `velocity_anomaly` - Unusual transaction frequency

**Screening Alerts:**

- `sanctions_match` - Potential match on sanctions list
- `pep_match` - Politically Exposed Person identified
- `adverse_media` - Negative media coverage found
- `watch_list_match` - Internal/external watch list hit

**Risk Alerts:**

- `high_risk_customer` - Customer risk level elevated to high
- `kyc_expiry` - Know Your Customer documentation expired
- `risk_escalation` - Significant risk increase detected
- `jurisdiction_risk` - High-risk jurisdiction interaction

**Behavioral Alerts:**

- `dormant_reactivation` - Dormant account suddenly active
- `profile_deviation` - Activity deviates from expected behavior
- `third_party_payments` - Unusual third-party payment pattern
- `channel_anomaly` - Unexpected channel usage

#### 6.2.2 Alert Classification Matrix

| Alert Type             | Source System       | Typical Severity | Auto-Case Creation |
| ---------------------- | ------------------- | ---------------- | ------------------ |
| sanctions_match        | Screening           | Critical         | Yes                |
| pep_match              | Screening           | High             | Yes                |
| transaction_risk       | Transaction Monitor | Medium-High      | Conditional        |
| high_value_transaction | Transaction Monitor | Medium           | Conditional        |
| structuring            | Transaction Monitor | High             | Yes                |
| kyc_expiry             | Customer System     | Medium           | No                 |
| risk_escalation        | Risk Engine         | Medium-High      | Yes                |
| adverse_media          | Screening           | High             | Yes                |

### 6.3 ALERT SEVERITY

#### 6.3.1 Severity Levels

**Critical (Level 4):**

- Sanctions match confirmed or high confidence
- Immediate regulatory reporting required
- Potential relationship termination
- Requires immediate senior management attention

**High (Level 3):**

- PEP identification
- Confirmed adverse media
- Structuring pattern detected
- Multiple transaction scenarios triggered
- Requires expedited review

**Medium (Level 2):**

- Single transaction monitoring scenario
- Risk level increase
- KYC expiration for medium/high-risk customers
- Profile deviation
- Standard investigation required

**Low (Level 1):**

- Routine threshold breaches
- Low-risk customer anomalies
- Information gathering alerts
- Monitoring alerts

#### 6.3.2 Severity Calculation

```
severity = calculate_severity(alert_type, risk_factors, customer_context)

Base Severity by Type:
- sanctions_match: Critical
- structuring: High
- pep_match: High
- transaction_risk: Medium
- profile_deviation: Low

Adjustments:
IF customer.risk_level == "high":
  severity = increase_severity(severity, +1 level)

IF multiple_alerts_in_period:
  severity = increase_severity(severity, +1 level)

IF alert.score > high_confidence_threshold:
  severity = increase_severity(severity, +1 level)

IF customer.has_prior_sar:
  severity = increase_severity(severity, +1 level)
```

**Example:**

```
Alert Type: transaction_risk (Base: Medium)
Customer Risk: High (+1 level → High)
Multiple Alerts: 3 in last 30 days (+1 level → Critical)
Final Severity: Critical
```

### 6.4 ALERT GENERATION

#### 6.4.1 Generation Process

**Step 1: Event Detection**

```
monitoring_system detects suspicious_activity:
  - Transaction monitoring engine evaluates scenarios
  - Screening system identifies matches
  - Risk engine detects risk changes
  - Customer behavior analysis flags anomalies
```

**Step 2: Alert Creation**

```
CREATE ALERT {
  alert_type: determined from event
  severity: calculated from rules
  customer_id: subject of alert
  transaction_id: related transaction (if applicable)
  description: auto-generated summary
  details: event-specific data
  score: confidence/risk score
  created_at: current timestamp
  source_system: originating system
}
```

**Step 3: Enrichment**

```
ENRICH ALERT with:
  - Customer profile data
  - Historical alert count
  - Related alerts (same customer)
  - Risk assessment scores
  - Screening history
  - Transaction context
```

**Step 4: Routing Decision**

```
IF severity >= case_creation_threshold:
  route_to_case_creation()
ELSE:
  route_to_alert_queue()
```

#### 6.4.2 Deduplication

**Deduplication Logic:**

```
existing_alert = find_similar_alert(
  customer_id,
  alert_type,
  time_window = 24 hours
)

IF existing_alert EXISTS:
  UPDATE existing_alert {
    occurrence_count += 1
    last_occurrence_at = current_time
    severity = recalculate_severity(occurrence_count)
    add_to_related_transactions(new_transaction_id)
  }
ELSE:
  CREATE new_alert
```

**Deduplication Rules:**

- Same alert type for same customer within 24 hours: Deduplicate
- Different alert types: Create separate alerts
- Same type, different customers: Separate alerts
- Screening alerts: Always create new (need individual resolution)

#### 6.4.3 Aggregation

**Alert Aggregation Strategies:**

**1. Customer-Level Aggregation:**

```
Group all alerts for a customer within time window (7 days)
Display aggregated view with:
  - Total alert count by type
  - Highest severity
  - Combined risk score
  - Timeline of alerts
```

**2. Pattern-Based Aggregation:**

```
Identify related alerts across multiple customers:
  - Same transaction chain
  - Same beneficiary
  - Same geographic pattern
  - Same time period
```

**3. Scenario-Based Aggregation:**

```
Group alerts triggered by same monitoring scenario:
  - Analyze effectiveness
  - Identify false positive patterns
  - Tune thresholds
```

### 6.5 ALERT WORKFLOW

#### 6.5.1 Alert States

**State Definitions:**

1. **Generated**

   - Alert created by system
   - Not yet reviewed
   - Waiting in queue

2. **Assigned**

   - Routed to specific analyst
   - In analyst's work queue
   - Not yet opened

3. **Under Review**

   - Analyst actively investigating
   - Information gathering in progress
   - May request additional data

4. **Escalated**

   - Requires senior review
   - Elevated to higher authority
   - May convert to case

5. **Resolved - Cleared**

   - Investigation complete
   - Activity determined legitimate
   - No further action required

6. **Resolved - True Positive**

   - Suspicious activity confirmed
   - Case created or SAR filed
   - Follow-up actions initiated

7. **Resolved - False Positive**
   - Alert determined incorrect
   - System tuning may be needed
   - Feedback for scenario adjustment

**State Transitions:**

```
Generated → Assigned → Under Review → Resolved (Cleared/True Positive/False Positive)
                            ↓
                        Escalated → [continues through review process]
```

#### 6.5.2 Resolution Process

**Investigation Steps:**

1. **Initial Review**

   ```
   - Review alert details and severity
   - Check customer profile and risk level
   - Review historical alerts for customer
   - Assess immediate risk
   ```

2. **Information Gathering**

   ```
   - Review transaction details
   - Analyze transaction patterns
   - Check customer documentation
   - Review screening results
   - Consult external sources if needed
   ```

3. **Analysis**

   ```
   - Compare to expected behavior
   - Evaluate legitimacy indicators
   - Consider customer context
   - Assess red flags
   ```

4. **Decision**

   ```
   - Determine if activity is suspicious
   - Decide on appropriate action
   - Document rationale
   - Select resolution outcome
   ```

5. **Action**
   ```
   - Clear alert (if legitimate)
   - Create case (if requires investigation)
   - File SAR (if meets reporting criteria)
   - Apply enhanced monitoring
   - Request customer information
   ```

#### 6.5.3 Resolution Outcomes

**Possible Outcomes:**

- **No Action Required** - Activity legitimate, consistent with profile
- **Enhanced Monitoring** - Increase scrutiny without immediate action
- **Request Information** - Contact customer for clarification
- **Case Created** - Requires full investigation
- **SAR Filed** - Reportable suspicious activity
- **False Positive** - Alert error, scenario tuning needed

**Outcome Documentation:**

```
{
  resolution_outcome: enum
  resolution_notes: string (analyst explanation)
  supporting_evidence: string[] (references)
  resolved_by_user_id: string
  resolved_at: datetime
  case_id: string (if case created)
  sar_reference: string (if SAR filed)
}
```

### 6.6 ALERT ASSIGNMENT

#### 6.6.1 Assignment Rules

**Priority-Based Assignment:**

```
IF severity == "critical":
  assign_to = senior_analyst_on_duty()
ELIF severity == "high":
  assign_to = available_analyst(specialization="high_priority")
ELIF alert_type IN ["sanctions_match", "pep_match"]:
  assign_to = screening_specialist()
ELSE:
  assign_to = round_robin_assignment()
```

**Workload Balancing:**

```
consider_workload(analysts):
  - Current open alert count
  - Current open case count
  - Analyst availability status
  - Analyst expertise/specialization
  - Historical resolution time
```

**Specialization Routing:**
| Alert Type | Specialist Role |
|------------|----------------|
| sanctions_match | Sanctions Analyst |
| pep_match | PEP Specialist |
| structuring | Financial Crime Analyst |
| transaction_risk | Transaction Monitoring Analyst |
| kyc_expiry | KYC Officer |
| adverse_media | Investigation Specialist |

#### 6.6.2 Reassignment

**Reassignment Triggers:**

- Analyst unavailable (out of office, departed)
- Workload rebalancing needed
- Expertise mismatch identified
- Escalation to senior analyst
- Supervisor override

**Reassignment Process:**

```
REASSIGN alert {
  - Record previous assignee
  - Update assigned_to_user_id
  - Add timeline event
  - Notify new assignee
  - Notify previous assignee (if active)
  - Document reassignment reason
}
```

### 6.7 ALERT PRIORITIZATION

#### 6.7.1 Priority Calculation

```
priority_score = calculate_priority(
  severity,
  customer_risk,
  alert_age,
  occurrence_count
)

priority_score = (severity_weight × 40) +
                 (customer_risk_weight × 30) +
                 (age_factor × 20) +
                 (occurrence_factor × 10)

Where:
- severity_weight: 1.0 (low), 2.0 (medium), 3.0 (high), 4.0 (critical)
- customer_risk_weight: 1.0 (low), 2.0 (medium), 3.0 (high)
- age_factor: increases with time pending
- occurrence_factor: increases with repeated triggers
```

**Priority Ranking:**

```
Sort alerts by priority_score descending
Critical + High Customer Risk + Aged = Highest Priority
Low + Low Customer Risk + Recent = Lowest Priority
```

#### 6.7.2 SLA by Priority

| Priority Level | Target Review Time | Escalation Time |
| -------------- | ------------------ | --------------- |
| Critical       | 4 hours            | 2 hours         |
| High           | 24 hours           | 12 hours        |
| Medium         | 72 hours           | 48 hours        |
| Low            | 7 days             | 5 days          |

**SLA Monitoring:**

```
IF alert.created_at + sla_time < current_time AND alert.status != "resolved":
  trigger_sla_breach_alert()
  escalate_to_supervisor()
  add_timeline_event("SLA Breach")
```

### 6.8 ALERT ENRICHMENT

#### 6.8.1 Contextual Data

**Customer Context:**

- Customer risk level and score
- Customer tenure (days since onboarding)
- Expected transaction volume
- Historical alert count
- Prior SAR/STR filings
- Relationship status (active, dormant, closed)

**Transaction Context:**

- Transaction amount and currency
- Transaction type and channel
- Counterparty information
- Geographic data (origin, destination)
- Related transactions (chain analysis)
- Time and date patterns

**Screening Context:**

- Screening match score
- Match details (name, DOB, nationality)
- List sources (OFAC, UN, EU, etc.)
- Historical screening results
- Related party screening status

**Risk Context:**

- Current CRA score
- Risk component breakdown
- Triggered scenarios
- Applied controls/mitigations
- Recent risk changes

#### 6.8.2 Related Alerts

**Linkage Logic:**

```
related_alerts = find_related_alerts(current_alert)

Criteria:
  - Same customer, last 90 days
  - Same transaction chain
  - Same counterparty
  - Similar pattern/scenario
  - Same geographic indicator
```

**Relationship Types:**

- **Direct:** Same customer, same alert type
- **Indirect:** Same customer, different alert type
- **Network:** Different customer, shared transaction/entity
- **Temporal:** Similar timeframe, similar pattern

### 6.9 ALERT DATA STRUCTURE

#### 6.9.1 Core Alert Schema

```
{
  alert_id: string (unique identifier)
  alert_type: enum (see section 6.2.1)
  severity: enum ["low", "medium", "high", "critical"]
  status: enum ["generated", "assigned", "under_review", "escalated", "resolved"]

  customer_id: string
  transaction_id: string (nullable)

  source_system: enum [
    "transaction_monitoring",
    "screening",
    "risk_engine",
    "manual"
  ]

  short_description: string (auto-generated summary)
  long_description: string (detailed explanation)

  score: number (confidence/risk score, 0.0-1.0 or higher)
  occurrence_count: integer (for deduplicated alerts)

  triggered_rule: {
    rule_id: string
    rule_name: string
    rule_parameters: object
  } (nullable)

  created_at: datetime
  updated_at: datetime
  first_occurrence_at: datetime
  last_occurrence_at: datetime

  assigned_to_user_id: string (nullable)
  assigned_at: datetime (nullable)

  resolved: boolean
  resolved_at: datetime (nullable)
  resolved_by_user_id: string (nullable)
  resolution_outcome: enum (see section 6.5.3)
  resolution_notes: string (nullable)

  case_id: string (nullable, if case created)

  related_alert_ids: string[] (linked alerts)

  metadata: object (alert-type-specific data)
  tags: string[] (for categorization)
}
```

#### 6.9.2 Alert-Specific Metadata

**Transaction Alert Metadata:**

```
{
  transaction_ids: string[] (all related transactions)
  triggered_scenarios: [
    {
      scenario_id: string
      scenario_name: string
      threshold: number
      actual_value: number
      risk_delta: number
    }
  ]
  transaction_risk_score: number
  cumulative_amount: number (if applicable)
  time_period: string (e.g., "30 days")
}
```

**Screening Alert Metadata:**

```
{
  screening_event_id: string
  match_details: {
    entity_name: string
    match_score: number
    name_match_type: enum ["exact", "alias", "fuzzy"]
    dob_match: boolean
    nationality_match: boolean
  }
  list_sources: string[] (e.g., ["OFAC SDN", "UN Consolidated"])
  entity_type: enum ["person", "organization"]
}
```

**Risk Alert Metadata:**

```
{
  risk_assessment_id: string
  previous_risk_level: enum ["low", "medium", "high"]
  new_risk_level: enum ["low", "medium", "high"]
  previous_risk_score: number
  new_risk_score: number
  triggered_scenarios: string[]
  risk_factors: object
}
```

### 6.10 ALERT QUEUE MANAGEMENT

#### 6.10.1 Queue Views

**My Alerts:**

- Alerts assigned to current user
- Sorted by priority/SLA
- Quick filters: severity, alert type, age

**Team Queue:**

- Unassigned alerts for team
- Alerts assigned to team members
- Team performance metrics

**Critical Queue:**

- All critical severity alerts
- Visible to all senior analysts
- Auto-escalation alerts

**Overdue Queue:**

- Alerts exceeding SLA
- Sorted by breach duration
- Requires immediate attention

#### 6.10.2 Queue Operations

**Bulk Operations:**

- Assign multiple alerts to analyst
- Mark multiple as reviewed
- Apply tags to selection
- Export alert list

**Queue Filters:**

```
{
  severity: enum[]
  alert_type: enum[]
  status: enum[]
  customer_risk: enum[]
  date_range: {from, to}
  assigned_to: string (user_id or "unassigned")
  has_related_case: boolean
  sla_status: enum ["on_time", "at_risk", "breached"]
}
```

### 6.11 ALERT QUALITY MANAGEMENT

#### 6.11.1 False Positive Analysis

**False Positive Rate Calculation:**

```
false_positive_rate = (false_positive_count / total_resolved_alerts) × 100

Track by:
  - Alert type
  - Scenario/rule
  - Customer segment
  - Time period
  - Analyst
```

**Acceptable Thresholds:**

- Transaction monitoring: < 20% false positive rate
- Screening: < 10% false positive rate
- Risk alerts: < 15% false positive rate

**Action on High False Positives:**

```
IF false_positive_rate > threshold:
  - Review scenario parameters
  - Adjust thresholds
  - Refine rule logic
  - Consider customer segmentation
  - Retrain models (if ML-based)
```

#### 6.11.2 True Positive Validation

**True Positive Metrics:**

- SAR conversion rate (true positives leading to SAR)
- Case creation rate
- Investigation depth required
- Regulatory feedback (if available)

**Quality Indicators:**

- High-quality alert: Clear indicators, good context, actionable
- Medium-quality alert: Requires investigation, moderate clarity
- Low-quality alert: Vague, requires significant research, low actionability

#### 6.11.3 Scenario Tuning

**Tuning Process:**

```
1. Analyze alert outcomes by scenario
2. Calculate false positive rate per scenario
3. Review threshold effectiveness
4. Identify common false positive patterns
5. Adjust parameters:
   - Increase thresholds (reduce false positives)
   - Decrease thresholds (reduce false negatives)
   - Add exclusion rules
   - Refine customer segmentation
6. Test changes in sandbox environment
7. Deploy tuned scenarios
8. Monitor impact
```

**Tuning Cycle:** Quarterly or when false positive rate > 25%

### 6.12 ALERT REPORTING

#### 6.12.1 Operational Reports

**Daily Alert Summary:**

- Alerts generated (last 24 hours)
- Critical/high alerts outstanding
- SLA breaches
- Resolution rate
- Open alert count by analyst

**Weekly Alert Metrics:**

- Alert volume trends
- Resolution time by severity
- False positive rate
- Alert type distribution
- Analyst performance

**Monthly Alert Analytics:**

- Scenario effectiveness
- Customer segment analysis
- Geographic patterns
- Temporal patterns (time of day, day of week)
- Quality metrics

#### 6.12.2 Management Reports

**Executive Summary:**

- Total alerts vs prior period
- Critical incidents
- SAR conversions
- SLA compliance rate
- Resource allocation recommendations

**Regulatory Reporting:**

- Alert coverage statistics
- Monitoring effectiveness
- Quality assurance results
- Scenario validation

### 6.13 ALERT RETENTION

**Data Retention:**

- Active alerts: Live database
- Resolved alerts: Minimum 7 years
- Alert with SAR/case: 10+ years
- Audit trail: Permanent

**Archive Policy:**

- Alerts resolved > 1 year: Move to warm storage
- Alerts resolved > 5 years: Move to cold storage
- Maintain searchability across all storage tiers

### 6.14 PERFORMANCE REQUIREMENTS

- **Alert Generation:** < 1 minute from event detection
- **Alert Assignment:** < 5 seconds
- **Queue Load Time:** < 2 seconds (100 alerts)
- **Alert Detail Load:** < 1 second
- **Search Performance:** < 3 seconds (1M+ alerts)
- **Bulk Operations:** < 10 seconds (100 alerts)
- **Real-Time Updates:** < 5 seconds refresh
- **Concurrent Users:** 50+ analysts working simultaneously

---

## 7. REPORTING & COMPLIANCE

### 7.1 OVERVIEW

The reporting module generates regulatory-compliant reports for submission to authorities, internal management reporting, and audit trail documentation. Reports aggregate data from cases, transactions, screening, and risk assessments.

**Purpose:**

- Generate regulatory reports (SAR, STR, ECDD)
- Export goAML-compliant XML
- Support internal compliance reporting
- Enable audit trail documentation
- Facilitate regulatory submissions

**Scope:**

- Suspicious Activity Reports (SAR)
- Suspicious Transaction Reports (STR)
- Enhanced Customer Due Diligence (ECDD) reports
- Additional Information Forms (AIF)
- Management reports
- Regulatory statistics

### 7.2 SUSPICIOUS ACTIVITY REPORT (SAR)

#### 7.2.1 SAR Purpose & Scope

**Regulatory Requirement:**
Financial institutions must report suspicious activities that may indicate money laundering, terrorist financing, or other financial crimes to regulatory authorities.

**Reporting Threshold:**

- Activities that raise suspicion (no minimum amount in most jurisdictions)
- Pattern of transactions designed to evade reporting
- Transactions with no apparent business purpose
- Unusual customer behavior

**Timeframe:**

- File within regulatory deadline (typically 15-30 days from detection)
- Urgent cases: File within 24-48 hours

#### 7.2.2 SAR Components

**Report Structure:**

1. **Reporting Institution Information**

   ```
   {
     institution_name: string
     institution_code: string (regulatory identifier)
     contact_person: string
     contact_email: string
     contact_phone: string
     report_date: date
     report_id: string (internal tracking)
   }
   ```

2. **Subject Information**

   ```
   {
     subject_type: "person" | "entity"
     subject_id: string (internal customer ID)

     // For Person
     full_name: string
     date_of_birth: date
     nationality: string[]
     id_type: string (passport, national_id, etc.)
     id_number: string
     address: {
       country: string
       city: string
       street: string
       postal_code: string
     }
     occupation: string

     // For Entity
     legal_name: string
     trade_name: string
     incorporation_country: string
     registration_number: string
     business_sector: string
     ubos: [
       {name, dob, nationality, ownership_percentage}
     ]
   }
   ```

3. **Transaction Information**

   ```
   {
     transactions: [
       {
         transaction_id: string
         transaction_date: datetime
         transaction_type: enum
         amount: number
         currency: string

         from_account: {
           account_number: string
           account_holder: string
           institution: string
         }

         to_account: {
           account_number: string
           account_holder: string
           institution: string
           country: string
         }

         payment_method: string
         is_third_party: boolean
         purpose: string
       }
     ]

     total_amount: number
     transaction_count: integer
     time_period: {from: date, to: date}
   }
   ```

4. **Activity Description**

   ```
   {
     suspicion_reason: string (structured narrative)
     modus_operandi: string (method of operation)

     risk_indicators: [
       "large_amount",
       "structuring",
       "terrorism_finance",
       "third_party_funding",
       "third_party_payments",
       "high_risk_jurisdiction",
       "unusual_pattern"
     ]

     narrative: string (detailed explanation)

     related_parties: [
       {
         name: string
         relationship: string (beneficiary, sender, etc.)
         country: string
         role: string
       }
     ]
   }
   ```

5. **Investigation Details**

   ```
   {
     case_id: string
     investigation_start_date: date
     investigation_end_date: date
     investigator: string
     approved_by: string (MLRO)
     approval_date: date

     actions_taken: [
       "customer_interviewed",
       "documents_requested",
       "transaction_analysis",
       "screening_conducted",
       "external_enquiries"
     ]
   }
   ```

#### 7.2.3 SAR Risk Scoring

**Risk Indicator Weighting:**

```
risk_weights = {
  terrorism_finance: 3.0 (highest)
  structuring: 2.5
  third_party_funding: 2.0
  third_party_payments: 2.0
  large_amount: 1.5
  unusual_pattern: 1.5
  high_risk_jurisdiction: 2.0
}

sar_risk_score = Σ(triggered_indicators × weights) / count(indicators)

risk_level = determine_level(sar_risk_score):
  IF sar_risk_score >= 2.5: "high"
  ELIF sar_risk_score >= 1.5: "medium"
  ELSE: "low"
```

**Example:**

```
Indicators: terrorism_finance (3.0), structuring (2.5), large_amount (1.5)
Risk Score: (3.0 + 2.5 + 1.5) / 3 = 2.33
Risk Level: Medium
```

#### 7.2.4 SAR Generation Process

**Step 1: Initiate Report**

```
- Link to case investigation
- Select subject (customer)
- Select related transactions
- Specify reporting period
```

**Step 2: Auto-Populate Data**

```
- Extract customer information from profile
- Extract transaction details from system
- Extract case investigation notes
- Identify related parties from transactions
- Determine risk indicators
```

**Step 3: AI-Assisted Narrative Generation**

```
AI generates draft narrative based on:
  - Transaction patterns
  - Risk indicators
  - Customer profile
  - Investigation findings
  - Case notes

Narrative includes:
  - Summary of suspicious activity
  - Timeline of events
  - Reasons for suspicion
  - Supporting evidence
  - Recommended further action
```

**Step 4: Human Review & Edit**

```
- Compliance officer reviews auto-generated content
- Edits and refines narrative
- Adds additional context
- Verifies accuracy of all data
- Ensures completeness
```

**Step 5: Approval Workflow**

```
- Analyst submits for review (Maker)
- Senior compliance officer reviews (Checker)
- MLRO final approval (Approver)
- Each approval level documented
```

**Step 6: goAML Export**

```
- Generate goAML-compliant XML
- Validate against schema
- Include all required fields
- Attach supporting documents
- Create submission package
```

**Step 7: Submission & Tracking**

```
- Submit to regulatory authority portal
- Record submission date and reference
- Track acknowledgment receipt
- Update case with SAR filing outcome
- Archive report and supporting docs
```

### 7.3 goAML FORMAT

#### 7.3.1 goAML Overview

**goAML (Global Anti-Money Laundering):**

- International standard for AML reporting
- XML-based format
- Used by many jurisdictions (UAE, Southeast Asia, Africa)
- Enables standardized data exchange

#### 7.3.2 goAML Report Structure

**XML Schema Structure:**

```xml
<report>
  <report_code>SAR</report_code>
  <submission_date>2024-01-15</submission_date>

  <reporting_institution>
    <code>INST001</code>
    <name>Institution Name</name>
    <contact>
      <person>John Doe</person>
      <email>compliance@institution.com</email>
      <phone>+971-x-xxx-xxxx</phone>
    </contact>
  </reporting_institution>

  <subjects>
    <subject>
      <subject_type>natural_person</subject_type>
      <first_name>Ahmed</first_name>
      <middle_name>Mohamed</middle_name>
      <last_name>Al-Rahman</last_name>
      <birth_date>1980-05-15</birth_date>
      <nationality>AE</nationality>
      <identification>
        <type>passport</type>
        <number>A123456789</number>
        <issuing_country>AE</issuing_country>
      </identification>
      <address>
        <country>AE</country>
        <city>Dubai</city>
        <street>Sheikh Zayed Road</street>
        <postal_code>12345</postal_code>
      </address>
    </subject>
  </subjects>

  <transactions>
    <transaction>
      <transaction_id>TXN001</transaction_id>
      <date>2024-01-10</date>
      <type>wire_transfer</type>
      <amount>500000</amount>
      <currency>AED</currency>
      <from_account>
        <account_number>12345678</account_number>
        <institution>INST001</institution>
      </from_account>
      <to_account>
        <account_number>98765432</account_number>
        <institution>EXT_BANK</institution>
        <country>CH</country>
      </to_account>
    </transaction>
  </transactions>

  <suspicious_activity>
    <reason_code>01</reason_code> <!-- Unusual transaction pattern -->
    <description>
      Customer conducted series of high-value transactions to
      high-risk jurisdiction with no clear business purpose...
    </description>
    <indicators>
      <indicator code="L">Large transaction</indicator>
      <indicator code="H">High-risk jurisdiction</indicator>
      <indicator code="T">Third-party payment</indicator>
    </indicators>
  </suspicious_activity>

  <risk_assessment>
    <risk_level>high</risk_level>
    <risk_score>2.8</risk_score>
  </risk_assessment>
</report>
```

#### 7.3.3 goAML Field Mapping

**System Field → goAML Field Mapping:**

| Internal Field         | goAML Element                  | Required | Format             |
| ---------------------- | ------------------------------ | -------- | ------------------ |
| customer.full_name     | subject.name                   | Yes      | String             |
| customer.date_of_birth | subject.birth_date             | Yes      | YYYY-MM-DD         |
| customer.nationality   | subject.nationality            | Yes      | ISO 3166-1 alpha-2 |
| transaction.amount     | transaction.amount             | Yes      | Decimal            |
| transaction.currency   | transaction.currency           | Yes      | ISO 4217           |
| transaction.date       | transaction.date               | Yes      | YYYY-MM-DD         |
| case.risk_score        | risk_assessment.score          | No       | Decimal            |
| alert.risk_indicators  | suspicious_activity.indicators | Yes      | Code list          |

#### 7.3.4 goAML Validation

**Validation Rules:**

```
1. Schema validation: XML must conform to goAML XSD schema
2. Required fields: All mandatory fields present
3. Data format: Dates, codes, amounts in correct format
4. Code lists: Use approved goAML code lists
5. Character encoding: UTF-8
6. File size: Within limits (typically < 10MB per report)
7. Relationships: Valid links between subjects, transactions, accounts
```

**Common Validation Errors:**

- Missing required fields
- Invalid date format
- Unknown country/currency codes
- Invalid indicator codes
- Character encoding issues
- Malformed XML structure

### 7.4 SUSPICIOUS TRANSACTION REPORT (STR)

#### 7.4.1 STR vs SAR

**Differences:**

- **SAR:** Focuses on overall suspicious activity pattern or relationship
- **STR:** Focuses on specific suspicious transaction(s)

**When to File STR:**

- Single transaction raises suspicion
- Transaction characteristics indicate potential crime
- No broader pattern of activity (yet)

#### 7.4.2 STR Components

Similar to SAR but emphasizes:

- Specific transaction details
- Transaction counterparties
- Transaction purpose
- Immediate suspicion triggers

**STR-Specific Fields:**

```
{
  transaction_focus: {
    primary_transaction_id: string
    related_transaction_ids: string[]
  }

  transaction_suspicion: {
    suspicion_type: enum [
      "no_economic_purpose",
      "third_party_unexplained",
      "amount_inconsistent",
      "destination_unexplained",
      "timing_suspicious",
      "method_unusual"
    ]
    immediate_concerns: string
  }
}
```

### 7.5 ENHANCED CUSTOMER DUE DILIGENCE (ECDD) REPORT

#### 7.5.1 ECDD Purpose

**When Required:**

- High-risk customer onboarding
- PEP relationship
- High-risk jurisdiction nexus
- Risk escalation
- Regulatory requirement

**ECDD Objectives:**

- Verify customer identity thoroughly
- Understand source of wealth
- Understand source of funds
- Assess business relationship purpose
- Determine ongoing monitoring requirements

#### 7.5.2 ECDD Report Structure

```
{
  report_id: string
  customer_id: string
  report_date: date
  conducted_by: string
  approved_by: string

  customer_profile: {
    identity_verification: {
      documents_verified: string[]
      verification_method: string
      verification_date: date
      verification_outcome: string
    }

    source_of_wealth: {
      declared_sources: string[]
      supporting_evidence: string[]
      verification_outcome: "verified" | "partially_verified" | "unverified"
      concerns: string
    }

    source_of_funds: {
      declared_sources: string[]
      supporting_documents: string[]
      verification_outcome: "verified" | "partially_verified" | "unverified"
      concerns: string
    }

    business_purpose: {
      stated_purpose: string
      expected_activity: {
        transaction_volume: number
        transaction_frequency: string
        transaction_types: string[]
        counterparty_countries: string[]
      }
      rationale_assessment: string
    }

    pep_status: {
      is_pep: boolean
      pep_type: "domestic" | "foreign" | "international_org"
      position: string
      appointment_date: date
      end_date: date (if former PEP)
      family_relationships: string[]
      close_associates: string[]
    }

    risk_factors: {
      high_risk_jurisdictions: string[]
      adverse_media: boolean
      sanctions_concerns: boolean
      complex_ownership: boolean
      cash_intensive_business: boolean
      other_concerns: string[]
    }
  }

  risk_assessment: {
    inherent_risk_score: number
    residual_risk_score: number
    risk_level: "low" | "medium" | "high"
    risk_rationale: string
  }

  recommendations: {
    relationship_decision: "approve" | "reject" | "requires_further_info"
    monitoring_level: "standard" | "enhanced" | "intensive"
    review_frequency: string
    additional_controls: string[]
    approval_required: boolean
  }

  conclusions: string (summary narrative)

  attachments: [
    {
      document_type: string
      file_name: string
      upload_date: date
    }
  ]
}
```

### 7.6 ADDITIONAL INFORMATION FORM (AIF)

#### 7.6.1 AIF Purpose

**When Required:**

- Follow-up to previously filed SAR
- Regulator requests additional information
- New information emerges after SAR filing
- Update on customer status/actions taken

#### 7.6.2 AIF Structure

```
{
  aif_id: string
  related_sar_reference: string (original SAR ID)
  submission_date: date
  reason_for_submission: enum [
    "regulator_request",
    "additional_evidence",
    "update_on_actions",
    "correction"
  ]

  additional_information: {
    new_transactions: [...] (if applicable)
    new_evidence: string
    customer_updates: string
    investigation_updates: string
    actions_taken: string[]
  }

  submitting_officer: string
  approval: {
    approved_by: string
    approval_date: date
  }
}
```

### 7.7 MANAGEMENT REPORTING

#### 7.7.1 Compliance Dashboard

**Real-Time Metrics:**

- Open cases (by status, priority)
- Open alerts (by severity)
- SLA compliance (cases and alerts)
- High-risk customers (count, percentage)
- Recent SARs filed
- Pending reviews/approvals

#### 7.7.2 Executive Summary Reports

**Monthly Executive Report:**

```
{
  reporting_period: {from: date, to: date}

  case_statistics: {
    total_cases_created: integer
    cases_by_trigger: {trigger: count}
    cases_resolved: integer
    average_resolution_time: number (days)
    sla_compliance_rate: percentage
    open_cases: integer
  }

  alert_statistics: {
    total_alerts_generated: integer
    alerts_by_type: {type: count}
    alerts_by_severity: {severity: count}
    false_positive_rate: percentage
    true_positive_rate: percentage
  }

  regulatory_filings: {
    sars_filed: integer
    strs_filed: integer
    other_filings: integer
  }

  customer_risk_profile: {
    total_customers: integer
    high_risk_customers: integer
    medium_risk_customers: integer
    low_risk_customers: integer
    risk_distribution_change: string
  }

  screening_activity: {
    total_screenings: integer
    sanctions_matches: integer
    pep_identifications: integer
    false_positive_rate: percentage
  }

  transaction_monitoring: {
    transactions_monitored: integer
    scenarios_triggered: {scenario: count}
    monitoring_effectiveness: percentage
  }

  key_highlights: string[]
  areas_of_concern: string[]
  recommendations: string[]
}
```

### 7.8 AUDIT REPORTS

#### 7.8.1 Audit Trail Report

**Purpose:**

- Demonstrate regulatory compliance
- Support internal/external audits
- Document decision-making process
- Evidence due diligence

**Contents:**

```
{
  audit_subject: "customer" | "case" | "transaction" | "screening"
  subject_id: string
  audit_period: {from: date, to: date}

  activities: [
    {
      timestamp: datetime
      activity_type: string
      performed_by: string
      description: string
      before_state: object
      after_state: object
      ip_address: string
      session_id: string
    }
  ]

  key_events: [
    {
      event_date: date
      event_type: string
      description: string
      outcome: string
    }
  ]

  compliance_indicators: {
    kyc_current: boolean
    screening_current: boolean
    risk_assessment_current: boolean
    edd_completed: boolean (if required)
    monitoring_active: boolean
  }
}
```

#### 7.8.2 Compliance Attestation Report

**Annual/Quarterly Compliance Certification:**

```
{
  reporting_period: {from: date, to: date}
  reporting_entity: string

  program_effectiveness: {
    policies_procedures_current: boolean
    staff_training_completed: boolean
    technology_systems_operational: boolean
    quality_assurance_performed: boolean
  }

  regulatory_compliance: {
    cdd_performed: percentage
    edd_performed_when_required: percentage
    transaction_monitoring_coverage: percentage
    screening_coverage: percentage
    timely_sar_filing: percentage
    recordkeeping_compliant: boolean
  }

  risk_assessment: {
    enterprise_risk_assessment_current: boolean
    customer_risk_assessments_current: percentage
    high_risk_customers_reviewed: boolean
  }

  findings: {
    internal_audit_findings: integer
    regulatory_findings: integer
    remediation_status: string
  }

  attestation: {
    attested_by: string (CCO/MLRO)
    title: string
    date: date
    signature: string (digital signature)
  }
}
```

### 7.9 REGULATORY STATISTICS

#### 7.9.1 Required Statistics

**Typical Regulatory Reporting Requirements:**

1. **Customer Base Statistics**

   - Total customers (beginning, end of period)
   - New customers onboarded
   - Customers by risk level
   - High-risk customer percentage
   - PEP count

2. **Transaction Statistics**

   - Total transaction volume
   - Total transaction count
   - Large transactions (above threshold)
   - International transactions
   - Suspicious transactions reported

3. **Screening Statistics**

   - Screenings performed
   - Sanctions matches (true positives)
   - PEP identifications
   - False positive rate

4. **SAR/STR Filings**

   - Total SARs/STRs filed
   - By suspicion category
   - By customer risk level
   - Average time from detection to filing

5. **Case Statistics**
   - Cases opened
   - Cases closed
   - Average resolution time
   - Cases by outcome

### 7.10 EXPORT FORMATS

#### 7.10.1 Supported Formats

**Report Export Options:**

- **PDF:** For regulatory submission, archival, human review
- **XML (goAML):** For electronic regulatory submission
- **Excel/CSV:** For data analysis, internal reporting
- **JSON:** For API integration, system-to-system transfer
- **Word (DOCX):** For editable reports, templates

#### 7.10.2 Format Specifications

**PDF Requirements:**

- PDF/A format (archival standard)
- Embedded fonts
- Searchable text
- Digital signature support
- Tamper-evident

**XML Requirements:**

- UTF-8 encoding
- Schema validation
- Well-formed structure
- Namespace declarations
- Digital signature (if required)

### 7.11 REPORT RETENTION

**Retention Requirements:**

- SAR/STR reports: 10 years minimum
- ECDD reports: 7 years from relationship end
- AIF reports: Same as related SAR
- Management reports: 7 years
- Audit reports: 10 years
- Supporting documents: Same as report

**Storage Requirements:**

- Secure storage (encrypted)
- Access controls (role-based)
- Audit logging (who accessed when)
- Backup and disaster recovery
- Migration plan (format changes)

### 7.12 PERFORMANCE REQUIREMENTS

- **Report Generation:** < 30 seconds for standard reports
- **SAR Generation:** < 2 minutes (with AI assistance)
- **goAML Export:** < 10 seconds
- **Large Dataset Reports:** < 5 minutes (10,000+ records)
- **PDF Rendering:** < 15 seconds
- **Concurrent Report Generation:** Support 10+ simultaneous reports

---

## 8. CONFIGURATION & SETTINGS

### 8.1 OVERVIEW

The configuration module provides centralized management of system parameters, thresholds, rules, and organizational settings. Configuration operates at multiple levels: system defaults, organization overrides, and customer segment customizations.

**Purpose:**

- Centralize system configuration
- Enable organization-level customization
- Support multi-tenant isolation
- Allow dynamic threshold adjustment
- Facilitate regulatory compliance customization

**Configuration Hierarchy:**

```
System Defaults (lowest priority)
    ↓
Organization Settings (overrides defaults)
    ↓
Customer Segment Settings (overrides organization)
    ↓
Individual Customer Overrides (highest priority)
```

### 8.2 ORGANIZATION CONFIGURATION

#### 8.2.1 Organization Profile

```
{
  organization_id: string
  organization_name: string
  regulatory_jurisdiction: string (e.g., "UAE", "UK", "US")
  license_type: string
  mlro: {
    name: string
    email: string
    phone: string
  }

  regulatory_identifiers: {
    license_number: string
    registration_number: string
    regulatory_authority: string
  }

  operational_settings: {
    default_currency: string (ISO 4217)
    timezone: string
    business_hours: {
      start: time
      end: time
      days: string[] (e.g., ["Monday", "Tuesday", ...])
    }
    holidays: date[] (non-business days)
  }
}
```

#### 8.2.2 Risk Configuration

**CRA Settings:**

```
{
  cra_config: {
    component_weights: {
      customer: 0.30
      geography: 0.20
      product: 0.30
      channel: 0.20
    }

    risk_thresholds: {
      low_medium: 1.7
      medium_high: 2.4
    }

    product_aggregation_method: "max" | "mean"

    controls: {
      maximum_reduction: 0.70 (70%)
      minimum_for_downgrade: 0.35 (35%)
    }

    reassessment_intervals: {
      high_risk_days: 180
      medium_risk_days: 365
      low_risk_days: 730
    }
  }
}
```

**CRA Scenarios:**

```
{
  cra_scenarios: {
    pep_status: {
      enabled: boolean
      action: "elevate_high" | "block"
    }

    high_risk_jurisdiction: {
      enabled: boolean
      action: "elevate_high" | "block"
      jurisdictions: string[] (country codes)
    }

    opaque_ownership: {
      enabled: boolean
      action: "elevate_high" | "block"
      max_ownership_layers: integer
    }

    confirmed_sanctions: {
      enabled: boolean
      action: "block" (non-configurable)
      auto_decline: boolean
    }

    sar_str_filed: {
      enabled: boolean
      action: "elevate_high"
    }

    law_enforcement_enquiry: {
      enabled: boolean
      action: "elevate_high"
    }

    adverse_media_confirmed: {
      enabled: boolean
      action: "elevate_high"
    }
  }
}
```

**Transaction Scenarios:**

```
{
  transaction_scenarios: [
    {
      scenario_id: "high_value_single"
      enabled: boolean
      name: "High-Value Single Transaction"
      threshold_amount: number
      risk_delta: number
      weight: number
      applies_to_customer_types: ["individual", "legal_entity"]
      applies_to_risk_levels: ["low", "medium", "high"]
    },
    {
      scenario_id: "high_value_cumulative"
      enabled: boolean
      threshold_amount: number
      period_days: integer (30, 7, 1)
      risk_delta: number
    },
    {
      scenario_id: "dormant_reactivation"
      enabled: boolean
      dormancy_days: integer
      amount_threshold: number
      risk_delta: number
    },
    {
      scenario_id: "high_risk_jurisdiction"
      enabled: boolean
      amount_threshold: number
      jurisdictions: string[]
      risk_delta: number
    },
    {
      scenario_id: "high_risk_channel"
      enabled: boolean
      thresholds: {
        cryptocurrency: number
        international_wire: number
        cash: number
        msb: number
      }
      risk_delta: number
    },
    {
      scenario_id: "new_customer_activity"
      enabled: boolean
      tenure_threshold_days: integer
      amount_threshold: number
      risk_delta: number
    },
    {
      scenario_id: "third_party_payments"
      enabled: boolean
      single_threshold: number
      cumulative_threshold: number
      period_days: integer
      risk_delta: number
    },
    {
      scenario_id: "structuring"
      enabled: boolean
      reporting_threshold: number
      just_below_percentage: number (e.g., 0.9 for 90%)
      frequency_threshold: integer
      period_days: integer
      risk_delta: number
    },
    {
      scenario_id: "velocity_anomaly"
      enabled: boolean
      baseline_period_days: integer
      evaluation_period_days: integer
      multiplier: number (e.g., 3.0 for 3x)
      risk_delta: number
    },
    {
      scenario_id: "round_amounts"
      enabled: boolean
      round_multiples: number[] (e.g., [10000, 20000, 50000])
      frequency_threshold: integer
      period_days: integer
      risk_delta: number
    },
    {
      scenario_id: "rapid_in_out"
      enabled: boolean
      time_window_hours: integer
      percentage_threshold: number (e.g., 0.80 for 80%)
      minimum_amount: number
      risk_delta: number
    },
    {
      scenario_id: "expected_volume_variance"
      enabled: boolean
      variance_threshold: number (e.g., 1.5 for 150%)
      minimum_variance_amount: number
      period_days: integer
      risk_delta: number
    }
  ]
}
```

#### 8.2.3 Screening Configuration

```
{
  screening_config: {
    thresholds: {
      sanctions: 0.6 (60% match confidence)
      pep: 0.6
    }

    datasets: [
      "us_ofac_sdn",
      "un_sc_consolidated",
      "eu_sanctions",
      "uk_hmt_sanctions",
      "opensanctions_peps",
      "internal_watchlist"
    ]

    topics: [
      "sanction",
      "role.pep"
    ]

    algorithm: "logic-v1" | "fuzzy-v2"

    provider: {
      name: "opensanctions" | "dow_jones" | "refinitiv"
      api_endpoint: string
      api_key: string (encrypted)
      timeout_seconds: integer
    }

    rescreening_frequency: {
      high_risk_days: 90
      medium_risk_days: 180
      low_risk_days: 365
    }

    auto_case_creation: {
      sanctions_match: boolean
      pep_match: boolean
      adverse_media: boolean
    }
  }
}
```

#### 8.2.4 Reference Lists

**Products & Services Catalog:**

```
{
  products_services: [
    {
      id: string
      name: string
      category: string
      risk_score: number (1.0 - 3.0)
      description: string
      active: boolean
    }
  ]
}
```

**Onboarding Channels:**

```
{
  onboarding_channels: [
    {
      id: string
      name: string
      risk_score: number (1.0 - 3.0)
      description: string
      active: boolean
    }
  ]
}
```

**Jurisdictions:**

```
{
  jurisdictions: [
    {
      country_code: string (ISO 3166-1 alpha-3)
      country_name: string
      risk_level: "low" | "medium" | "high"
      risk_score: number (1.0 - 3.0)
      is_high_risk: boolean
      is_sanctioned: boolean
      fatf_status: "compliant" | "greylist" | "blacklist"
      notes: string
    }
  ]
}
```

**Business Sectors:**

```
{
  business_sectors: [
    {
      id: string
      name: string
      category: string
      risk_level: "low" | "medium" | "high"
      risk_score: number (1.0 - 3.0)
      description: string
    }
  ]
}
```

#### 8.2.5 Case Management Configuration

```
{
  case_config: {
    sla_settings: {
      critical_hours: 24
      high_hours: 72
      medium_days: 7
      low_days: 30
    }

    auto_case_creation: {
      sanctions_match: boolean
      pep_match: boolean
      transaction_risk_severity_threshold: "medium" | "high" | "critical"
      risk_level_change: boolean
      kyc_expiry: boolean
      adverse_media: boolean
    }

    approval_requirements: {
      high_priority_requires_senior: boolean
      critical_priority_requires_mlro: boolean
      sar_filing_dual_approval: boolean
      account_closure_approval_level: "manager" | "mlro" | "cco"
    }

    assignment_rules: {
      enable_auto_assignment: boolean
      round_robin: boolean
      workload_balancing: boolean
      specialization_routing: boolean
    }
  }
}
```

#### 8.2.6 Alert Configuration

```
{
  alert_config: {
    severity_thresholds: {
      critical: 30
      high: 20
      medium: 10
    }

    sla_by_severity: {
      critical_hours: 4
      high_hours: 24
      medium_hours: 72
      low_days: 7
    }

    deduplication: {
      enabled: boolean
      time_window_hours: 24
    }

    aggregation: {
      customer_level: boolean
      time_window_days: 7
    }

    false_positive_threshold: {
      acceptable_rate: 0.20 (20%)
      review_frequency_days: 90
    }
  }
}
```

#### 8.2.7 Reporting Configuration

```
{
  reporting_config: {
    regulatory_reporting: {
      jurisdiction: string
      goaml_version: string
      reporting_entity_code: string
      preferred_format: "goaml_xml" | "json" | "pdf"
    }

    sar_config: {
      filing_deadline_days: integer (e.g., 30)
      urgent_filing_hours: integer (e.g., 24)
      dual_approval_required: boolean
      mlro_final_approval: boolean
    }

    ai_assistance: {
      enabled: boolean
      narrative_generation: boolean
      risk_indicator_detection: boolean
      model_version: string
    }

    report_retention: {
      sar_str_years: 10
      ecdd_years: 7
      management_reports_years: 7
      audit_reports_years: 10
    }
  }
}
```

### 8.3 USER ROLES & PERMISSIONS

#### 8.3.1 Role Definitions

**Role Hierarchy:**

```
{
  roles: [
    {
      role_id: "aml_analyst"
      name: "AML Analyst"
      permissions: [
        "view_cases_assigned",
        "view_alerts_assigned",
        "create_case",
        "update_case_investigating",
        "add_case_note",
        "add_case_task",
        "add_case_attachment",
        "resolve_alert",
        "screen_customer",
        "view_customer_profile",
        "view_transactions"
      ]
    },
    {
      role_id: "senior_analyst"
      name: "Senior AML Analyst"
      permissions: [
        ...aml_analyst_permissions,
        "view_all_cases",
        "approve_case_decision",
        "reassign_case",
        "escalate_case",
        "override_alert_decision"
      ]
    },
    {
      role_id: "compliance_manager"
      name: "Compliance Manager"
      permissions: [
        ...senior_analyst_permissions,
        "view_all_customers",
        "approve_high_risk_onboarding",
        "approve_edd",
        "manage_team",
        "view_reports",
        "configure_scenarios"
      ]
    },
    {
      role_id: "mlro"
      name: "Money Laundering Reporting Officer"
      permissions: [
        ...compliance_manager_permissions,
        "approve_sar_filing",
        "submit_sar",
        "approve_critical_decisions",
        "terminate_relationship",
        "configure_system"
      ]
    },
    {
      role_id: "auditor"
      name: "Internal Auditor"
      permissions: [
        "view_all_cases",
        "view_all_alerts",
        "view_audit_trail",
        "generate_audit_reports",
        "view_system_logs"
      ]
      restrictions: [
        "read_only",
        "no_case_modification",
        "no_decision_making"
      ]
    },
    {
      role_id: "system_admin"
      name: "System Administrator"
      permissions: [
        "manage_users",
        "manage_roles",
        "configure_organization",
        "manage_integrations",
        "view_system_health",
        "backup_restore"
      ]
      restrictions: [
        "no_case_access",
        "no_decision_authority"
      ]
    }
  ]
}
```

#### 8.3.2 Permission Matrix

| Permission             | Analyst | Senior | Manager | MLRO | Auditor | Admin |
| ---------------------- | ------- | ------ | ------- | ---- | ------- | ----- |
| View assigned cases    | ✓       | ✓      | ✓       | ✓    | ✓       | ✗     |
| View all cases         | ✗       | ✓      | ✓       | ✓    | ✓       | ✗     |
| Create case            | ✓       | ✓      | ✓       | ✓    | ✗       | ✗     |
| Update case            | ✓       | ✓      | ✓       | ✓    | ✗       | ✗     |
| Approve case decision  | ✗       | ✓      | ✓       | ✓    | ✗       | ✗     |
| Approve SAR filing     | ✗       | ✗      | ✗       | ✓    | ✗       | ✗     |
| Configure scenarios    | ✗       | ✗      | ✓       | ✓    | ✗       | ✗     |
| Manage users           | ✗       | ✗      | ✗       | ✗    | ✗       | ✓     |
| View audit trail       | ✗       | ✗      | ✓       | ✓    | ✓       | ✓     |
| Terminate relationship | ✗       | ✗      | ✗       | ✓    | ✗       | ✗     |

### 8.4 SYSTEM SETTINGS

#### 8.4.1 Performance Settings

```
{
  performance: {
    batch_processing: {
      max_batch_size: 1000
      concurrent_batches: 5
      retry_attempts: 3
      timeout_seconds: 300
    }

    caching: {
      customer_cache_ttl_seconds: 3600
      screening_cache_ttl_seconds: 86400
      configuration_cache_ttl_seconds: 300
    }

    rate_limiting: {
      api_requests_per_minute: 1000
      screening_requests_per_minute: 100
      report_generation_concurrent: 10
    }
  }
}
```

#### 8.4.2 Integration Settings

```
{
  integrations: {
    screening_provider: {
      provider: "opensanctions" | "dow_jones" | "refinitiv"
      endpoint: string
      api_key: string (encrypted)
      timeout_seconds: 10
      retry_enabled: boolean
      fallback_provider: string (nullable)
    }

    ai_service: {
      provider: "openai" | "anthropic" | "azure"
      endpoint: string
      api_key: string (encrypted)
      model: string
      timeout_seconds: 30
    }

    email_service: {
      provider: "sendgrid" | "ses" | "smtp"
      config: object
      from_email: string
      from_name: string
    }

    document_storage: {
      provider: "s3" | "azure_blob" | "gcs"
      bucket: string
      region: string
      credentials: object (encrypted)
    }
  }
}
```

#### 8.4.3 Security Settings

```
{
  security: {
    session: {
      timeout_minutes: 30
      max_concurrent_sessions: 3
      require_mfa: boolean
    }

    password_policy: {
      min_length: 12
      require_uppercase: boolean
      require_lowercase: boolean
      require_numbers: boolean
      require_special_chars: boolean
      expiry_days: 90
      history_count: 5
    }

    audit_logging: {
      log_all_access: boolean
      log_data_changes: boolean
      log_configuration_changes: boolean
      retention_days: 2555 (7 years)
    }

    encryption: {
      data_at_rest: "aes_256"
      data_in_transit: "tls_1_3"
      key_rotation_days: 90
    }

    ip_whitelist: {
      enabled: boolean
      allowed_ips: string[]
    }
  }
}
```

#### 8.4.4 Notification Settings

```
{
  notifications: {
    email_notifications: {
      enabled: boolean
      recipients: {
        critical_alerts: string[]
        sla_breaches: string[]
        sar_filings: string[]
        system_errors: string[]
      }
    }

    in_app_notifications: {
      enabled: boolean
      notification_types: [
        "case_assigned",
        "case_escalated",
        "alert_assigned",
        "sla_approaching",
        "approval_required",
        "comment_mention"
      ]
    }

    sms_notifications: {
      enabled: boolean
      critical_only: boolean
      recipients: string[]
    }
  }
}
```

### 8.5 CUSTOMER SEGMENT CONFIGURATION

#### 8.5.1 Segment Definition

```
{
  customer_segments: [
    {
      segment_id: string
      name: string
      description: string

      criteria: {
        customer_types: ["individual", "legal_entity"]
        risk_levels: ["low", "medium", "high"]
        jurisdictions: string[]
        business_sectors: string[]
        products: string[]
        transaction_volume_min: number
        transaction_volume_max: number
      }

      overrides: {
        transaction_scenario_thresholds: {
          high_value_single: number
          high_value_cumulative: number
          ...
        }

        screening_threshold: number

        monitoring_intensity: "standard" | "enhanced" | "intensive"

        review_frequency_days: integer
      }
    }
  ]
}
```

**Example Segments:**

- High-net-worth individuals
- MSB customers
- Non-profit organizations
- E-commerce merchants
- International trade companies
- Real estate developers

### 8.6 CONFIGURATION MANAGEMENT

#### 8.6.1 Configuration Changes

**Change Tracking:**

```
{
  configuration_changes: [
    {
      change_id: string
      changed_at: datetime
      changed_by_user_id: string
      change_type: "create" | "update" | "delete"

      configuration_section: string (e.g., "cra_scenarios", "transaction_thresholds")

      before_state: object
      after_state: object

      change_reason: string
      approval_required: boolean
      approved_by_user_id: string (if applicable)
      approved_at: datetime
    }
  ]
}
```

**Approval Workflow:**

```
Critical changes require approval:
  - Risk threshold changes
  - Scenario enable/disable
  - Integration credentials
  - User role permissions
  - Security settings

Approval levels:
  - Compliance Manager: Scenario configurations
  - MLRO: Risk thresholds, critical settings
  - System Admin: Integration and security settings
```

#### 8.6.2 Configuration Versioning

**Version Control:**

```
{
  configuration_versions: [
    {
      version_id: string
      version_number: string (e.g., "v1.2.3")
      created_at: datetime
      created_by: string

      configuration_snapshot: object (full config state)

      changes_summary: string

      rollback_available: boolean
      active: boolean
    }
  ]
}
```

**Rollback Capability:**

- Restore previous configuration version
- Preview changes before rollback
- Approval required for rollback
- Audit trail of rollback events

#### 8.6.3 Configuration Export/Import

**Export Format:**

```json
{
  "export_metadata": {
    "organization_id": "org_123",
    "exported_at": "2024-01-15T10:30:00Z",
    "exported_by": "user_456",
    "version": "1.0"
  },
  "configuration": {
    "cra_config": {...},
    "transaction_scenarios": [...],
    "screening_config": {...},
    "reference_lists": {...}
  }
}
```

**Use Cases:**

- Backup configuration
- Migrate configuration across environments
- Share configuration across organizations (with sanitization)
- Disaster recovery

### 8.7 DEFAULT CONFIGURATIONS

#### 8.7.1 Conservative Defaults

**System Defaults (Pre-configured):**

```
{
  default_config: {
    cra: {
      component_weights: {customer: 0.30, geography: 0.20, product: 0.30, channel: 0.20}
      risk_thresholds: {low_medium: 1.7, medium_high: 2.4}
      product_aggregation: "max"
      controls_max_reduction: 0.70
    }

    transaction_monitoring: {
      high_value_single: 50000
      high_value_cumulative: 100000
      dormancy_days: 90
      structuring_threshold: 10000
      velocity_multiplier: 3.0
    }

    screening: {
      sanctions_threshold: 0.6
      pep_threshold: 0.6
      rescreening_high_risk_days: 90
    }

    case_management: {
      sla_critical_hours: 24
      sla_high_hours: 72
      sla_medium_days: 7
      sla_low_days: 30
    }
  }
}
```

**Jurisdiction-Specific Defaults:**

- UAE: Tailored thresholds based on CBUAE regulations
- UK: FCA-compliant settings
- US: OFAC and FinCEN requirements
- EU: AMLD5/AMLD6 compliance

### 8.8 CONFIGURATION UI

#### 8.8.1 Configuration Pages

**Settings Navigation:**

```
/settings
  /settings/organization
  /settings/cra-scenarios
  /settings/transaction-scenarios
  /settings/inherent-risk
  /settings/screening-lists
  /settings/case-management
  /settings/alerts
  /settings/reporting
  /settings/users-roles
  /settings/integrations
  /settings/security
  /settings/notifications
```

#### 8.8.2 Configuration Features

**User Interface Requirements:**

- Form validation (client and server-side)
- Preview changes before saving
- Confirmation dialog for critical changes
- Rollback option for recent changes
- Search and filter configuration items
- Bulk update capabilities
- Import/export functionality
- Change history view

### 8.9 PERFORMANCE REQUIREMENTS

- **Configuration Load:** < 500ms on application start
- **Configuration Update:** < 1 second
- **Configuration Cache Refresh:** < 100ms
- **Settings Page Load:** < 2 seconds
- **Bulk Configuration Import:** < 30 seconds (1000+ settings)

---

## 9. API SPECIFICATIONS

### 9.1 OVERVIEW

The AML system exposes APIs for all major operations including risk assessment, screening, transaction monitoring, case management, and reporting. APIs follow RESTful principles with type-safe contracts.

**API Architecture:**

- Type-safe RPC-style endpoints
- Input validation with schemas
- Standardized error responses
- Authentication and authorization
- Rate limiting
- Audit logging

### 9.2 API ENDPOINT CATEGORIES

#### 9.2.1 Customer Risk Assessment APIs

**Calculate Inherent Risk**

```
Endpoint: /api/cra/calculateCustomerInherent
Method: POST
Request: {
  customerId: string
  input: CustomerRiskInput
}
Response: {
  customerId: string
  inherentRisk: {
    score: number
    level: string
    components: ComponentBreakdown
  }
  scenarios: ScenarioResult[]
}
```

**Calculate Residual Risk**

```
Endpoint: /api/cra/calculateCustomerResidual
Method: POST
Request: {
  customerId: string
  inherentRisk: number
  controls: ControlInput[]
}
Response: {
  customerId: string
  residualRisk: {
    score: number
    level: string
    controlEffectiveness: number
  }
}
```

**Reassess Customer**

```
Endpoint: /api/cra/reassessCustomer
Method: POST
Request: {
  customerId: string
  reason: string
}
Response: {
  assessmentId: string
  customerId: string
  inherentRisk: RiskResult
  residualRisk: RiskResult
  finalRisk: RiskResult
  eddRequired: boolean
}
```

**Bulk Reassess Customers**

```
Endpoint: /api/cra/bulkReassessCustomers
Method: POST
Request: {
  customerIds: string[]
  reason: string
}
Response: {
  jobId: string
  totalCount: number
  estimatedCompletionTime: datetime
}
```

**Get Customer Risks**

```
Endpoint: /api/cra/getCustomerRisks
Method: GET
Query Parameters: {
  riskLevel?: string[]
  eddRequired?: boolean
  page?: number
  limit?: number
}
Response: {
  items: CustomerRisk[]
  total: number
  page: number
  limit: number
}
```

#### 9.2.2 Sanctions Screening APIs

**Unified Screening**

```
Endpoint: /api/sanctions/unifiedScreening
Method: POST
Request: {
  entityType: "person" | "organization"
  name: string
  dateOfBirth?: date
  nationality?: string[]
  datasets: string[]
  threshold: number
}
Response: {
  screeningId: string
  screeningDate: datetime
  matches: ScreeningMatch[]
  summary: {
    totalMatches: number
    highestScore: number
    hasSanctionsMatch: boolean
    hasPepMatch: boolean
  }
}
```

**Comprehensive Screening (with UBOs)**

```
Endpoint: /api/sanctions/comprehensiveScreening
Method: POST
Request: {
  customerId: string
  includeUbos: boolean
  includeDirectors: boolean
  includeShareholders: boolean
}
Response: {
  screeningId: string
  entityMatches: ScreeningMatch[]
  directorMatches: ScreeningMatch[]
  uboMatches: ScreeningMatch[]
  highestOverallScore: number
  hasMatch: boolean
}
```

**Get Screening History**

```
Endpoint: /api/sanctions/getScreeningHistory
Method: GET
Query Parameters: {
  customerId: string
  fromDate?: datetime
  toDate?: datetime
}
Response: {
  screenings: ScreeningEvent[]
  totalCount: number
}
```

#### 9.2.3 Transaction Monitoring APIs

**Monitor Transaction**

```
Endpoint: /api/transactions/monitor
Method: POST
Request: {
  transactionId: string
  customerId: string
  amount: number
  currency: string
  transactionType: string
  paymentType: string
  destinationCountry?: string
}
Response: {
  transactionId: string
  riskScore: number
  riskLevel: string
  triggeredScenarios: ScenarioTrigger[]
  alertsGenerated: Alert[]
}
```

**Get Transaction Alerts**

```
Endpoint: /api/transactions/getAlerts
Method: GET
Query Parameters: {
  transactionId?: string
  customerId?: string
  severity?: string[]
  status?: string[]
}
Response: {
  alerts: TransactionAlert[]
  total: number
}
```

#### 9.2.4 Case Management APIs

**Create Case**

```
Endpoint: /api/cases/create
Method: POST
Request: {
  customerId: string
  transactionId?: string
  trigger: CaseTrigger
  source: CaseSource
  shortDescription: string
  longDescription?: string
  priority?: CasePriority
  tags?: string[]
}
Response: {
  caseId: string
  publicId: string
  createdAt: datetime
  status: CaseStatus
  dueAt: datetime
}
```

**Update Case**

```
Endpoint: /api/cases/update
Method: PATCH
Request: {
  caseId: string
  updates: {
    status?: CaseStatus
    priority?: CasePriority
    assignedTo?: string
    tags?: string[]
    longDescription?: string
  }
}
Response: {
  caseId: string
  updatedAt: datetime
  ...updatedFields
}
```

**Get Case by ID**

```
Endpoint: /api/cases/getById
Method: GET
Query Parameters: {
  caseId: string
}
Response: {
  case: CaseDetail
  alerts: CaseAlert[]
  notes: CaseNote[]
  tasks: CaseTask[]
  attachments: CaseAttachment[]
  timeline: TimelineEvent[]
  decisions: CaseDecision[]
}
```

**List Cases**

```
Endpoint: /api/cases/list
Method: GET
Query Parameters: {
  status?: CaseStatus[]
  priority?: CasePriority[]
  trigger?: CaseTrigger[]
  assignedTo?: string
  createdFrom?: datetime
  createdTo?: datetime
  hasOverdueSla?: boolean
  page?: number
  limit?: number
  sortBy?: string
  sortOrder?: "asc" | "desc"
}
Response: {
  items: Case[]
  total: number
  page: number
  limit: number
}
```

**Add Case Note**

```
Endpoint: /api/cases/addNote
Method: POST
Request: {
  caseId: string
  content: string
  noteType: NoteType
  isInternal: boolean
}
Response: {
  noteId: string
  createdAt: datetime
}
```

**Add Case Task**

```
Endpoint: /api/cases/addTask
Method: POST
Request: {
  caseId: string
  title: string
  description?: string
  assignedTo?: string
  dueAt?: datetime
}
Response: {
  taskId: string
  createdAt: datetime
}
```

**Decide Case**

```
Endpoint: /api/cases/decideCase
Method: POST
Request: {
  caseId: string
  decision: CaseDecision
  decisionType: DecisionType
  rationale: string
  outcomes?: CaseOutcome[]
}
Response: {
  caseId: string
  decisionId: string
  decidedAt: datetime
}
```

**Close Case**

```
Endpoint: /api/cases/closeCase
Method: POST
Request: {
  caseId: string
  closureReason: string
  outcomes: CaseOutcome[]
}
Response: {
  caseId: string
  closedAt: datetime
  finalStatus: CaseStatus
}
```

**Get Case Statistics**

```
Endpoint: /api/cases/stats
Method: GET
Query Parameters: {
  fromDate?: datetime
  toDate?: datetime
  groupBy?: "status" | "priority" | "trigger"
}
Response: {
  totalCases: number
  byStatus: Record<CaseStatus, number>
  byPriority: Record<CasePriority, number>
  byTrigger: Record<CaseTrigger, number>
  avgResolutionTime: number
  slaComplianceRate: number
}
```

#### 9.2.5 Alert Management APIs

**Get Alerts**

```
Endpoint: /api/alerts/list
Method: GET
Query Parameters: {
  severity?: AlertSeverity[]
  alertType?: AlertType[]
  status?: AlertStatus[]
  customerId?: string
  assignedTo?: string
  resolved?: boolean
  page?: number
  limit?: number
}
Response: {
  items: Alert[]
  total: number
  page: number
}
```

**Resolve Alert**

```
Endpoint: /api/alerts/resolve
Method: POST
Request: {
  alertId: string
  outcome: ResolutionOutcome
  notes: string
  caseId?: string
}
Response: {
  alertId: string
  resolvedAt: datetime
  outcome: ResolutionOutcome
}
```

#### 9.2.6 Reporting APIs

**Generate SAR**

```
Endpoint: /api/reports/generateSar
Method: POST
Request: {
  caseId: string
  subjects: SubjectInfo[]
  transactions: TransactionInfo[]
  reportingPeriod: {from: date, to: date}
}
Response: {
  sarId: string
  reportCode: "SAR"
  riskLevel: string
  riskScore: number
  generatedXml: string (goAML format)
  narrative: string (AI-generated)
}
```

**Generate ECDD Report**

```
Endpoint: /api/reports/generateEcdd
Method: POST
Request: {
  customerId: string
  includeTransactionHistory: boolean
  includeScreeningHistory: boolean
}
Response: {
  reportId: string
  customerId: string
  reportDate: datetime
  ecddData: ECDDReport
  pdfUrl: string
}
```

**Export Report**

```
Endpoint: /api/reports/export
Method: POST
Request: {
  reportId: string
  format: "pdf" | "xml" | "json" | "excel"
}
Response: {
  exportId: string
  downloadUrl: string
  expiresAt: datetime
}
```

### 9.3 API REQUEST/RESPONSE PATTERNS

#### 9.3.1 Standard Request Format

```
{
  // Business data
  ...requestFields

  // Optional metadata
  metadata?: {
    requestId?: string (client-generated trace ID)
    timestamp?: datetime
    source?: string (calling system identifier)
  }
}
```

#### 9.3.2 Standard Response Format

**Success Response:**

```
{
  success: true
  data: {
    ...responseFields
  }
  metadata: {
    requestId: string
    timestamp: datetime
    processingTime: number (ms)
  }
}
```

**Error Response:**

```
{
  success: false
  error: {
    code: string (e.g., "VALIDATION_ERROR", "NOT_FOUND")
    message: string (human-readable)
    details?: object (additional context)
    field?: string (for validation errors)
  }
  metadata: {
    requestId: string
    timestamp: datetime
  }
}
```

#### 9.3.3 Pagination Pattern

**Request:**

```
{
  page: number (1-indexed)
  limit: number (default: 50, max: 100)
  sortBy?: string
  sortOrder?: "asc" | "desc"
}
```

**Response:**

```
{
  items: T[]
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
    hasNextPage: boolean
    hasPreviousPage: boolean
  }
}
```

### 9.4 ERROR CODES

| Error Code              | HTTP Status | Description                             |
| ----------------------- | ----------- | --------------------------------------- |
| VALIDATION_ERROR        | 400         | Request validation failed               |
| AUTHENTICATION_REQUIRED | 401         | Authentication missing or invalid       |
| AUTHORIZATION_FAILED    | 403         | Insufficient permissions                |
| NOT_FOUND               | 404         | Resource not found                      |
| CONFLICT                | 409         | Resource conflict (e.g., duplicate)     |
| RATE_LIMIT_EXCEEDED     | 429         | Too many requests                       |
| INTERNAL_ERROR          | 500         | Server error                            |
| SERVICE_UNAVAILABLE     | 503         | Temporary service unavailable           |
| TIMEOUT                 | 504         | Request timeout                         |
| EXTERNAL_SERVICE_ERROR  | 502         | External service (screening, AI) failed |

### 9.5 AUTHENTICATION & AUTHORIZATION

#### 9.5.1 Authentication Methods

**API Key Authentication:**

```
Headers: {
  "X-API-Key": "your_api_key"
  "X-Organization-Id": "org_id"
}
```

**OAuth 2.0 (Bearer Token):**

```
Headers: {
  "Authorization": "Bearer {access_token}"
  "X-Organization-Id": "org_id"
}
```

#### 9.5.2 Authorization

**Permission Checks:**

- User role determines accessible endpoints
- Organization context enforced (multi-tenant)
- Resource-level permissions (e.g., assigned cases only)
- Audit trail for all API access

### 9.6 RATE LIMITING

**Rate Limits by Endpoint Category:**
| Category | Requests per Minute | Burst Limit |
|----------|-------------------|-------------|
| Read Operations | 1000 | 100 |
| Write Operations | 500 | 50 |
| Screening | 100 | 20 |
| Reporting | 50 | 10 |
| Bulk Operations | 10 | 2 |

**Rate Limit Headers:**

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1704067200 (Unix timestamp)
```

### 9.7 WEBHOOKS

#### 9.7.1 Webhook Events

**Available Events:**

- `case.created`
- `case.status_changed`
- `case.assigned`
- `alert.generated`
- `screening.match_found`
- `risk_assessment.completed`
- `sar.submitted`

**Webhook Payload:**

```
{
  event: string
  eventId: string
  timestamp: datetime
  organizationId: string
  data: {
    ...eventSpecificData
  }
}
```

#### 9.7.2 Webhook Configuration

```
{
  webhookUrl: string
  events: string[]
  secret: string (for signature verification)
  enabled: boolean
  retryPolicy: {
    maxAttempts: number
    backoffSeconds: number
  }
}
```

### 9.8 API VERSIONING

**Version Strategy:**

- URL-based versioning: `/api/v1/...`
- Current version: v1
- Backward compatibility maintained for 12 months
- Deprecation notices provided 6 months in advance

### 9.9 API PERFORMANCE

**Performance Targets:**

- p50: < 200ms
- p95: < 1000ms
- p99: < 3000ms
- Availability: 99.9%
- Error Rate: < 0.1%

---

## 10. DATABASE SCHEMA

### 10.1 OVERVIEW

The database schema supports all AML operations with proper normalization, referential integrity, and audit trails. Design emphasizes data integrity, query performance, and regulatory compliance.

**Database Requirements:**

- ACID compliance
- JSON/JSONB field support
- Full-text search capabilities
- Transaction support
- Referential integrity
- Index optimization

### 10.2 CORE ENTITIES

#### 10.2.1 Customer Entity

```
Table: Customer
Primary Key: id (string/uuid)

Fields:
- id: string (unique)
- organizationId: string (foreign key → Organization)
- customerType: enum ("natural_person", "legal_entity")
- fullName: string
- dateOfBirth: date (nullable, for natural persons)
- nationality: string[] (ISO country codes)
- residenceCountry: string
- incorporationCountry: string (nullable, for legal entities)
- registrationType: string (nullable)
- businessSector: string (nullable)
- onboardingChannel: string
- onboardingDate: datetime
- productsServices: string[]
- expectedMonthlyVolume: decimal (nullable)
- riskScore: integer (nullable)
- riskLevel: string (nullable, enum: low/medium/high)
- eddRequired: boolean
- kycExpired: boolean
- kycExpiryDate: date (nullable)
- status: string (enum: active, suspended, closed)
- createdAt: datetime
- updatedAt: datetime

Indexes:
- PRIMARY KEY (id)
- INDEX (organizationId)
- INDEX (riskLevel)
- INDEX (onboardingDate)
- INDEX (status)
- FULLTEXT INDEX (fullName)
```

#### 10.2.2 Party Entity (Related Parties)

```
Table: Party
Primary Key: id (string/uuid)

Fields:
- id: string
- customerId: string (foreign key → Customer)
- partyType: enum ("director", "shareholder", "ubo", "authorized_signatory")
- fullName: string
- dateOfBirth: date (nullable)
- nationality: string[]
- ownershipPercentage: decimal (nullable)
- isPep: boolean
- pepType: string (nullable)
- sanctionsStatus: string (nullable)
- createdAt: datetime
- updatedAt: datetime

Indexes:
- PRIMARY KEY (id)
- INDEX (customerId)
- INDEX (partyType)
- INDEX (isPep)
```

#### 10.2.3 Transaction Entity

```
Table: Transaction
Primary Key: id (string/uuid)

Fields:
- id: string
- organizationId: string
- customerId: string (foreign key → Customer)
- transactionDate: datetime
- transactionType: enum
- paymentType: enum
- amount: decimal
- currency: string (ISO 4217)
- status: enum (pending, completed, rejected, cancelled)
- isThirdPartyPayment: boolean (nullable)
- originCountry: string (nullable)
- destinationCountry: string (nullable)
- beneficiaryName: string (nullable)
- senderName: string (nullable)
- purpose: string (nullable)
- riskLevel: string (nullable)
- riskScore: integer (nullable)
- createdAt: datetime
- updatedAt: datetime

Indexes:
- PRIMARY KEY (id)
- INDEX (organizationId)
- INDEX (customerId)
- INDEX (transactionDate)
- INDEX (riskLevel)
- INDEX (amount)
- INDEX (status)
```

#### 10.2.4 Case Entity

```
Table: Case
Primary Key: id (string/uuid)

Fields:
- id: string
- publicId: string (unique, human-readable)
- organizationId: string
- customerId: string (foreign key → Customer)
- transactionId: string (nullable, foreign key → Transaction)
- trigger: enum (sanction, pep, transaction_risk, etc.)
- source: enum (screening, transaction_monitoring, manual, etc.)
- status: enum (open, investigating, under_review, etc.)
- priority: enum (low, medium, high, critical)
- shortDescription: string
- longDescription: text (nullable)
- riskScore: integer (nullable)
- tags: string[]
- dueAt: datetime
- closedAt: datetime (nullable)
- createdAt: datetime
- updatedAt: datetime
- createdByUserId: string
- assignedToUserId: string (nullable)

Indexes:
- PRIMARY KEY (id)
- UNIQUE INDEX (publicId)
- INDEX (organizationId)
- INDEX (customerId)
- INDEX (status)
- INDEX (priority)
- INDEX (trigger)
- INDEX (assignedToUserId)
- INDEX (dueAt)
- INDEX (createdAt)
```

#### 10.2.5 Alert Entity

```
Table: Alert
Primary Key: id (string/uuid)

Fields:
- id: string
- organizationId: string
- alertType: enum
- severity: enum (low, medium, high, critical)
- status: enum (generated, assigned, under_review, resolved)
- customerId: string (foreign key → Customer)
- transactionId: string (nullable)
- caseId: string (nullable, foreign key → Case)
- sourceSystem: string
- shortDescription: string
- longDescription: text (nullable)
- score: decimal (nullable)
- occurrenceCount: integer (default: 1)
- resolved: boolean (default: false)
- resolvedAt: datetime (nullable)
- resolvedByUserId: string (nullable)
- resolutionOutcome: string (nullable)
- resolutionNotes: text (nullable)
- metadata: jsonb
- createdAt: datetime
- updatedAt: datetime
- firstOccurrenceAt: datetime
- lastOccurrenceAt: datetime
- assignedToUserId: string (nullable)
- assignedAt: datetime (nullable)

Indexes:
- PRIMARY KEY (id)
- INDEX (organizationId)
- INDEX (customerId)
- INDEX (severity)
- INDEX (status)
- INDEX (resolved)
- INDEX (assignedToUserId)
- INDEX (createdAt)
```

#### 10.2.6 ScreeningEvent Entity

```
Table: ScreeningEvent
Primary Key: id (string/uuid)

Fields:
- id: string
- organizationId: string
- customerId: string (nullable)
- subjectType: enum (customer, party, transaction_party)
- subjectName: string
- entityType: enum (person, organization)
- provider: string
- datasets: string[]
- topics: string[]
- algorithm: string (nullable)
- threshold: decimal
- input: jsonb
- result: jsonb
- matches: jsonb
- highestScore: decimal (nullable)
- hasSanctionsMatch: boolean
- hasPepMatch: boolean
- createdAt: datetime

Indexes:
- PRIMARY KEY (id)
- INDEX (organizationId)
- INDEX (customerId)
- INDEX (hasSanctionsMatch)
- INDEX (hasPepMatch)
- INDEX (createdAt)
```

#### 10.2.7 CaseNote Entity

```
Table: CaseNote
Primary Key: id (string/uuid)

Fields:
- id: string
- caseId: string (foreign key → Case)
- content: text
- noteType: enum (investigation, communication, decision, general)
- isInternal: boolean
- createdByUserId: string
- createdAt: datetime
- updatedAt: datetime

Indexes:
- PRIMARY KEY (id)
- INDEX (caseId)
- INDEX (createdAt)
```

#### 10.2.8 CaseTask Entity

```
Table: CaseTask
Primary Key: id (string/uuid)

Fields:
- id: string
- caseId: string (foreign key → Case)
- title: string
- description: text (nullable)
- status: enum (open, in_progress, completed, cancelled)
- assignedToUserId: string (nullable)
- dueAt: datetime (nullable)
- completedAt: datetime (nullable)
- createdAt: datetime
- updatedAt: datetime

Indexes:
- PRIMARY KEY (id)
- INDEX (caseId)
- INDEX (status)
- INDEX (assignedToUserId)
- INDEX (dueAt)
```

### 10.3 AUDIT & HISTORY TABLES

#### 10.3.1 AuditLog Entity

```
Table: AuditLog
Primary Key: id (string/uuid)

Fields:
- id: string
- organizationId: string
- userId: string (nullable, system events have null)
- entityType: string (e.g., "Customer", "Case", "Transaction")
- entityId: string
- action: string (e.g., "create", "update", "delete", "read")
- changes: jsonb (before/after state)
- ipAddress: string (nullable)
- userAgent: string (nullable)
- timestamp: datetime

Indexes:
- PRIMARY KEY (id)
- INDEX (organizationId)
- INDEX (userId)
- INDEX (entityType, entityId)
- INDEX (timestamp)
```

#### 10.3.2 CustomerRiskHistory Entity

```
Table: CustomerRiskHistory
Primary Key: id (string/uuid)

Fields:
- id: string
- customerId: string (foreign key → Customer)
- assessmentDate: datetime
- assessmentType: enum (initial, periodic, event_triggered)
- inherentScore: decimal
- residualScore: decimal
- finalScore: decimal
- riskLevel: string
- scenarios: jsonb
- controls: jsonb
- assessedByUserId: string (nullable)
- createdAt: datetime

Indexes:
- PRIMARY KEY (id)
- INDEX (customerId)
- INDEX (assessmentDate)
- INDEX (riskLevel)
```

### 10.4 REFERENCE DATA TABLES

#### 10.4.1 Organization Entity

```
Table: Organization
Primary Key: id (string/uuid)

Fields:
- id: string
- name: string
- regulatoryJurisdiction: string
- licenseNumber: string (nullable)
- riskConfig: jsonb (all configuration)
- settings: jsonb
- createdAt: datetime
- updatedAt: datetime

Indexes:
- PRIMARY KEY (id)
- UNIQUE INDEX (licenseNumber)
```

#### 10.4.2 User Entity

```
Table: User
Primary Key: id (string/uuid)

Fields:
- id: string
- organizationId: string (foreign key → Organization)
- email: string
- fullName: string
- role: string
- permissions: string[]
- isActive: boolean
- lastLoginAt: datetime (nullable)
- createdAt: datetime
- updatedAt: datetime

Indexes:
- PRIMARY KEY (id)
- UNIQUE INDEX (email, organizationId)
- INDEX (organizationId)
- INDEX (role)
```

### 10.5 DATA RELATIONSHIPS

**Entity Relationship Diagram (Key Relationships):**

```
Organization 1──────── * Customer
Customer 1──────── * Party
Customer 1──────── * Transaction
Customer 1──────── * Case
Customer 1──────── * Alert
Customer 1──────── * ScreeningEvent
Customer 1──────── * CustomerRiskHistory
Case 1──────── * CaseNote
Case 1──────── * CaseTask
Case 1──────── * Alert (linked)
Transaction 1──────── * Alert
User 1──────── * Case (assigned)
User 1──────── * Alert (assigned)
```

### 10.6 DATA RETENTION & ARCHIVAL

**Retention Policies:**

- Customers: Permanent (7+ years after relationship end)
- Transactions: 7 years minimum
- Cases: 7-10 years (SAR-related: 10 years)
- Alerts: 7 years
- Screening Events: Permanent
- Audit Logs: 7 years minimum
- Risk History: Permanent

**Archival Strategy:**

- Active data: Primary database
- Data > 2 years old: Move to warm storage
- Data > 7 years old: Move to cold storage (archived)
- Maintain query capability across all tiers

### 10.7 PERFORMANCE CONSIDERATIONS

**Database Optimization:**

- Proper indexing on frequently queried fields
- Partitioning for large tables (by date, organizationId)
- JSONB indexes for metadata searches
- Connection pooling
- Query optimization
- Read replicas for reporting
- Caching layer for reference data

---

## 11. INTEGRATION & ARCHITECTURE

### 11.1 SYSTEM ARCHITECTURE

#### 11.1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Web Client  │  │  Mobile App  │  │  API Clients │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
┌─────────────────────────────┼─────────────────────────────────────┐
│                       API GATEWAY LAYER                            │
│  ┌────────────────────────────────────────────────────────┐      │
│  │  Authentication │ Authorization │ Rate Limiting │ Logs │      │
│  └────────────────────────────────────────────────────────┘      │
└────────────────────────────┬───────────────────────────────────────┘
                             │
┌─────────────────────────────┼─────────────────────────────────────┐
│                      APPLICATION LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Risk Engine  │  │  Screening   │  │ Transaction  │           │
│  │   (CRA)      │  │   Service    │  │  Monitoring  │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
│         │                  │                  │                    │
│  ┌──────┴───────────┬──────┴─────────┬───────┴────────┐         │
│  │   Case Mgmt      │  Alert Mgmt    │   Reporting    │         │
│  └──────────────────┴────────────────┴────────────────┘         │
└────────────────────────────┬───────────────────────────────────────┘
                             │
┌─────────────────────────────┼─────────────────────────────────────┐
│                        DATA LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  PostgreSQL  │  │    Redis     │  │  File Store  │           │
│  │   (Primary)  │  │   (Cache)    │  │ (Documents)  │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└────────────────────────────────────────────────────────────────────┘
                             │
┌─────────────────────────────┼─────────────────────────────────────┐
│                    EXTERNAL SERVICES                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Sanctions DB │  │  AI Service  │  │    Email     │           │
│  │  (Yente API) │  │  (Narrative) │  │   Service    │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└────────────────────────────────────────────────────────────────────┘
```

#### 11.1.2 Component Architecture

**Layered Architecture:**

1. **Presentation Layer**

   - Web application (user interface)
   - Mobile applications
   - Third-party API consumers

2. **API Gateway**

   - Request routing
   - Authentication/authorization
   - Rate limiting
   - Request logging
   - Response caching

3. **Application Services**

   - Risk Assessment Service
   - Screening Service
   - Transaction Monitoring Service
   - Case Management Service
   - Alert Management Service
   - Reporting Service

4. **Data Access Layer**

   - Database abstraction
   - Query optimization
   - Connection pooling
   - Transaction management

5. **Integration Layer**
   - External API clients
   - Message queue handlers
   - Webhook processors
   - File processors

### 11.2 INTEGRATION PATTERNS

#### 11.2.1 Synchronous Integration

**REST API Integration:**

```
Client → API Gateway → Service → External API → Response
```

**Use Cases:**

- Real-time screening requests
- Customer risk calculation
- Case operations
- Alert management

**Characteristics:**

- Request-response pattern
- Timeout: 10-30 seconds
- Retry logic with exponential backoff
- Circuit breaker pattern

#### 11.2.2 Asynchronous Integration

**Message Queue Pattern:**

```
Service → Queue → Worker → Processing → Database
                    ↓
                 Notification
```

**Use Cases:**

- Bulk customer reassessment
- Periodic rescreening
- Report generation
- Batch transaction monitoring

**Characteristics:**

- Fire-and-forget
- Job tracking with status
- Error handling and retries
- Progress notifications

#### 11.2.3 Event-Driven Integration

**Event Bus Pattern:**

```
Event Source → Event Bus → Multiple Subscribers
```

**Events:**

- Customer risk changed
- Screening match found
- Case status changed
- Alert generated
- SAR filed

**Subscribers:**

- Case creation service
- Notification service
- Audit service
- Analytics service
- External systems (webhooks)

### 11.3 EXTERNAL SERVICE INTEGRATIONS

#### 11.3.1 Sanctions Screening Provider

**Integration Details:**

```
Service: OpenSanctions (Yente API)
Protocol: HTTPS REST API
Authentication: API Key
Format: JSON
Timeout: 10 seconds
Retry: 3 attempts with exponential backoff
Fallback: Cached lists (if provider unavailable)
```

**Request Flow:**

```
1. Normalize subject data
2. Build screening query
3. Send HTTP POST to provider
4. Parse response matches
5. Calculate enhanced scores
6. Store screening event
7. Return matches to caller
```

**Error Handling:**

- Network errors: Retry with backoff
- Timeout: Retry once, then fail gracefully
- Provider error: Log and alert operations
- Fallback: Use cached sanctions lists

#### 11.3.2 AI Service Integration

**Integration Details:**

```
Service: AI Provider (OpenAI, Anthropic, etc.)
Protocol: HTTPS REST API
Authentication: API Key / Bearer Token
Format: JSON
Timeout: 30 seconds
Retry: 2 attempts
```

**Use Cases:**

- SAR narrative generation
- Risk indicator detection
- Pattern analysis
- Document summarization

**Request Flow:**

```
1. Prepare context data (case, transactions, customer)
2. Build prompt with instructions
3. Send to AI API
4. Parse response
5. Human review and edit
6. Store generated content
```

#### 11.3.3 Email Service Integration

**Integration Details:**

```
Provider: SendGrid / AWS SES / SMTP
Protocol: HTTPS API or SMTP
Authentication: API Key or SMTP credentials
Format: JSON (API) or MIME (SMTP)
```

**Use Cases:**

- Alert notifications
- Case assignments
- SLA breach warnings
- Report distribution
- User notifications

#### 11.3.4 Document Storage Integration

**Integration Details:**

```
Provider: AWS S3 / Azure Blob / Google Cloud Storage
Protocol: HTTPS API
Authentication: IAM credentials / Access keys
Format: Binary
```

**Use Cases:**

- Case attachments
- Supporting documents
- Report PDFs
- Evidence files
- Backup storage

### 11.4 DATA FLOW DIAGRAMS

#### 11.4.1 Customer Onboarding Flow

```
┌──────────┐
│ Customer │
│  Submits │
│   Data   │
└────┬─────┘
     │
     ▼
┌────────────────┐
│   Validate     │
│  Customer Data │
└────┬───────────┘
     │
     ├──────────────────────┐
     │                      │
     ▼                      ▼
┌────────────┐      ┌──────────────┐
│  Sanctions │      │     CRA      │
│  Screening │      │  Assessment  │
└────┬───────┘      └──────┬───────┘
     │                     │
     ├─────────────────────┤
     │                     │
     ▼                     ▼
┌─────────────────────────────┐
│   Evaluate Risk & Matches   │
└────────┬────────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌────────┐
│ Block  │  │Approve │
│        │  │ (with  │
│        │  │  EDD)  │
└────────┘  └───┬────┘
                │
                ▼
         ┌──────────────┐
         │ Create Case  │
         │  (if needed) │
         └──────────────┘
```

#### 11.4.2 Transaction Monitoring Flow

```
┌─────────────┐
│ Transaction │
│   Created   │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  Enrich with     │
│  Customer Data   │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Evaluate All    │
│    Scenarios     │
└──────┬───────────┘
       │
       ├────────────┐
       │            │
   No Match    Scenario(s)
       │        Triggered
       ▼            │
  ┌────────┐       ▼
  │  Pass  │  ┌──────────┐
  └────────┘  │  Create  │
              │  Alert   │
              └────┬─────┘
                   │
              ┌────┴────┐
              │         │
         Severity   Severity
          Low/Med    High/Crit
              │         │
              ▼         ▼
        ┌─────────┐  ┌────────┐
        │  Queue  │  │ Create │
        │  Alert  │  │  Case  │
        └─────────┘  └────────┘
```

#### 11.4.3 SAR Filing Flow

```
┌──────────┐
│   Case   │
│ Complete │
└────┬─────┘
     │
     ▼
┌────────────────┐
│   Analyst      │
│   Recommends   │
│   SAR Filing   │
└────┬───────────┘
     │
     ▼
┌────────────────┐
│ Generate SAR   │
│  (with AI)     │
└────┬───────────┘
     │
     ▼
┌────────────────┐
│   Compliance   │
│    Manager     │
│    Reviews     │
└────┬───────────┘
     │
     ▼
┌────────────────┐
│      MLRO      │
│    Approves    │
└────┬───────────┘
     │
     ▼
┌────────────────┐
│  Generate      │
│  goAML XML     │
└────┬───────────┘
     │
     ▼
┌────────────────┐
│   Submit to    │
│  Regulatory    │
│   Authority    │
└────┬───────────┘
     │
     ▼
┌────────────────┐
│  Update Case   │
│  with SAR Ref  │
└────────────────┘
```

### 11.5 SCALABILITY ARCHITECTURE

#### 11.5.1 Horizontal Scaling

**Stateless Services:**

- API servers: Scale horizontally with load balancer
- Worker processes: Scale based on queue depth
- Background jobs: Distributed processing

**Database Scaling:**

- Read replicas for reporting queries
- Connection pooling
- Query optimization
- Partitioning by organization

**Caching Strategy:**

- Application-level caching (Redis)
- API response caching
- Configuration caching
- Reference data caching

#### 11.5.2 Performance Optimization

**Query Optimization:**

- Proper indexing
- Query result caching
- Pagination for large datasets
- Selective field loading

**API Optimization:**

- Response compression
- CDN for static assets
- API result caching
- Batch operations

**Background Processing:**

- Asynchronous job processing
- Queue-based workload distribution
- Priority-based job execution
- Resource pooling

### 11.6 RESILIENCE & FAULT TOLERANCE

#### 11.6.1 High Availability

**Component Redundancy:**

- Multiple API server instances
- Database replication (primary-replica)
- Message queue clustering
- Load balancer health checks

**Failover Strategy:**

- Automatic failover for database
- Graceful degradation for external services
- Circuit breaker pattern
- Retry logic with backoff

#### 11.6.2 Error Handling

**Error Recovery:**

```
1. Detect error
2. Log error details
3. Attempt automatic retry (if applicable)
4. Fallback to degraded service (if possible)
5. Alert operations team (if critical)
6. Return user-friendly error message
```

**Circuit Breaker:**

```
States: Closed → Open → Half-Open

Closed: Normal operation
  ↓ (failure threshold exceeded)
Open: Fail fast, don't call service
  ↓ (timeout period elapsed)
Half-Open: Try one request
  ↓ (success) → Closed
  ↓ (failure) → Open
```

### 11.7 MONITORING & OBSERVABILITY

#### 11.7.1 Logging

**Log Levels:**

- ERROR: Application errors, failures
- WARN: Potential issues, degraded performance
- INFO: Business events, state changes
- DEBUG: Detailed diagnostic information

**Structured Logging:**

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "service": "screening-service",
  "organizationId": "org_123",
  "userId": "user_456",
  "requestId": "req_789",
  "event": "screening_completed",
  "details": {
    "customerId": "cust_abc",
    "matchesFound": 3,
    "processingTime": 1250
  }
}
```

#### 11.7.2 Metrics

**Key Metrics:**

- API request rate (requests/second)
- API response time (p50, p95, p99)
- Error rate (%)
- Database query time
- Queue depth
- Job processing time
- External API latency
- Cache hit rate

**Business Metrics:**

- Cases created per day
- Alerts generated per day
- SARs filed per month
- Screening requests per hour
- Risk assessments completed
- SLA compliance rate

#### 11.7.3 Alerting

**Alert Triggers:**

- Error rate > threshold (e.g., 1%)
- Response time > threshold (e.g., 5s at p95)
- Queue depth > threshold
- External service unavailable
- Disk space low
- Database connection pool exhausted
- SLA breach imminent

**Alert Channels:**

- Email notifications
- SMS for critical alerts
- Incident management system integration
- Dashboard alerts

### 11.8 DEPLOYMENT ARCHITECTURE

#### 11.8.1 Environment Separation

**Environments:**

```
Development → Staging → Production

Development:
  - Feature development
  - Unit testing
  - Integration testing

Staging:
  - Pre-production testing
  - User acceptance testing
  - Performance testing

Production:
  - Live system
  - Real customer data
  - High availability
```

#### 11.8.2 Deployment Strategy

**Deployment Process:**

```
1. Code review and approval
2. Automated testing (unit, integration)
3. Build artifacts
4. Deploy to staging
5. Run smoke tests
6. Manual QA
7. Deploy to production (blue-green or canary)
8. Monitor metrics
9. Rollback if issues detected
```

**Blue-Green Deployment:**

```
Blue (Current) ← Traffic
Green (New) ← Deploy & Test
     ↓
Switch Traffic → Green
     ↓
Monitor Green
     ↓
If OK: Retire Blue
If Issues: Switch back to Blue
```

### 11.9 SECURITY ARCHITECTURE

#### 11.9.1 Defense in Depth

**Security Layers:**

1. **Network Security**

   - Firewall rules
   - VPC isolation
   - DDoS protection
   - IP whitelisting

2. **Application Security**

   - Input validation
   - Output encoding
   - SQL injection prevention
   - XSS prevention
   - CSRF protection

3. **Authentication & Authorization**

   - Multi-factor authentication
   - Role-based access control
   - Session management
   - Token-based authentication

4. **Data Security**

   - Encryption at rest (AES-256)
   - Encryption in transit (TLS 1.3)
   - Sensitive data masking
   - Key rotation

5. **Audit & Compliance**
   - Comprehensive audit logging
   - Access monitoring
   - Security event alerting
   - Compliance reporting

#### 11.9.2 Compliance Requirements

**Regulatory Compliance:**

- GDPR (data protection)
- PCI DSS (if handling payment data)
- SOC 2 (security controls)
- ISO 27001 (information security)
- Local AML regulations

**Data Protection:**

- Personally Identifiable Information (PII) protection
- Data minimization
- Right to erasure (with regulatory exceptions)
- Data breach notification procedures

---

## 12. NON-FUNCTIONAL REQUIREMENTS

### 12.1 PERFORMANCE REQUIREMENTS

#### 12.1.1 Response Time

**API Response Times:**
| Operation | Target (p50) | Target (p95) | Target (p99) |
|-----------|-------------|-------------|-------------|
| Customer risk calculation | 500ms | 1.5s | 2s |
| Sanctions screening | 1s | 3s | 5s |
| Transaction monitoring | 500ms | 1s | 2s |
| Case operations | 200ms | 500ms | 1s |
| Alert operations | 200ms | 500ms | 1s |
| Report generation | 5s | 20s | 30s |

**Page Load Times:**
| Page | Target |
|------|--------|
| Dashboard | < 2s |
| Case detail | < 1.5s |
| Customer profile | < 1.5s |
| Alert queue | < 2s |
| Reports list | < 2s |

#### 12.1.2 Throughput

**Transaction Processing:**

- 10,000+ transactions per hour
- 100+ concurrent risk assessments
- 50+ concurrent screenings
- 1,000+ API requests per minute

**Batch Operations:**

- Bulk customer reassessment: 100+ customers per batch
- Periodic rescreening: 1,000+ customers per hour
- Report generation: 10+ concurrent reports

#### 12.1.3 Scalability

**Vertical Scaling:**

- Support increased load by adding resources

**Horizontal Scaling:**

- Add more application server instances
- Distribute workload across instances
- Scale based on metrics (CPU, memory, queue depth)

**Growth Support:**

- 100,000+ customers per organization
- 1,000,000+ transactions per month
- 10,000+ cases per year
- 50,000+ alerts per year

### 12.2 AVAILABILITY REQUIREMENTS

**Uptime Target:** 99.9% (43.8 minutes downtime per month)

**Service Level Objectives:**
| Component | Availability | Max Downtime/Month |
|-----------|-------------|-------------------|
| API Services | 99.9% | 43.8 minutes |
| Database | 99.95% | 21.6 minutes |
| External Integrations | 99.5% | 3.6 hours |

**Maintenance Windows:**

- Scheduled maintenance: Monthly, 2-hour window
- Off-peak hours (2:00 AM - 4:00 AM local time)
- Advance notice: 7 days minimum

**Disaster Recovery:**

- RTO (Recovery Time Objective): 4 hours
- RPO (Recovery Point Objective): 1 hour
- Backup frequency: Daily (full), hourly (incremental)
- Backup retention: 30 days

### 12.3 SECURITY REQUIREMENTS

#### 12.3.1 Authentication

**Requirements:**

- Support multiple authentication methods
- Multi-factor authentication for privileged users
- Password complexity requirements
- Account lockout after failed attempts
- Session timeout (30 minutes inactivity)

#### 12.3.2 Authorization

**Requirements:**

- Role-based access control (RBAC)
- Principle of least privilege
- Separation of duties
- Multi-tenant data isolation
- Permission inheritance

#### 12.3.3 Data Protection

**Requirements:**

- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3 minimum)
- Sensitive data masking in logs
- Secure key management
- Regular key rotation (90 days)

#### 12.3.4 Audit & Compliance

**Requirements:**

- Comprehensive audit logging
- Tamper-evident logs
- Log retention: 7+ years
- User activity monitoring
- Security event alerting

### 12.4 USABILITY REQUIREMENTS

**User Experience:**

- Intuitive navigation
- Consistent UI patterns
- Responsive design (desktop, tablet, mobile)
- Accessibility compliance (WCAG 2.1 Level AA)
- Context-sensitive help
- Clear error messages
- Loading indicators for long operations

**Internationalization:**

- Multi-language support
- Locale-specific date/time formats
- Currency formatting
- Right-to-left language support

### 12.5 RELIABILITY REQUIREMENTS

**Error Handling:**

- Graceful degradation
- User-friendly error messages
- Automatic retry for transient errors
- Circuit breaker for external services
- Fallback mechanisms

**Data Integrity:**

- ACID transaction compliance
- Referential integrity enforcement
- Data validation at all entry points
- Backup verification
- Corruption detection

**Fault Tolerance:**

- No single point of failure
- Automatic failover
- Service redundancy
- Health monitoring
- Self-healing capabilities

### 12.6 MAINTAINABILITY REQUIREMENTS

**Code Quality:**

- Modular architecture
- Clear separation of concerns
- Comprehensive documentation
- Code comments for complex logic
- Consistent coding standards

**Testing:**

- Unit test coverage: > 80%
- Integration test coverage: > 70%
- End-to-end test coverage: Critical paths
- Performance testing
- Security testing

**Deployment:**

- Automated deployment pipeline
- Zero-downtime deployments
- Quick rollback capability
- Environment parity (dev/staging/prod)
- Configuration management

### 12.7 COMPLIANCE REQUIREMENTS

**Regulatory Compliance:**

- UAE CBUAE AML regulations
- FATF recommendations
- GDPR (where applicable)
- Local data residency requirements
- Audit trail requirements

**Industry Standards:**

- ISO 27001 (Information Security)
- SOC 2 Type II (Service Organization Controls)
- PCI DSS (if applicable)

**Documentation:**

- System documentation
- User manuals
- API documentation
- Operational runbooks
- Disaster recovery plans

### 12.8 CAPACITY REQUIREMENTS

**Storage:**

- Database: 1 TB initial, 500 GB growth per year
- File storage: 500 GB initial, 200 GB growth per year
- Backup storage: 3x primary storage
- Log storage: 100 GB per month

**Compute:**

- API servers: 4-8 vCPUs, 16-32 GB RAM per instance
- Database: 8-16 vCPUs, 64-128 GB RAM
- Background workers: 2-4 vCPUs, 8-16 GB RAM per worker

**Network:**

- Bandwidth: 1 Gbps minimum
- Latency: < 100ms for API calls
- External API calls: < 200ms average

### 12.9 COMPATIBILITY REQUIREMENTS

**Browser Support:**

- Chrome (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Edge (last 2 versions)

**Mobile Support:**

- iOS 14+
- Android 10+
- Responsive design for tablets

**API Compatibility:**

- REST API versioning
- Backward compatibility for 12 months
- Deprecation notices 6 months in advance

### 12.10 OPERATIONAL REQUIREMENTS

**Monitoring:**

- Real-time system health monitoring
- Performance metrics dashboard
- Business metrics dashboard
- Alert management
- Log aggregation

**Support:**

- 24/7 critical issue support
- Business hours standard support
- SLA-based response times
- Incident management process
- Knowledge base

**Backup & Recovery:**

- Automated daily backups
- Point-in-time recovery
- Backup verification
- Disaster recovery testing (quarterly)
- Backup retention: 30 days operational, 7 years compliance

---

## APPENDICES

### APPENDIX A: GLOSSARY

| Term              | Definition                                          |
| ----------------- | --------------------------------------------------- |
| **AML**           | Anti-Money Laundering                               |
| **CRA**           | Customer Risk Assessment                            |
| **SAR**           | Suspicious Activity Report                          |
| **STR**           | Suspicious Transaction Report                       |
| **PEP**           | Politically Exposed Person                          |
| **UBO**           | Ultimate Beneficial Owner                           |
| **EDD**           | Enhanced Due Diligence                              |
| **KYC**           | Know Your Customer                                  |
| **MLRO**          | Money Laundering Reporting Officer                  |
| **FATF**          | Financial Action Task Force                         |
| **OFAC**          | Office of Foreign Assets Control                    |
| **goAML**         | Global Anti-Money Laundering (XML format)           |
| **Inherent Risk** | Risk before applying controls                       |
| **Residual Risk** | Risk after applying controls                        |
| **Structuring**   | Breaking transactions to avoid reporting thresholds |
| **Layering**      | Complex transactions to obscure fund origin         |
| **Smurfing**      | Using multiple people to structure transactions     |

### APPENDIX B: ACRONYMS

- **API** - Application Programming Interface
- **CBUAE** - Central Bank of the United Arab Emirates
- **CCO** - Chief Compliance Officer
- **REST** - Representational State Transfer
- **RPC** - Remote Procedure Call
- **SLA** - Service Level Agreement
- **TLS** - Transport Layer Security
- **UUID** - Universally Unique Identifier
- **WCAG** - Web Content Accessibility Guidelines
- **XSS** - Cross-Site Scripting
- **CSRF** - Cross-Site Request Forgery

### APPENDIX C: REFERENCES

1. FATF Recommendations - International Standards on Combating Money Laundering
2. UAE AML Laws and Regulations - CBUAE AML Guidelines
3. goAML Implementation Guide - UNODC goAML Documentation
4. ISO 27001 - Information Security Management
5. GDPR - General Data Protection Regulation
6. WCAG 2.1 - Web Content Accessibility Guidelines

### APPENDIX D: DOCUMENT CHANGELOG

| Version | Date       | Author         | Changes                                                       |
| ------- | ---------- | -------------- | ------------------------------------------------------------- |
| 1.0     | 2025-11-13 | Technical Team | Initial TRD creation - Complete documentation of AML features |

---

**END OF DOCUMENT**

---

Total Pages: Comprehensive Technical Requirements Document
Document ID: TRD-AML-001
Classification: Internal - Confidential
