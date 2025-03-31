import React from 'react';
import './DeleteModal.css';

const DeleteModal = ({ isOpen, onClose, onConfirm, leadName }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Delete Lead</h2>
        <p>Are you sure you want to delete the lead for <strong>{leadName}</strong>?</p>
        <p className="warning-text">This action cannot be undone.</p>
        <div className="modal-buttons">
          <button className="cancel-btn" onClick={onClose}>
            Cancel
          </button>
          <button className="confirm-btn" onClick={onConfirm}>
            Delete
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteModal; 