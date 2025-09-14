import React, { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChartContainer } from '../ui';

interface DonutSegment {
  name: string;
  value: number;
  color: string;
  percentage?: number;
}

interface RealTimeDonutChartProps {
  title: string;
  subtitle?: string;
  data: DonutSegment[];
  centerText?: string;
  centerValue?: string;
  isLive?: boolean;
  showLegend?: boolean;
  showPercentages?: boolean;
  height?: number;
  className?: string;
  onSegmentHover?: (segment: DonutSegment | null) => void;
}

const RealTimeDonutChart: React.FC<RealTimeDonutChartProps> = ({
  title,
  subtitle,
  data,
  centerText = 'Total',
  centerValue,
  isLive = true,
  showLegend = true,
  showPercentages = true,
  height = 350,
  className = '',
  onSegmentHover
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [animatedData, setAnimatedData] = useState<DonutSegment[]>([]);
  const [hoveredSegment, setHoveredSegment] = useState<DonutSegment | null>(null);
  const [animationProgress, setAnimationProgress] = useState(0);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Calculate percentages and animate data
  const processedData = useMemo(() => {
    const total = data.reduce((sum, item) => sum + item.value, 0);
    return data.map(item => ({
      ...item,
      percentage: total > 0 ? (item.value / total) * 100 : 0
    }));
  }, [data]);

  // Animate data changes
  useEffect(() => {
    const animateSegments = () => {
      setAnimationProgress(0);

      const startTime = Date.now();
      const duration = 1000;

      const animate = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);

        setAnimationProgress(progress);

        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          setAnimatedData(processedData);
        }
      };

      requestAnimationFrame(animate);
    };

    if (processedData.length > 0) {
      animateSegments();
    }
  }, [processedData]);

  // Draw donut chart
  useEffect(() => {
    if (!canvasRef.current || processedData.length === 0) return;

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
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 40;
    const innerRadius = radius * 0.6;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    let currentAngle = -Math.PI / 2; // Start from top

    processedData.forEach((segment, index) => {
      const angle = (segment.percentage / 100) * 2 * Math.PI * animationProgress;

      // Draw segment
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + angle);
      ctx.arc(centerX, centerY, innerRadius, currentAngle + angle, currentAngle, true);
      ctx.closePath();

      // Apply hover effect
      const isHovered = hoveredSegment?.name === segment.name;
      const segmentRadius = isHovered ? radius + 8 : radius;

      if (isHovered) {
        ctx.shadowColor = segment.color;
        ctx.shadowBlur = 15;
      } else {
        ctx.shadowColor = 'transparent';
        ctx.shadowBlur = 0;
      }

      ctx.fillStyle = segment.color;
      ctx.fill();

      // Draw segment with hover effect
      if (isHovered) {
        ctx.beginPath();
        ctx.arc(centerX, centerY, segmentRadius, currentAngle, currentAngle + angle);
        ctx.arc(centerX, centerY, innerRadius, currentAngle + angle, currentAngle, true);
        ctx.closePath();
        ctx.fill();
      }

      // Draw percentage labels
      if (showPercentages && segment.percentage > 5) {
        const labelAngle = currentAngle + angle / 2;
        const labelRadius = (radius + innerRadius) / 2;
        const labelX = centerX + Math.cos(labelAngle) * labelRadius;
        const labelY = centerY + Math.sin(labelAngle) * labelRadius;

        ctx.save();
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 12px Inter';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`${segment.percentage.toFixed(1)}%`, labelX, labelY);
        ctx.restore();
      }

      currentAngle += angle;
    });

    // Reset shadow
    ctx.shadowColor = 'transparent';
    ctx.shadowBlur = 0;

    // Draw center circle
    ctx.beginPath();
    ctx.arc(centerX, centerY, innerRadius, 0, 2 * Math.PI);
    ctx.fillStyle = '#ffffff';
    ctx.fill();

    // Draw center border
    ctx.beginPath();
    ctx.arc(centerX, centerY, innerRadius, 0, 2 * Math.PI);
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 2;
    ctx.stroke();

  }, [processedData, animationProgress, hoveredSegment, showPercentages]);

  // Handle mouse events
  const handleMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    setMousePosition({ x: event.clientX, y: event.clientY });

    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const radius = Math.min(rect.width, rect.height) / 2 - 40;
    const innerRadius = radius * 0.6;

    const distance = Math.sqrt((x - centerX) ** 2 + (y - centerY) ** 2);

    if (distance >= innerRadius && distance <= radius) {
      const angle = Math.atan2(y - centerY, x - centerX);
      const normalizedAngle = (angle + Math.PI / 2 + 2 * Math.PI) % (2 * Math.PI);

      let currentAngle = 0;
      for (const segment of processedData) {
        const segmentAngle = (segment.percentage / 100) * 2 * Math.PI;
        if (normalizedAngle >= currentAngle && normalizedAngle <= currentAngle + segmentAngle) {
          setHoveredSegment(segment);
          if (onSegmentHover) onSegmentHover(segment);
          return;
        }
        currentAngle += segmentAngle;
      }
    }

    setHoveredSegment(null);
    if (onSegmentHover) onSegmentHover(null);
  };

  const handleMouseLeave = () => {
    setHoveredSegment(null);
    if (onSegmentHover) onSegmentHover(null);
  };

  // Simulate real-time data updates
  useEffect(() => {
    if (!isLive || processedData.length === 0) return;

    const interval = setInterval(() => {
      // Simulate small changes in portfolio allocation
      setAnimatedData(prev => prev.map(segment => ({
        ...segment,
        value: Math.max(0, segment.value + (Math.random() - 0.5) * segment.value * 0.01)
      })));
    }, 60000); // Changed from 5000ms to 60000ms to reduce re-renders

    return () => clearInterval(interval);
  }, [isLive, processedData]);

  const totalValue = processedData.reduce((sum, item) => sum + item.value, 0);
  const displayValue = centerValue || totalValue.toLocaleString();

  return (
    <ChartContainer
      title={title}
      subtitle={subtitle}
      height={height + 100}
      className={className}
      headerActions={
        isLive && (
          <div className="flex items-center space-x-2">
            <motion.div
              className="w-2 h-2 bg-emerald-400 rounded-full"
              animate={{ scale: [1, 1.5, 1] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            />
            <span className="text-xs text-emerald-600 font-medium">LIVE</span>
          </div>
        )
      }
    >
      <div className="flex items-center space-x-8" style={{ height }}>
        {/* Chart Canvas */}
        <div className="relative flex-1">
          <canvas
            ref={canvasRef}
            className="w-full h-full cursor-pointer"
            style={{ height }}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
          />

          {/* Center Text */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="text-center">
              <div className="text-sm text-slate-600 font-medium mb-1">{centerText}</div>
              <motion.div
                className="text-2xl font-bold text-slate-800"
                key={displayValue}
                initial={{ scale: 1.1, opacity: 0.8 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.3 }}
              >
                {displayValue}
              </motion.div>
            </div>
          </div>

          {/* Loading overlay */}
          <AnimatePresence>
            {animationProgress < 1 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 flex items-center justify-center bg-white/50 backdrop-blur-sm"
              >
                <div className="text-center">
                  <div className="w-8 h-8 border-2 border-blue-200 border-t-blue-500 rounded-full animate-spin mx-auto mb-2"></div>
                  <p className="text-sm text-slate-500">Loading chart...</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Legend */}
        {showLegend && (
          <div className="flex-shrink-0 space-y-3 max-w-xs">
            {processedData.map((segment, index) => (
              <motion.div
                key={segment.name}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`flex items-center space-x-3 p-2 rounded-lg transition-colors cursor-pointer ${
                  hoveredSegment?.name === segment.name
                    ? 'bg-slate-100'
                    : 'hover:bg-slate-50'
                }`}
                onMouseEnter={() => setHoveredSegment(segment)}
                onMouseLeave={() => setHoveredSegment(null)}
              >
                <motion.div
                  className="w-4 h-4 rounded-full flex-shrink-0"
                  style={{ backgroundColor: segment.color }}
                  animate={hoveredSegment?.name === segment.name ? { scale: 1.2 } : { scale: 1 }}
                  transition={{ duration: 0.2 }}
                />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-slate-800 truncate">
                    {segment.name}
                  </div>
                  <div className="text-xs text-slate-500">
                    {segment.percentage?.toFixed(1)}% • {segment.value.toLocaleString()}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Tooltip */}
        <AnimatePresence>
          {hoveredSegment && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="fixed z-50 bg-slate-800 text-white px-3 py-2 rounded-lg shadow-lg pointer-events-none"
              style={{
                left: mousePosition.x + 10,
                top: mousePosition.y - 40,
                transform: 'translate(0, -100%)'
              }}
            >
              <div className="text-sm font-medium">{hoveredSegment.name}</div>
              <div className="text-xs opacity-80">
                {hoveredSegment.percentage?.toFixed(1)}% • ₹{hoveredSegment.value.toLocaleString()}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </ChartContainer>
  );
};

export default RealTimeDonutChart;