import React, { useState, useEffect } from 'react';
import { initializeApp } from 'firebase/app';
import { getDatabase, ref, onValue, update } from 'firebase/database';
import LeadCard from './LeadCard';
import './LeadsList.css';

// Firebase configuration
const firebaseConfig = {
  // Your Firebase config here
  databaseURL: process.env.REACT_APP_FIREBASE_URL
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const database = getDatabase(app);

const LeadsList = () => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const leadsRef = ref(database, 'phoneLeads');
    
    const unsubscribe = onValue(leadsRef, (snapshot) => {
      const data = snapshot.val();
      if (data) {
        // Convert object to array and flatten the structure
        const leadsArray = Object.entries(data).flatMap(([batchKey, batch]) => 
          batch.leads.map(lead => ({
            ...lead,
            batchKey,
            batchMetadata: batch.metadata
          }))
        );
        setLeads(leadsArray);
      } else {
        setLeads([]);
      }
      setLoading(false);
    }, (error) => {
      console.error('Error fetching leads:', error);
      setError('Failed to load leads');
      setLoading(false);
    });

    return () => unsubscribe();
  }, [database]);

  const updateLeadNotes = async (batchKey, leadIndex, notes) => {
    try {
      const leadRef = ref(database, `phoneLeads/${batchKey}/leads/${leadIndex}`);
      await update(leadRef, { notes });
    } catch (error) {
      console.error('Error updating lead notes:', error);
      setError('Failed to update notes');
    }
  };

  const markLeadCalled = async (batchKey, leadIndex) => {
    try {
      const leadRef = ref(database, `phoneLeads/${batchKey}/leads/${leadIndex}`);
      await update(leadRef, { 
        called: true,
        calledAt: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error marking lead as called:', error);
      setError('Failed to update lead status');
    }
  };

  if (loading) {
    return <div className="loading">Loading leads...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="leads-list">
      <h1>Business Leads</h1>
      <div className="leads-grid">
        {leads.map((lead, index) => (
          <LeadCard
            key={`${lead.batchKey}-${index}`}
            lead={lead}
            onUpdateNotes={(notes) => updateLeadNotes(lead.batchKey, index, notes)}
            onMarkCalled={() => markLeadCalled(lead.batchKey, index)}
          />
        ))}
      </div>
    </div>
  );
};

export default LeadsList; 