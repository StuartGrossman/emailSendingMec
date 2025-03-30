import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { initializeApp } from 'firebase/app';
import { getDatabase, ref, onValue } from 'firebase/database';
import LeadsList from '../LeadsList';

// Mock Firebase
jest.mock('firebase/app');
jest.mock('firebase/database');

describe('LeadsList Component', () => {
  const mockLeads = {
    'batch1': {
      leads: [
        {
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
        }
      ],
      metadata: {
        city: 'San Francisco',
        state: 'CA',
        business_type: 'auto_repair',
        timestamp: '20240330',
        count: 1
      }
    }
  };

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();

    // Mock Firebase initialization
    initializeApp.mockReturnValue({});
    getDatabase.mockReturnValue({});

    // Mock Firebase onValue
    onValue.mockImplementation((ref, callback) => {
      callback({ val: () => mockLeads });
      return () => {}; // Return unsubscribe function
    });
  });

  test('renders loading state initially', () => {
    render(<LeadsList />);
    expect(screen.getByText('Loading leads...')).toBeInTheDocument();
  });

  test('renders leads after loading', async () => {
    render(<LeadsList />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Business')).toBeInTheDocument();
      expect(screen.getByText('555-0123')).toBeInTheDocument();
    });
  });

  test('displays error message when Firebase fails', async () => {
    onValue.mockImplementation((ref, callback) => {
      callback({ val: () => null });
      return () => {};
    });

    render(<LeadsList />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load leads')).toBeInTheDocument();
    });
  });

  test('expands lead card when clicked', async () => {
    render(<LeadsList />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Business')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Test Business'));

    // Check if analysis sections are visible
    expect(screen.getByText('Technology Stack')).toBeInTheDocument();
    expect(screen.getByText('Business Operations')).toBeInTheDocument();
    expect(screen.getByText('Growth Potential')).toBeInTheDocument();
  });

  test('allows adding notes to a lead', async () => {
    render(<LeadsList />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Business')).toBeInTheDocument();
    });

    const notesTextarea = screen.getByPlaceholderText('Add your notes here...');
    fireEvent.change(notesTextarea, { target: { value: 'Test notes' } });

    expect(notesTextarea.value).toBe('Test notes');
  });

  test('marks lead as called', async () => {
    render(<LeadsList />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Business')).toBeInTheDocument();
    });

    const markCalledButton = screen.getByText('Mark as Called');
    fireEvent.click(markCalledButton);

    expect(screen.getByText('Called ✓')).toBeInTheDocument();
  });
}); 