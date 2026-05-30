import React from 'react';

const statusColors = {
  ACTIVE: 'bg-success/10 text-success border-success/20',
  PUBLISHED: 'bg-success/10 text-success border-success/20',
  COMPLETED: 'bg-success/10 text-success border-success/20',
  ONLINE: 'bg-success/10 text-success border-success/20',
  DRAFT: 'bg-gov-400/10 text-gov-400 border-gov-400/20',
  PENDING: 'bg-warning/10 text-warning border-warning/20',
  RUNNING: 'bg-info/10 text-info border-info/20 animate-pulse',
  IN_PROGRESS: 'bg-info/10 text-info border-info/20 animate-pulse',
  WAITING: 'bg-warning/10 text-warning border-warning/20',
  FAILED: 'bg-danger/10 text-danger border-danger/20',
  REJECTED: 'bg-danger/10 text-danger border-danger/20',
  OFFLINE: 'bg-danger/10 text-danger border-danger/20',
  SUSPENDED: 'bg-danger/10 text-danger border-danger/20',
  CANCELLED: 'bg-gov-500/10 text-gov-500 border-gov-500/20',
  ARCHIVED: 'bg-gov-500/10 text-gov-500 border-gov-500/20',
  SKIPPED: 'bg-gov-400/10 text-gov-400 border-gov-400/20',
  DEFAULT: 'bg-gov-400/10 text-gov-400 border-gov-400/20',
};

const Badge = ({ status, text }) => {
  const cls = statusColors[status] || statusColors.DEFAULT;
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${cls}`}>
      {text || status}
    </span>
  );
};

export default Badge;
