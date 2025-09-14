import React from 'react';
import { motion } from 'framer-motion';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  isLoading?: boolean;
  className?: string;
  variant?: 'default' | 'compact' | 'featured';
  onClick?: () => void;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend = 'neutral',
  trendValue,
  isLoading = false,
  className = '',
  variant = 'default',
  onClick
}) => {
  const getTrendColor = () => {
    switch (trend) {
      case 'up': return 'text-emerald-600 bg-emerald-50';
      case 'down': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return '↗';
      case 'down': return '↘';
      default: return '→';
    }
  };

  const getVariantStyles = () => {
    switch (variant) {
      case 'compact':
        return 'p-4 min-h-[100px]';
      case 'featured':
        return 'p-6 min-h-[140px] bg-gradient-to-br from-white to-blue-50/30 border-blue-200/50';
      default:
        return 'p-5 min-h-[120px]';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{
        scale: onClick ? 1.02 : 1,
        boxShadow: 'var(--shadow-widget)'
      }}
      className={`
        bg-white/90 backdrop-blur-xl rounded-2xl border border-slate-200/40
        shadow-xl shadow-slate-200/10 transition-all duration-300
        ${onClick ? 'cursor-pointer' : ''}
        ${getVariantStyles()}
        ${className}
      `}
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          {icon && (
            <div className="p-2 bg-blue-50 rounded-lg">
              <span className="text-lg">{icon}</span>
            </div>
          )}
          <h3 className="text-sm font-semibold text-slate-700 truncate">
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
          <div className="skeleton h-8 w-32 mb-2"></div>
        ) : (
          <motion.div
            className={`font-bold text-slate-800 ${
              variant === 'featured' ? 'text-3xl' : variant === 'compact' ? 'text-xl' : 'text-2xl'
            }`}
            key={value}
            initial={{ scale: 1.1, opacity: 0.8 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            {value}
          </motion.div>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between">
        {trendValue && (
          <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-sm font-medium ${getTrendColor()}`}>
            <span className="text-xs">{getTrendIcon()}</span>
            <span>{trendValue}</span>
          </div>
        )}
        {subtitle && (
          <div className="text-xs text-slate-500 truncate ml-auto">
            {subtitle}
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default MetricCard;