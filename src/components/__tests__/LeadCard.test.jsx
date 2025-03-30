import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import LeadCard from '../LeadCard';

describe('LeadCard Component', () => {
  const mockLead = {
    name: 'Test Business',
    phone: '555-0123',
    address: '123 Main St',
    website: 'test.com',
    category: 'auto_repair',
    overall_score: 7.5,
    analysis: {
      tech_stack: {
        score: 7,
        current_systems: ['System 1', 'System 2']
      },
      operations: {
        score: 8,
        scale: 'Small',
        efficiency: 'Medium'
      },
      growth_potential: {
        score: 9,
        market_position: 'Strong'
      },
      software_opportunity: {
        score: 8,
        pain_points: ['Point 1', 'Point 2']
      },
      sales_conversation: {
        opening_points: ['Point 1', 'Point 2'],
        questions: ['Question 1', 'Question 2']
      }
    }
  };

  const mockOnUpdateNotes = jest.fn();
  const mockOnMarkCalled = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders basic lead information', () => {
    render(
      <LeadCard
        lead={mockLead}
        onUpdateNotes={mockOnUpdateNotes}
        onMarkCalled={mockOnMarkCalled}
      />
    );

    expect(screen.getByText('Test Business')).toBeInTheDocument();
    expect(screen.getByText('555-0123')).toBeInTheDocument();
    expect(screen.getByText('123 Main St')).toBeInTheDocument();
    expect(screen.getByText('test.com')).toBeInTheDocument();
    expect(screen.getByText('AUTO REPAIR')).toBeInTheDocument();
    expect(screen.getByText('Score: 7.5')).toBeInTheDocument();
  });

  test('expands to show analysis when clicked', () => {
    render(
      <LeadCard
        lead={mockLead}
        onUpdateNotes={mockOnUpdateNotes}
        onMarkCalled={mockOnMarkCalled}
      />
    );

    fireEvent.click(screen.getByText('Test Business'));

    // Check if analysis sections are visible
    expect(screen.getByText('Technology Stack')).toBeInTheDocument();
    expect(screen.getByText('Business Operations')).toBeInTheDocument();
    expect(screen.getByText('Growth Potential')).toBeInTheDocument();
    expect(screen.getByText('Software Opportunity')).toBeInTheDocument();
    expect(screen.getByText('Sales Conversation Guide')).toBeInTheDocument();
  });

  test('displays analysis scores correctly', () => {
    render(
      <LeadCard
        lead={mockLead}
        onUpdateNotes={mockOnUpdateNotes}
        onMarkCalled={mockOnMarkCalled}
      />
    );

    fireEvent.click(screen.getByText('Test Business'));

    expect(screen.getByText('Score: 7.0')).toBeInTheDocument();
    expect(screen.getByText('Score: 8.0')).toBeInTheDocument();
    expect(screen.getByText('Score: 9.0')).toBeInTheDocument();
    expect(screen.getByText('Score: 8.0')).toBeInTheDocument();
  });

  test('allows adding notes', () => {
    render(
      <LeadCard
        lead={mockLead}
        onUpdateNotes={mockOnUpdateNotes}
        onMarkCalled={mockOnMarkCalled}
      />
    );

    const notesTextarea = screen.getByPlaceholderText('Add your notes here...');
    fireEvent.change(notesTextarea, { target: { value: 'Test notes' } });

    expect(notesTextarea.value).toBe('Test notes');
    expect(mockOnUpdateNotes).toHaveBeenCalledWith('Test notes');
  });

  test('marks lead as called', () => {
    render(
      <LeadCard
        lead={mockLead}
        onUpdateNotes={mockOnUpdateNotes}
        onMarkCalled={mockOnMarkCalled}
      />
    );

    const markCalledButton = screen.getByText('Mark as Called');
    fireEvent.click(markCalledButton);

    expect(mockOnMarkCalled).toHaveBeenCalled();
  });

  test('displays called status correctly', () => {
    const calledLead = {
      ...mockLead,
      called: true,
      calledAt: '2024-03-30T12:00:00Z'
    };

    render(
      <LeadCard
        lead={calledLead}
        onUpdateNotes={mockOnUpdateNotes}
        onMarkCalled={mockOnMarkCalled}
      />
    );

    expect(screen.getByText('Called ✓')).toBeInTheDocument();
  });

  test('displays sales conversation guide when expanded', () => {
    render(
      <LeadCard
        lead={mockLead}
        onUpdateNotes={mockOnUpdateNotes}
        onMarkCalled={mockOnMarkCalled}
      />
    );

    fireEvent.click(screen.getByText('Test Business'));

    expect(screen.getByText('Opening Points:')).toBeInTheDocument();
    expect(screen.getByText('Point 1')).toBeInTheDocument();
    expect(screen.getByText('Point 2')).toBeInTheDocument();
    expect(screen.getByText('Questions to Ask:')).toBeInTheDocument();
    expect(screen.getByText('Question 1')).toBeInTheDocument();
    expect(screen.getByText('Question 2')).toBeInTheDocument();
  });

  test('displays pain points when expanded', () => {
    render(
      <LeadCard
        lead={mockLead}
        onUpdateNotes={mockOnUpdateNotes}
        onMarkCalled={mockOnMarkCalled}
      />
    );

    fireEvent.click(screen.getByText('Test Business'));

    expect(screen.getByText('Pain Points:')).toBeInTheDocument();
    expect(screen.getByText('Point 1')).toBeInTheDocument();
    expect(screen.getByText('Point 2')).toBeInTheDocument();
  });
}); 