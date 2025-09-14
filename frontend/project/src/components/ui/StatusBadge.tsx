import React from 'react';
import { motion } from 'framer-motion';

interface StatusBadgeProps {
  status: 'active' | 'inactive' | 'warning' | 'error' | 'success' | 'pending';
  label?: string;
  icon?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'solid' | 'outline' | 'subtle';
  animate?: boolean;
  className?: string;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  label,
  icon,
  size = 'md',
  variant = 'solid',
  animate = true,
  className = ''
}) => {
  const getStatusConfig = () => {
    const configs = {
      active: {
        colors: {
          solid: 'bg-emerald-500 text-white',
          outline: 'border-emerald-500 text-emerald-700 bg-emerald-50',
          subtle: 'bg-emerald-100 text-emerald-800'
        },
        dot: 'bg-emerald-400'
      },
      inactive: {
        colors: {
          solid: 'bg-gray-500 text-white',
          outline: 'border-gray-500 text-gray-700 bg-gray-50',
          subtle: 'bg-gray-100 text-gray-800'
        },
        dot: 'bg-gray-400'
      },
      warning: {
        colors: {
          solid: 'bg-yellow-500 text-white',
          outline: 'border-yellow-500 text-yellow-700 bg-yellow-50',
          subtle: 'bg-yellow-100 text-yellow-800'
        },
        dot: 'bg-yellow-400'
      },
      error: {
        colors: {
          solid: 'bg-red-500 text-white',
          outline: 'border-red-500 text-red-700 bg-red-50',
          subtle: 'bg-red-100 text-red-800'
        },
        dot: 'bg-red-400'
      },
      success: {
        colors: {
          solid: 'bg-emerald-600 text-white',
          outline: 'border-emerald-600 text-emerald-700 bg-emerald-50',
          subtle: 'bg-emerald-100 text-emerald-800'
        },
        dot: 'bg-emerald-500'
      },
      pending: {
        colors: {
          solid: 'bg-blue-500 text-white',
          outline: 'border-blue-500 text-blue-700 bg-blue-50',
          subtle: 'bg-blue-100 text-blue-800'
        },
        dot: 'bg-blue-400'
      }
    };
    return configs[status];
  };

  const getSizeConfig = () => {
    const configs = {
      sm: {
        padding: 'px-2 py-1',
        text: 'text-xs',
        dot: 'w-1.5 h-1.5',
        icon: 'text-xs'
      },
      md: {
        padding: 'px-3 py-1.5',
        text: 'text-sm',
        dot: 'w-2 h-2',
        icon: 'text-sm'
      },
      lg: {
        padding: 'px-4 py-2',
        text: 'text-base',
        dot: 'w-2.5 h-2.5',
        icon: 'text-base'
      }
    };
    return configs[size];
  };

  const statusConfig = getStatusConfig();
  const sizeConfig = getSizeConfig();

  const baseClasses = `
    inline-flex items-center space-x-2 rounded-full font-medium
    transition-all duration-200
    ${sizeConfig.padding}
    ${sizeConfig.text}
    ${variant === 'outline' ? 'border' : ''}
    ${statusConfig.colors[variant]}
  `;

  const BadgeComponent = animate ? motion.div : 'div';
  const badgeProps = animate ? {
    initial: { scale: 0.8, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    transition: { duration: 0.2 }
  } : {};

  return (
    <BadgeComponent
      className={`${baseClasses} ${className}`}
      {...badgeProps}
    >
      {/* Status Dot */}
      <motion.div
        className={`rounded-full ${sizeConfig.dot} ${statusConfig.dot}`}
        animate={status === 'active' || status === 'pending' ? { scale: [1, 1.2, 1] } : {}}
        transition={status === 'active' || status === 'pending' ? {
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut'
        } : {}}
      />

      {/* Icon */}
      {icon && (
        <span className={sizeConfig.icon}>
          {icon}
        </span>
      )}

      {/* Label */}
      {label && (
        <span className="font-medium">
          {label}
        </span>
      )}
    </BadgeComponent>
  );
};

export default StatusBadge;