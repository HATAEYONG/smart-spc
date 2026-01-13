import React, { useState } from 'react';

// Tabs 컴포넌트들
interface TabsProps {
  defaultValue?: string;
  children: React.ReactNode;
  className?: string;
}

interface TabsListProps {
  children: React.ReactNode;
  className?: string;
}

interface TabsTriggerProps {
  value: string;
  children: React.ReactNode;
  className?: string;
}

interface TabsContentProps {
  value: string;
  children: React.ReactNode;
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({ defaultValue, children, className = '' }) => {
  const [activeTab, setActiveTab] = useState(defaultValue || '');

  const childrenArray = React.Children.toArray(children);
  const list = childrenArray.find((child: any) => child?.type?.displayName === 'TabsList');
  const contents = childrenArray.filter((child: any) => child?.type?.displayName === 'TabsContent');

  return (
    <div className={className}>
      {list && React.cloneElement(list as React.ReactElement, {
        activeTab,
        onTabChange: setActiveTab,
      } as any)}
      <div className="mt-4">
        {contents?.map((content: any) =>
          content?.props.value === activeTab ? content : null
        )}
      </div>
    </div>
  );
};

Tabs.List = function TabsList({ children, activeTab, onTabChange, className = '' }: any) {
  return (
    <div className={`inline-flex h-10 items-center justify-center rounded-md bg-gray-100 p-1 ${className}`}>
      {React.Children.map(children, (child: any) =>
        React.cloneElement(child, {
          isActive: child.props.value === activeTab,
          onClick: () => onTabChange(child.props.value),
        })
      )}
    </div>
  );
};
Tabs.List.displayName = 'TabsList';

Tabs.Trigger = function TabsTrigger({ value, children, isActive = false, onClick, className = '' }: any) {
  return (
    <button
      onClick={onClick}
      className={`inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-white transition-all focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ${
        isActive
          ? 'bg-white text-gray-900 shadow-sm'
          : 'text-gray-500 hover:text-gray-900'
      } ${className}`}
    >
      {children}
    </button>
  );
};
Tabs.Trigger.displayName = 'TabsTrigger';

Tabs.Content = function TabsContent({ value, children, className = '' }: TabsContentProps) {
  return (
    <div className={className}>
      {children}
    </div>
  );
};
Tabs.Content.displayName = 'TabsContent';
