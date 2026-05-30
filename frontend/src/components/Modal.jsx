import React from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';

const Modal = ({ isOpen, onClose, title, children, size = 'md' }) => {
  if (!isOpen) return null;
  
  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-6xl'
  };

  return createPortal(
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in"
      onClick={onClose}>
      <div 
        className={`bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl shadow-2xl w-full ${sizeClasses[size]} max-h-[90vh] overflow-y-auto no-scrollbar`}
        onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-[var(--border-color)] sticky top-0 bg-[var(--bg-panel)] rounded-t-xl z-10">
          <h3 className="text-lg font-semibold text-[var(--text-primary)]">{title}</h3>
          <button 
            onClick={onClose} 
            className="p-1 hover:bg-[var(--bg-input)] rounded-lg transition-colors text-[var(--text-muted)]">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-4">{children}</div>
      </div>
    </div>,
    document.body
  );
};

export default Modal;