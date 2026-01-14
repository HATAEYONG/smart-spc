import React, { useState } from 'react';

// Select 컴포넌트들
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  className?: string;
  value?: string;
  onValueChange?: (value: string) => void;
  children?: React.ReactNode;
}

interface SelectTriggerProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
  children: React.ReactNode;
}

interface SelectContentProps {
  children: React.ReactNode;
}

interface SelectItemProps extends React.OptionHTMLAttributes<HTMLOptionElement> {
  value: string;
  children: React.ReactNode;
}

export const Select: React.FC<SelectProps> = ({ children, className = '', value, onValueChange, ...props }) => {
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    if (onValueChange) {
      onValueChange(e.target.value);
    }
    if (props.onChange) {
      props.onChange(e);
    }
  };

  return (
    <div className="relative">
      <select
        value={value}
        onChange={handleChange}
        className={`flex h-10 w-full items-center justify-between rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
        {...props}
      >
        {children}
      </select>
    </div>
  );
};

export const SelectTrigger: React.FC<SelectTriggerProps> = ({ children, className = '', ...props }) => (
  <div className={`flex h-10 w-full items-center justify-between rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ${className}`} {...props}>
    {children}
  </div>
);

export const SelectContent: React.FC<SelectContentProps> = ({ children }) => <>{children}</>;

export const SelectItem: React.FC<SelectItemProps> = ({ value, children, ...props }) => (
  <option value={value} {...props}>
    {children}
  </option>
);

interface SelectValueProps {
  placeholder?: string;
}

export const SelectValue: React.FC<SelectValueProps> = ({ placeholder }) => (
  <span className="text-gray-500">{placeholder}</span>
);
