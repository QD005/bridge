import React from 'react';
import { Hash, CreditCard, User, Building2, Mail, Phone, Calendar, FileText, CheckSquare, Type, AlertCircle } from 'lucide-react';

const fieldIcons = {
  nin: Hash,
  tin: CreditCard,
  name: User,
  surname: User,
  first_name: User,
  last_name: User,
  full_name: User,
  company_name: Building2,
  business_name: Building2,
  email: Mail,
  phone: Phone,
  phone_number: Phone,
  date: Calendar,
  date_of_birth: Calendar,
  dob: Calendar,
  description: FileText,
  comment: FileText,
  notes: FileText,
  default: Type,
};

const getFieldIcon = (name) => {
  const key = Object.keys(fieldIcons).find(k => name.toLowerCase().includes(k));
  const Icon = key ? fieldIcons[key] : fieldIcons.default;
  return <Icon className="w-4 h-4 text-[var(--text-muted)]" />;
};

const DynamicForm = ({ fields, data, onChange, errors = {} }) => {
  const handleChange = (name, value) => {
    onChange({ ...data, [name]: value });
  };

  const renderField = (field) => {
    const { name, label, type = 'text', required, placeholder, help_text, options = [], validation_regex } = field;
    const value = data[name] || '';
    const error = errors[name];
    const inputClasses = `input-field ${error ? 'border-danger focus:ring-danger' : ''}`;

    return (
      <div key={name} className="space-y-1">
        <label className="label flex items-center gap-2">
          {getFieldIcon(name)}
          {label || name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          {required && <span className="text-danger">*</span>}
        </label>

        {type === 'select' ? (
          <select
            className={inputClasses}
            value={value}
            onChange={e => handleChange(name, e.target.value)}
            required={required}
          >
            <option value="">Select...</option>
            {options.map(opt => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        ) : type === 'textarea' ? (
          <textarea
            className={inputClasses}
            rows={4}
            value={value}
            onChange={e => handleChange(name, e.target.value)}
            placeholder={placeholder || `Enter ${label || name}`}
            required={required}
          />
        ) : type === 'checkbox' ? (
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              className="w-4 h-4 rounded border-[var(--border-color)] text-accent focus:ring-accent"
              checked={!!value}
              onChange={e => handleChange(name, e.target.checked)}
            />
            <span className="text-sm text-[var(--text-secondary)]">{placeholder || 'Yes'}</span>
          </label>
        ) : type === 'file' ? (
          <input
            type="file"
            className="input-field py-1.5 text-sm file:mr-4 file:py-1 file:px-3 file:rounded-lg file:border-0 file:bg-accent file:text-white hover:file:bg-accent-hover"
            onChange={e => handleChange(name, e.target.files[0])}
          />
        ) : (
          <input
            type={type === 'phone' ? 'tel' : type === 'email' ? 'email' : type === 'number' ? 'number' : type === 'date' ? 'date' : 'text'}
            className={inputClasses}
            value={value}
            onChange={e => handleChange(name, e.target.value)}
            placeholder={placeholder || `Enter ${label || name}`}
            required={required}
            pattern={validation_regex || undefined}
          />
        )}

        {help_text && (
          <p className="text-xs text-[var(--text-muted)] flex items-center gap-1">
            <AlertCircle className="w-3 h-3" />
            {help_text}
          </p>
        )}
        {error && (
          <p className="text-xs text-danger flex items-center gap-1">
            <AlertCircle className="w-3 h-3" />
            {error}
          </p>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {fields.sort((a, b) => (a.order || 0) - (b.order || 0)).map(renderField)}
    </div>
  );
};

export default DynamicForm;
