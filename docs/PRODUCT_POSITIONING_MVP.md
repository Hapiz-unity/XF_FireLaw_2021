# Product Positioning (MVP)

## Product Statement

This system provides a fact-based evidence chain for fire pump maintenance work by automatically capturing and preserving check-in records, manual inspection data, and machine-captured IoT snapshots at the time of maintenance, without performing compliance judgments or status interpretations.

## The Problem Today

Before this system, fire maintenance organizations face several challenges:

- **Evidence Fragmentation**: Maintenance records, inspection notes, and sensor data exist in separate systems or paper forms, making it difficult to establish a complete timeline of what occurred during maintenance.

- **Interpretation Ambiguity**: When incidents occur or audits are conducted, there is often uncertainty about what actually happened versus what was inferred or assumed after the fact.

- **Manual Documentation Burden**: Field technicians must manually record inspection results, which is time-consuming and prone to inconsistencies or omissions.

- **Lack of Temporal Binding**: It is difficult to prove that IoT sensor readings correspond to the exact moment when maintenance was performed, creating gaps in the evidence chain.

- **Post-Incident Reconstruction Difficulty**: After a fire incident, investigators and regulators need to understand what maintenance was performed and what the equipment state was, but existing records may be incomplete or unclear.

## What This System Changes

This system shifts from **conclusion-based reporting** to **fact-based evidence preservation**:

### Fact-Based Evidence

- **Temporal Binding**: Each work order automatically captures IoT sensor data (pressure, pump running state) at the exact moment of check-in, creating an immutable link between human action and machine state.

- **Neutral Presentation**: All data is presented as raw values without interpretation. A pressure reading of 0.65 MPa is shown as "0.65 MPa", not as "normal" or "within range".

- **Complete Evidence Chain**: The system preserves:
  - Who performed the check-in (via work order record)
  - When it occurred (timestamp)
  - Where it occurred (location with QR code)
  - What was inspected (manual inspection fields: pumphouse, endpoint, hydrant, linkage)
  - What the equipment state was (IoT snapshot: pressure, pump running)
  - What metadata applies (unit information, source attribution)

- **Machine-Captured vs Human-Reported Separation**: The system clearly distinguishes between:
  - **Manual Inspection Summary**: Human-reported status (ok/issue) for each inspection point
  - **IoT Evidence Record**: Machine-captured sensor data with source attribution

### No Conclusions, Only Facts

The system does not:
- Determine if a pressure reading is "good" or "bad"
- Classify pump status as "normal" or "abnormal"
- Calculate compliance scores
- Generate pass/fail judgments
- Compare values against thresholds
- Provide recommendations or alerts

Instead, it presents the raw data and metadata, allowing human reviewers (maintenance managers, regulators, investigators) to make their own assessments based on applicable standards and regulations.

## What This System Explicitly Does NOT Do

### No Compliance Judgment

The system does not evaluate whether maintenance activities comply with fire safety regulations or standards. It does not:
- Compare inspection results against legal requirements
- Flag non-compliance
- Generate compliance reports
- Calculate compliance percentages

### No Normal/Abnormal Inference

The system does not classify any values as "normal" or "abnormal". It does not:
- Convert boolean values (e.g., `pump_running: true`) into status strings (e.g., "running" vs "stopped")
- Apply color coding (green/red) based on values
- Add judgment labels to any data points

### No Threshold-Based Conclusions

The system does not compare values against thresholds or ranges. It does not:
- Check if pressure is within acceptable range
- Determine if equipment is operating correctly
- Generate warnings or alerts based on value comparisons
- Provide "good/bad" indicators

### No Predictive or Diagnostic Capabilities

The system does not:
- Predict equipment failures
- Diagnose problems
- Suggest maintenance actions
- Provide real-time monitoring or continuous data streams
- Generate alerts or notifications

### No Remote Control

The system does not:
- Control fire pump equipment remotely
- Start or stop pumps
- Adjust system parameters
- Interface with control systems

## Who Is Responsible for Interpretation

**Human reviewers are responsible for all interpretation and judgment.**

The system provides:
- Raw data values
- Metadata (units, sources)
- Temporal context (when data was captured)
- Source attribution (which point, which sensor)

Human reviewers (maintenance managers, safety officers, regulators, investigators) use this information to:
- Apply relevant fire safety standards and regulations
- Determine compliance status
- Make operational decisions
- Conduct post-incident analysis
- Prepare audit responses

The system's role is to **preserve evidence accurately**, not to **interpret evidence**.

## Typical Use Cases

### Fire Maintenance Evidence Retention

**Scenario**: A maintenance organization needs to demonstrate that regular fire pump maintenance was performed according to schedule.

**How the system helps**:
- Provides timestamped records of each maintenance check-in
- Links manual inspection results with machine-captured equipment state
- Preserves complete evidence chain: who, when, where, what was inspected, what was the equipment state
- Enables retrieval of historical records by date, location, or work order ID

**Outcome**: The organization can produce factual evidence of maintenance activities without needing to interpret whether activities were "compliant" or "sufficient".

### Post-Incident Review

**Scenario**: After a fire incident, investigators need to understand what maintenance was performed and what the equipment condition was prior to the incident.

**How the system helps**:
- Provides immutable records of maintenance activities with timestamps
- Shows exact equipment state (pressure, pump running) at the time of each maintenance check-in
- Preserves evidence in a format that cannot be retroactively modified
- Enables timeline reconstruction of maintenance history

**Outcome**: Investigators have access to factual records without system-generated interpretations that might conflict with their own analysis.

### Third-Party Audit Explanation

**Scenario**: A regulatory body or insurance company audits maintenance records to verify that required maintenance was performed.

**How the system helps**:
- Provides structured, searchable records of all maintenance activities
- Shows both human-reported inspection results and machine-captured evidence
- Includes metadata (units, sources) for transparency
- Enables export of evidence chains in report format (PDF)

**Outcome**: Auditors receive factual evidence that they can evaluate according to their own standards and requirements, without system-generated compliance judgments that might not align with their criteria.

## Why This Is Different from Traditional Smart-Fire Systems

Traditional smart-fire systems typically focus on:

- **Real-time monitoring**: Continuous data streams, dashboards, live status displays
- **Alert generation**: Threshold-based notifications, anomaly detection
- **Compliance automation**: Automated checks against standards, pass/fail indicators
- **Predictive maintenance**: Failure prediction, maintenance scheduling recommendations
- **Control integration**: Remote equipment control, automated responses

This system takes a different approach:

- **Evidence preservation over real-time monitoring**: Focuses on capturing point-in-time snapshots at maintenance moments, not continuous monitoring
- **Fact presentation over alert generation**: Presents raw data without generating alerts or warnings
- **Neutral documentation over compliance automation**: Documents what occurred without making compliance judgments
- **Historical record over predictive analysis**: Emphasizes accurate record-keeping for post-incident review rather than future prediction
- **Read-only evidence over control integration**: Provides evidence for human review, does not control equipment

**Key Difference**: Traditional systems aim to **prevent problems** through monitoring and alerts. This system aims to **preserve evidence** of what actually occurred, enabling human reviewers to make their own assessments.

## Technical Scope (MVP)

This MVP implementation includes:

- Mobile check-in interface for field technicians
- QR code-based location selection
- Manual inspection data entry (pumphouse, endpoint, hydrant, linkage, conclusion)
- Automatic IoT snapshot capture (pressure, pump running state) at check-in time
- Work order query and detail views
- PDF report generation with evidence chain
- Point-specific metadata configuration (units, sources)

This MVP does not include:

- Real-time dashboards or continuous monitoring
- Alert systems or threshold-based notifications
- Compliance scoring or automated judgment
- Equipment control interfaces
- Predictive analytics
- Multi-tenant or enterprise features beyond basic demo data

## Target Users

- **Field Maintenance Technicians**: Use mobile interface to record maintenance activities
- **Maintenance Managers**: Query and review maintenance records, generate reports
- **Safety Officers**: Access evidence chains for compliance documentation
- **Regulators and Auditors**: Review factual records without system-generated interpretations
- **Post-Incident Investigators**: Reconstruct maintenance history and equipment state timeline

## Value Proposition

This system provides **trustworthy evidence preservation** rather than **automated compliance management**. Organizations use it to:

- Reduce documentation burden on field staff
- Improve evidence chain completeness and accuracy
- Enable faster response to audits and investigations
- Maintain clear separation between facts and interpretations
- Preserve immutable records that cannot be retroactively modified

The value is in **evidence quality and accessibility**, not in **automated decision-making**.

