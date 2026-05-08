-- Migration: Add new Phase 0-7 operational states to ticket_status ENUM
-- Description: Safely appends new tollgate states without dropping existing table data.
-- V3.0 Swarm Workflow (TECH-001)
-- Postgres 16 compatible

-- Add new states using ADD VALUE IF NOT EXISTS
-- Note: 'IF NOT EXISTS' requires PostgreSQL 12+
ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'PHASE_0_VANGUARD';
ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'PHASE_1_REFINEMENT';
ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'PHASE_2_EXECUTION';
ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'PHASE_3_QA_REVIEW';
ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'PHASE_4_AUDITING';
ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'PHASE_5_THREAT_COUNCIL';
ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'PHASE_6_DREAMSTATE';
ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'PHASE_7_RELEASE';

-- Explicit named Tollgate states
ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'QA_REVIEW';
ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'AUDITING';
ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'THREAT_COUNCIL_REVIEW';
ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'DREAMSTATE_READY';
ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'RELEASED';
