import React, { useState } from 'react';

// Dialog 컴포넌트들
interface DialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
}

interface DialogContentProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
}

interface DialogHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
}

interface DialogTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  className?: string;
}

interface DialogTriggerProps extends React.HTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  asChild?: boolean;
}

export const Dialog: React.FC<DialogProps> & {
  Trigger: React.FC<DialogTriggerProps>;
  Content: React.FC<DialogContentProps>;
  Header: React.FC<DialogHeaderProps>;
  Title: React.FC<DialogTitleProps>;
} = ({ open, onOpenChange, children }) => {
  const [internalOpen, setInternalOpen] = useState(false);

  const isControlled = open !== undefined;
  const isOpen = isControlled ? open : internalOpen;

  const handleOpenChange = (newOpen: boolean) => {
    if (!isControlled) {
      setInternalOpen(newOpen);
    }
    onOpenChange?.(newOpen);
  };

  // children에서 Trigger를 추출하여 렌더링
  const childrenArray = React.Children.toArray(children);
  const trigger = childrenArray.find((child: any) => child?.type?.displayName === 'DialogTrigger');
  const content = childrenArray.find((child: any) => child?.type?.displayName === 'DialogContent');

  return (
    <>
      {trigger && React.cloneElement(trigger as React.ReactElement, {
        onClick: () => handleOpenChange(true),
      } as any)}
      {isOpen && content}
    </>
  );
};

Dialog.Trigger = function DialogTrigger({ children, asChild = false, ...props }: DialogTriggerProps) {
  if (asChild) {
    return <>{children}</>;
  }
  return (
    <button type="button" {...props}>
      {children}
    </button>
  );
};
Dialog.Trigger.displayName = 'DialogTrigger';

Dialog.Content = function DialogContent({ children, className = '', ...props }: DialogContentProps) {
  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center bg-black/50 ${className}`} {...props}>
      <div className="relative bg-white rounded-lg shadow-lg max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {children}
      </div>
    </div>
  );
};
Dialog.Content.displayName = 'DialogContent';

Dialog.Header = function DialogHeader({ children, className = '', ...props }: DialogHeaderProps) {
  return (
    <div className={`flex flex-col space-y-1.5 p-6 ${className}`} {...props}>
      {children}
    </div>
  );
};
Dialog.Header.displayName = 'DialogHeader';

Dialog.Title = function DialogTitle({ children, className = '', ...props }: DialogTitleProps) {
  return (
    <h2 className={`text-lg font-semibold leading-none tracking-tight text-gray-900 ${className}`} {...props}>
      {children}
    </h2>
  );
};
Dialog.Title.displayName = 'DialogTitle';
