import React, { useState } from 'react';
import DeleteModal from './DeleteModal';
import './LeadCard.css';

const LeadCard = ({ lead, onUpdateNotes, onMarkCalled, onDelete }) => {
  const [notes, setNotes] = useState(lead.notes || '');
  const [isExpanded, setIsExpanded] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const handleNotesChange = (e) => {
    const newNotes = e.target.value;
    setNotes(newNotes);
    onUpdateNotes(newNotes);
  };

  const handleMarkCalled = () => {
    const calledNote = `Called on ${new Date().toLocaleDateString()} - ${notes || 'No notes added'}`;
    setNotes(calledNote);
    onUpdateNotes(calledNote);
    onMarkCalled();
  };

  const handleDeleteClick = () => {
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = () => {
    setShowDeleteModal(false);
    onDelete();
  };

  const handleDeleteCancel = () => {
    setShowDeleteModal(false);
  };

  const formatScore = (score) => {
    return Math.round(score * 10) / 10;
  };

  return (
    <>
      <div className={`lead-card ${lead.called ? 'called' : ''} ${isExpanded ? 'expanded' : ''}`}>
        <div className="lead-header" onClick={() => setIsExpanded(!isExpanded)}>
          <h2>{lead.name}</h2>
          <div className="lead-score">
            Score: {formatScore(lead.overall_score)}
          </div>
        </div>

        <div className="lead-content">
          <div className="lead-info">
            <p><strong>Phone:</strong> {lead.phone || 'N/A'}</p>
            <p><strong>Address:</strong> {lead.address || 'N/A'}</p>
            <p><strong>Website:</strong> {lead.website ? <a href={lead.website.startsWith('http') ? lead.website : `https://${lead.website}`} target="_blank" rel="noopener noreferrer">{lead.website}</a> : 'N/A'}</p>
            <p><strong>Category:</strong> {(lead.category || '').replace('_', ' ').toUpperCase()}</p>
          </div>

          {isExpanded && (
            <div className="lead-analysis">
              <h3>Analysis</h3>
              
              <div className="analysis-section">
                <h4>Technology Stack</h4>
                <p>Score: {formatScore(lead.analysis.tech_stack.score)}</p>
                <ul>
                  {lead.analysis.tech_stack.current_systems.map((system, index) => (
                    <li key={index}>{system}</li>
                  ))}
                </ul>
              </div>

              <div className="analysis-section">
                <h4>Business Operations</h4>
                <p>Score: {formatScore(lead.analysis.operations.score)}</p>
                <p>Scale: {lead.analysis.operations.scale}</p>
                <p>Efficiency: {lead.analysis.operations.efficiency}</p>
              </div>

              <div className="analysis-section">
                <h4>Growth Potential</h4>
                <p>Score: {formatScore(lead.analysis.growth_potential.score)}</p>
                <p>Market Position: {lead.analysis.growth_potential.market_position}</p>
              </div>

              <div className="analysis-section">
                <h4>Software Opportunity</h4>
                <p>Score: {formatScore(lead.analysis.software_opportunity.score)}</p>
                <h5>Pain Points:</h5>
                <ul>
                  {lead.analysis.software_opportunity.pain_points.map((point, index) => (
                    <li key={index}>{point}</li>
                  ))}
                </ul>
              </div>

              <div className="analysis-section">
                <h4>Sales Conversation Guide</h4>
                <h5>Opening Points:</h5>
                <ul>
                  {lead.analysis.sales_conversation.opening_points.map((point, index) => (
                    <li key={index}>{point}</li>
                  ))}
                </ul>
                <h5>Questions to Ask:</h5>
                <ul>
                  {lead.analysis.sales_conversation.questions.map((question, index) => (
                    <li key={index}>{question}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          <div className="lead-actions">
            <div className="notes-section">
              <h4>Call Notes</h4>
              <textarea
                value={notes}
                onChange={handleNotesChange}
                placeholder="Add your notes here..."
              />
            </div>

            <div className="action-buttons">
              <button
                className={`mark-called-btn ${lead.called ? 'called' : ''}`}
                onClick={handleMarkCalled}
                disabled={lead.called}
              >
                {lead.called ? 'Called ✓' : 'Mark as Called'}
              </button>
              <button
                className="delete-btn"
                onClick={handleDeleteClick}
              >
                Delete Lead
              </button>
            </div>
          </div>
        </div>
      </div>

      <DeleteModal
        isOpen={showDeleteModal}
        onClose={handleDeleteCancel}
        onConfirm={handleDeleteConfirm}
        leadName={lead.name}
      />
    </>
  );
};

export default LeadCard; 