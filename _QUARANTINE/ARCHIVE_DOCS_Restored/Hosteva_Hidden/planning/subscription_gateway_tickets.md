# Feature: Subscription Gateway

## Tech/Spike: Infrastructure Setup for Async Processing & Storage
* Implement Redis background task queues for asynchronous processing (e.g., PDF generation).
* Configure an S3-compatible blob storage bucket for document persistence.
* Setup Webhook endpoints for asynchronous payment event handling.
* Update database schema for subscriptions: `provider_customer_id`, `provider_subscription_id`, `current_period_end`, and `subscription_status` (active, past_due, canceled).
* Update database schema for property documents: `file_url`, `document_type`, and `generated_at`.

## User Story: TKT-101 - Select and Purchase Subscription
**Description:**
The system must provide a gateway for users to select, purchase, and manage their subscription tiers.

**Gherkin Scenarios:**

**Scenario:** Successful subscription purchase initiation
* **Given** the user is authenticated and on the Subscription Gateway page
* **When** the user selects the "Pro" tier and submits valid payment credentials
* **Then** the system must initiate the transaction and return a pending status
* **And** the system must await the asynchronous payment confirmation

**Scenario:** Async Webhook payment success processing
* **Given** a subscription payment is pending
* **When** the system receives a successful payment webhook event from the provider
* **Then** the system must update the user's subscription status to active
* **And** the system must update the `current_period_end`, `provider_customer_id`, and `provider_subscription_id`
* **And** the system must queue a confirmation email containing the receipt

**Scenario:** Failed subscription payment
* **Given** the user is authenticated and on the Subscription Gateway page
* **When** the user submits invalid payment credentials for a subscription tier
* **Then** the system must decline the transaction
* **And** the system must display an error message indicating payment failure
* **And** the system must leave the user's subscription tier unchanged

---

# Feature: Compliance Document Generation

## User Story: TKT-201 - Generate Short-Term Rental Compliance Documents
**Description:**
The system must generate properly formatted compliance documents asynchronously via Redis queues and store them in S3 based on the user's property address and local regulations.

**Gherkin Scenarios:**

**Scenario:** Successful asynchronous generation of a compliance document
* **Given** the system has verified the user's property address for eligibility
* **When** the user requests the generation of compliance documents
* **Then** the system must queue the generation task in Redis and return a pending status
* **And** the background worker must fetch the appropriate local regulatory template and populate it
* **And** the worker must upload the generated PDF file to S3 storage
* **And** the worker must save the S3 `file_url`, `document_type`, and `generated_at` to the user's property record

**Scenario:** Missing data for document generation
* **Given** the user's profile is missing required property data
* **When** the user requests the generation of compliance documents
* **Then** the system must halt the document generation process
* **And** the system must prompt the user to fill in the missing required fields

---

## Definition of Done (DoD)
* All 3rd-person Gherkin scenarios pass automated testing.
* Code is reviewed and approved by at least one peer.
* Code meets LOBSTER standards and is free of raw JSON/code bloat.
* Features are deployed to the staging environment and manually verified by the Product Owner (Richard Farber).


[APPROVED - Vision]
[APPROVED - Iron Man]
[SEALED - Captain America]
