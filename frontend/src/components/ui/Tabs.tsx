import React, { useState } from 'react';

// Tabs 컴포넌트들
interface TabsProps {
  defaultValue?: string;
  children: React.ReactNode;
  className?: string;
}

interface TabsListProps {
  children: React.ReactNode;
  activeTab?: string;
  onTabChange?: (tab: string) => void;
  className?: string;
}

interface TabsTriggerProps {
  value: string;
  children: React.ReactNode;
  isActive?: boolean;
  onClick?: () => void;
  className?: string;
}

interface TabsContentProps {
  value: string;
  children: React.ReactNode;
  className?: string;
}

export const Tabs: React.FC<TabsProps> & {
  List: React.FC<TabsListProps>;
  Trigger: React.FC<TabsTriggerProps>;
  Content: React.FC<TabsContentProps>;
} = ({ defaultValue, children, className = '' }) => {
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

const TabsList: React.FC<TabsListProps> = ({ children, activeTab, onTabChange, className = '' }) => {
  return (
    <div className={`inline-flex h-10 items-center justify-center rounded-md bg-gray-100 p-1 ${className}`}>
      {React.Children.map(children, (child: any) =>
        React.cloneElement(child, {
          isActive: child.props.value === activeTab,
          onClick: () => onTabChange?.(child.props.value),
        })
      )}
    </div>
  );
};
TabsList.displayName = 'TabsList';
Tabs.List = TabsList;

const TabsTrigger: React.FC<TabsTriggerProps> = ({ value, children, isActive = false, onClick, className = '' }) => {
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
TabsTrigger.displayName = 'TabsTrigger';
Tabs.Trigger = TabsTrigger;

const TabsContent: React.FC<TabsContentProps> = ({ value, children, className = '' }) => {
  return (
    <div className={className}>
      {children}
    </div>
  );
};
TabsContent.displayName = 'TabsContent';
Tabs.Content = TabsContent;

export { TabsList, TabsTrigger, TabsContent };
