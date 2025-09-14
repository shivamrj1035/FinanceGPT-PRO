import React, { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChartContainer } from '../ui';

interface DataPoint {
  timestamp: string;
  value: number;
  label?: string;
}

interface RealTimeLineChartProps {
  title: string;
  subtitle?: string;
  data: DataPoint[];
  maxDataPoints?: number;
  isLive?: boolean;
  color?: string;
  fillGradient?: boolean;
  showDots?: boolean;
  height?: number;
  className?: string;
  onDataUpdate?: (newPoint: DataPoint) => void;
}

const RealTimeLineChart: React.FC<RealTimeLineChartProps> = ({
  title,
  subtitle,
  data,
  maxDataPoints = 50,
  isLive = true,
  color = '#0ea5e9',
  fillGradient = true,
  showDots = true,
  height = 300,
  className = '',
  onDataUpdate
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const [animatedData, setAnimatedData] = useState<DataPoint[]>([]);
  const [isAnimating, setIsAnimating] = useState(false);

  // Process and limit data
  const processedData = useMemo(() => {
    return data.slice(-maxDataPoints);
  }, [data, maxDataPoints]);

  // Animate data changes
  useEffect(() => {
    if (processedData.length === 0) return;

    setIsAnimating(true);

    // Animate new data points
    const animateData = () => {
      setAnimatedData(prev => {
        const newData = [...processedData];

        // If we have new data points, animate them in
        if (newData.length > prev.length) {
          const latestPoint = newData[newData.length - 1];
          if (onDataUpdate) onDataUpdate(latestPoint);
        }

        return newData;
      });

      setTimeout(() => setIsAnimating(false), 500);
    };

    const timeout = setTimeout(animateData, 100);
    return () => clearTimeout(timeout);
  }, [processedData, onDataUpdate]);

  // Draw chart
  useEffect(() => {
    if (!canvasRef.current || animatedData.length < 2) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    const width = rect.width;
    const height = rect.height;
    const padding = 40;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Calculate scales
    const values = animatedData.map(d => d.value);
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const range = maxValue - minValue || 1;

    const xScale = (width - 2 * padding) / (animatedData.length - 1);
    const yScale = (height - 2 * padding) / range;

    // Create path
    ctx.beginPath();
    animatedData.forEach((point, index) => {
      const x = padding + index * xScale;
      const y = height - padding - ((point.value - minValue) * yScale);

      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    // Draw fill gradient if enabled
    if (fillGradient) {
      const fillPath = new Path2D();
      fillPath.moveTo(padding, height - padding);

      animatedData.forEach((point, index) => {
        const x = padding + index * xScale;
        const y = height - padding - ((point.value - minValue) * yScale);

        if (index === 0) {
          fillPath.lineTo(x, y);
        } else {
          fillPath.lineTo(x, y);
        }
      });

      fillPath.lineTo(width - padding, height - padding);
      fillPath.closePath();

      const gradient = ctx.createLinearGradient(0, 0, 0, height);
      gradient.addColorStop(0, `${color}40`);
      gradient.addColorStop(1, `${color}05`);

      ctx.fillStyle = gradient;
      ctx.fill(fillPath);
    }

    // Draw line
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.stroke();

    // Draw dots if enabled
    if (showDots) {
      animatedData.forEach((point, index) => {
        const x = padding + index * xScale;
        const y = height - padding - ((point.value - minValue) * yScale);

        // Highlight the last point
        if (index === animatedData.length - 1) {
          ctx.beginPath();
          ctx.arc(x, y, 6, 0, 2 * Math.PI);
          ctx.fillStyle = color;
          ctx.fill();

          ctx.beginPath();
          ctx.arc(x, y, 4, 0, 2 * Math.PI);
          ctx.fillStyle = '#ffffff';
          ctx.fill();

          // Animated pulse for live data
          if (isLive && isAnimating) {
            ctx.beginPath();
            ctx.arc(x, y, 12, 0, 2 * Math.PI);
            ctx.strokeStyle = `${color}60`;
            ctx.lineWidth = 2;
            ctx.stroke();
          }
        } else {
          ctx.beginPath();
          ctx.arc(x, y, 3, 0, 2 * Math.PI);
          ctx.fillStyle = color;
          ctx.fill();
        }
      });
    }

    // Draw grid lines
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;

    // Horizontal grid lines
    for (let i = 0; i <= 4; i++) {
      const y = padding + (i * (height - 2 * padding)) / 4;
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.stroke();
    }

    // Value labels
    ctx.fillStyle = '#64748b';
    ctx.font = '12px Inter';
    ctx.textAlign = 'right';

    for (let i = 0; i <= 4; i++) {
      const value = maxValue - (i * range / 4);
      const y = padding + (i * (height - 2 * padding)) / 4;
      ctx.fillText(value.toLocaleString(), padding - 10, y + 4);
    }

  }, [animatedData, color, fillGradient, showDots, isLive, isAnimating]);

  // Simulate live data updates for demo
  useEffect(() => {
    if (!isLive || animatedData.length === 0) return;

    const interval = setInterval(() => {
      const lastPoint = animatedData[animatedData.length - 1];
      if (lastPoint) {
        // Simulate new data point
        const newValue = lastPoint.value + (Math.random() - 0.5) * (lastPoint.value * 0.02);
        const newPoint: DataPoint = {
          timestamp: new Date().toISOString(),
          value: Math.max(0, newValue)
        };

        setAnimatedData(prev => [...prev.slice(-(maxDataPoints - 1)), newPoint]);
      }
    }, 60000); // Changed from 2000ms to 60000ms to reduce re-renders

    return () => clearInterval(interval);
  }, [isLive, animatedData, maxDataPoints]);

  // Handle resize
  useEffect(() => {
    const handleResize = () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }

      animationRef.current = requestAnimationFrame(() => {
        // Redraw will happen automatically due to useEffect dependency
      });
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  const currentValue = animatedData.length > 0 ? animatedData[animatedData.length - 1].value : 0;
  const previousValue = animatedData.length > 1 ? animatedData[animatedData.length - 2].value : currentValue;
  const change = currentValue - previousValue;
  const changePercent = previousValue !== 0 ? (change / previousValue) * 100 : 0;

  return (
    <ChartContainer
      title={title}
      subtitle={subtitle}
      height={height + 100}
      className={className}
      headerActions={
        <div className="flex items-center space-x-4">
          {/* Current Value Display */}
          <div className="text-right">
            <motion.div
              className="text-lg font-bold text-slate-800"
              key={currentValue}
              initial={{ scale: 1.1, opacity: 0.8 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              {currentValue.toLocaleString()}
            </motion.div>
            <div className={`text-sm font-medium ${
              change > 0 ? 'text-emerald-600' : change < 0 ? 'text-red-600' : 'text-gray-600'
            }`}>
              {change > 0 ? '↗' : change < 0 ? '↘' : '→'} {Math.abs(changePercent).toFixed(2)}%
            </div>
          </div>

          {/* Live Indicator */}
          {isLive && (
            <div className="flex items-center space-x-2">
              <motion.div
                className="w-2 h-2 bg-emerald-400 rounded-full"
                animate={isAnimating ? { scale: [1, 1.5, 1] } : {}}
                transition={{ duration: 0.5, ease: "easeInOut" }}
              />
              <span className="text-xs text-emerald-600 font-medium">LIVE</span>
            </div>
          )}
        </div>
      }
    >
      <div className="relative w-full" style={{ height }}>
        <canvas
          ref={canvasRef}
          className="absolute inset-0 w-full h-full"
          style={{ width: '100%', height: '100%' }}
        />

        {/* Loading overlay */}
        <AnimatePresence>
          {animatedData.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 flex items-center justify-center bg-white/50 backdrop-blur-sm"
            >
              <div className="text-center">
                <div className="w-8 h-8 border-2 border-blue-200 border-t-blue-500 rounded-full animate-spin mx-auto mb-2"></div>
                <p className="text-sm text-slate-500">Loading chart data...</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </ChartContainer>
  );
};

export default RealTimeLineChart;