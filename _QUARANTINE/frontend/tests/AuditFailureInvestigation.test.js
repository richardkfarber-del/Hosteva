// AuditFailureInvestigation.test.js
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import AuditFailureInvestigation from '../src/components/AuditFailureInvestigation';

describe('Audit Failure Investigation Component', () => {
  test('renders objective and scenarios', async () => {
    render(<AuditFailureInvestigation />);

    expect(screen.getByText('Objective:')).toBeInTheDocument();
    expect(screen.getByText('Scenarios:')).toBeInTheDocument();
  });

  test('renders recommendations', async () => {
    render(<AuditFailureInvestigation />);

    expect(screen.getByText('Update Regulations')).toBeInTheDocument();
    expect(screen.getByText('Correct Implementation')).toBeInTheDocument();
  });
});