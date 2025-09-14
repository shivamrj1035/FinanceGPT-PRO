import React from 'react';
import { motion } from 'framer-motion';

interface ChartContainerProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  isLoading?: boolean;
  error?: string;
  className?: string;
  headerActions?: React.ReactNode;
  variant?: 'default' | 'compact' | 'featured';
  height?: string | number;
}

const ChartContainer: React.FC<ChartContainerProps> = ({
  title,
  subtitle,
  children,
  isLoading = false,
  error,
  className = '',
  headerActions,
  variant = 'default',
  height = 'auto'
}) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'compact':
        return 'p-4 min-h-[200px]';
      case 'featured':
        return 'p-6 min-h-[400px] bg-gradient-to-br from-white via-blue-50/20 to-indigo-50/30 border-blue-200/50';
      default:
        return 'p-6 min-h-[300px]';
    }
  };

  const chartHeight = typeof height === 'number' ? `${height}px` : height;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`
        bg-white/90 backdrop-blur-xl rounded-2xl border border-slate-200/40
        shadow-xl shadow-slate-200/10 transition-all duration-300
        hover:shadow-2xl hover:shadow-slate-200/20
        ${getVariantStyles()}
        ${className}
      `}
      style={{ height: height !== 'auto' ? chartHeight : undefined }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-bold text-slate-800 mb-1">
            {title}
          </h3>
          {subtitle && (
            <p className="text-sm text-slate-600">
              {subtitle}
            </p>
          )}
        </div>

        {/* Loading or Actions */}
        <div className="flex items-center space-x-2">
          {isLoading && (
            <div className="w-5 h-5 border-2 border-blue-200 border-t-blue-500 rounded-full animate-spin"></div>
          )}
          {headerActions && !isLoading && headerActions}
        </div>
      </div>

      {/* Chart Content */}
      <div className="flex-1 relative">
        {error ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <div className="text-4xl mb-2">⚠️</div>
              <p className="text-red-600 font-medium mb-1">Chart Error</p>
              <p className="text-sm text-slate-500">{error}</p>
            </div>
          </div>
        ) : isLoading ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-slate-500">Loading chart data...</p>
            </div>
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="h-full w-full"
          >
            {children}
          </motion.div>
        )}
      </div>

      {/* Chart Footer (for legends, etc.) */}
      <div className="mt-4 pt-4 border-t border-slate-200/50">
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>Real-time data</span>
          <span className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
            <span>Live</span>
          </span>
        </div>
      </div>
    </motion.div>
  );
};

export default ChartContainer;