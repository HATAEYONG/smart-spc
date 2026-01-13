import React from 'react';

// ScrollArea 컴포넌트
interface ScrollAreaProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
}

export const ScrollArea: React.FC<ScrollAreaProps> = ({ children, className = '', ...props }) => (
  <div className={`overflow-auto ${className}`} {...props}>
    {children}
  </div>
);
