import React from 'react';
import { motion } from 'framer-motion';

interface KPICardProps {
  title: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon?: string;
  subtitle?: string;
  isLoading?: boolean;
  className?: string;
  onClick?: () => void;
}

const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  change,
  changeType = 'neutral',
  icon,
  subtitle,
  isLoading = false,
  className = '',
  onClick
}) => {
  const getChangeColor = () => {
    switch (changeType) {
      case 'positive': return 'text-emerald-600';
      case 'negative': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getChangeIcon = () => {
    switch (changeType) {
      case 'positive': return '↗';
      case 'negative': return '↘';
      default: return '→';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{
        scale: onClick ? 1.02 : 1,
        boxShadow: onClick ? 'var(--shadow-widget)' : 'var(--shadow-card)'
      }}
      className={`kpi-card ${onClick ? 'cursor-pointer' : ''} ${className}`}
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          {icon && (
            <span className="text-lg">{icon}</span>
          )}
          <h3 className="text-sm font-medium text-gray-600 truncate">
            {title}
          </h3>
        </div>
        {isLoading && (
          <div className="w-4 h-4 border-2 border-blue-200 border-t-blue-500 rounded-full animate-spin"></div>
        )}
      </div>

      {/* Value */}
      <div className="mb-2">
        {isLoading ? (
          <div className="skeleton h-8 w-24 mb-2"></div>
        ) : (
          <motion.div
            className="text-2xl font-bold text-gray-800"
            key={value}
            initial={{ scale: 1.1, opacity: 0.8 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            {value}
          </motion.div>
        )}
      </div>

      {/* Change & Subtitle */}
      <div className="flex items-center justify-between">
        {change && (
          <div className={`flex items-center space-x-1 text-sm font-medium ${getChangeColor()}`}>
            <span className="text-xs">{getChangeIcon()}</span>
            <span>{change}</span>
          </div>
        )}
        {subtitle && (
          <div className="text-xs text-gray-500 truncate">
            {subtitle}
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default KPICard;