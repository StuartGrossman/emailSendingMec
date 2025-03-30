import React, { useState, useEffect } from 'react';
import { ref, onValue, update, get, remove } from 'firebase/database';
import { getFirebaseDatabase } from '../firebase';
import LeadCard from './LeadCard';
import ScoreFilter from './ScoreFilter';
import './LeadsList.css';

const LeadsList = () => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [minScore, setMinScore] = useState(0);
  const [selectedCity, setSelectedCity] = useState('all');
  const [selectedBusinessType, setSelectedBusinessType] = useState('all');
  const [sortOrder, setSortOrder] = useState('desc');

  useEffect(() => {
    const database = getFirebaseDatabase();
    const leadsRef = ref(database, 'phoneLeads');
    
    const unsubscribe = onValue(leadsRef, (snapshot) => {
      try {
        const data = snapshot.val();
        if (data) {
          // Convert the nested structure to a flat array
          const leadsArray = [];
          Object.entries(data).forEach(([city, cityData]) => {
            Object.entries(cityData).forEach(([businessType, businessData]) => {
              Object.entries(businessData).forEach(([batchKey, batchData]) => {
                if (batchData.leads) {
                  batchData.leads.forEach(lead => {
                    leadsArray.push({
                      ...lead,
                      id: `${city}/${businessType}/${batchKey}/${lead.name}`,
                      city,
                      business_type: businessType,
                      batch_key: batchKey
                    });
                  });
                }
              });
            });
          });
          setLeads(leadsArray);
        } else {
          setLeads([]);
        }
      } catch (err) {
        console.error('Error processing leads data:', err);
        setError('Failed to process leads data');
      } finally {
        setLoading(false);
      }
    }, (error) => {
      console.error('Error fetching leads:', error);
      setError('Failed to fetch leads');
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Get unique cities and business types from leads
  const cities = ['all', ...new Set(leads.map(lead => lead.city))].sort();
  const businessTypes = ['all', ...new Set(leads.map(lead => lead.business_type))].sort();

  const updateLeadNotes = async (batchKey, leadIndex, notes) => {
    try {
      const database = getFirebaseDatabase();
      const leadRef = ref(database, `phoneLeads/${batchKey}/leads/${leadIndex}`);
      await update(leadRef, { notes });
    } catch (error) {
      console.error('Error updating lead notes:', error);
      setError('Failed to update notes');
    }
  };

  const markLeadCalled = async (leadId) => {
    try {
      const database = getFirebaseDatabase();
      const [city, businessType, batchKey, name] = leadId.split('/');
      const leadRef = ref(database, `phoneLeads/${city}/${businessType}/${batchKey}/leads/${name}`);
      await update(leadRef, { called: true });
    } catch (error) {
      console.error('Error marking lead as called:', error);
    }
  };

  const deleteLead = async (leadId) => {
    try {
      const database = getFirebaseDatabase();
      const [city, businessType, batchKey, name] = leadId.split('/');
      const leadRef = ref(database, `phoneLeads/${city}/${businessType}/${batchKey}/leads/${name}`);
      await remove(leadRef);
    } catch (error) {
      console.error('Error deleting lead:', error);
    }
  };

  // Filter and sort leads
  const filteredLeads = leads
    .filter(lead => lead.overall_score >= minScore)
    .filter(lead => selectedCity === 'all' || lead.city === selectedCity)
    .filter(lead => selectedBusinessType === 'all' || lead.business_type === selectedBusinessType)
    .sort((a, b) => {
      const scoreA = a.overall_score;
      const scoreB = b.overall_score;
      return sortOrder === 'desc' ? scoreB - scoreA : scoreA - scoreB;
    });

  if (loading) {
    return <div className="loading">Loading leads...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="leads-list">
      <div className="leads-header">
        <h1>Business Leads</h1>
        <div className="leads-filters">
          <select 
            value={selectedCity} 
            onChange={(e) => setSelectedCity(e.target.value)}
            className="filter-select"
          >
            {cities.map(city => (
              <option key={city} value={city}>
                {city === 'all' ? 'All Cities' : city}
              </option>
            ))}
          </select>

          <select 
            value={selectedBusinessType} 
            onChange={(e) => setSelectedBusinessType(e.target.value)}
            className="filter-select"
          >
            {businessTypes.map(type => (
              <option key={type} value={type}>
                {type === 'all' ? 'All Business Types' : type}
              </option>
            ))}
          </select>

          <button 
            className="sort-button"
            onClick={() => setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc')}
          >
            Sort {sortOrder === 'desc' ? '↓' : '↑'}
          </button>
        </div>
      </div>

      <ScoreFilter
        minScore={0}
        maxScore={10}
        currentScore={minScore}
        onScoreChange={setMinScore}
      />

      <div className="leads-grid">
        {filteredLeads.map((lead, index) => (
          <LeadCard
            key={`${lead.id}-${index}`}
            lead={lead}
            onUpdateNotes={(notes) => updateLeadNotes(lead.batch_key, index, notes)}
            onMarkCalled={() => markLeadCalled(lead.id)}
            onDelete={() => deleteLead(lead.id)}
          />
        ))}
      </div>
    </div>
  );
};

export default LeadsList; 