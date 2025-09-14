import { useCallback, useEffect, useMemo, useRef } from 'react';

interface PerformanceOptions {
  enableVirtualization?: boolean;
  debounceDelay?: number;
  throttleDelay?: number;
  enableLazyLoading?: boolean;
}

export const useDebounce = <T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T => {
  const debounceTimerRef = useRef<NodeJS.Timeout>();

  return useCallback(
    ((...args: Parameters<T>) => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }

      debounceTimerRef.current = setTimeout(() => {
        callback(...args);
      }, delay);
    }) as T,
    [callback, delay]
  );
};

export const useThrottle = <T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T => {
  const isThrottledRef = useRef(false);

  return useCallback(
    ((...args: Parameters<T>) => {
      if (!isThrottledRef.current) {
        callback(...args);
        isThrottledRef.current = true;

        setTimeout(() => {
          isThrottledRef.current = false;
        }, delay);
      }
    }) as T,
    [callback, delay]
  );
};

export const useMemoizedValue = <T>(
  computeFn: () => T,
  deps: React.DependencyList
): T => {
  return useMemo(computeFn, deps);
};

export const usePerformanceOptimization = (options: PerformanceOptions = {}) => {
  const {
    debounceDelay = 300,
    throttleDelay = 100,
    enableLazyLoading = true,
  } = options;

  // Performance monitoring
  const performanceRef = useRef({
    renderCount: 0,
    lastRenderTime: 0,
    averageRenderTime: 0,
  });

  useEffect(() => {
    performanceRef.current.renderCount += 1;
    const now = performance.now();

    if (performanceRef.current.lastRenderTime > 0) {
      const renderTime = now - performanceRef.current.lastRenderTime;
      performanceRef.current.averageRenderTime =
        (performanceRef.current.averageRenderTime + renderTime) / 2;
    }

    performanceRef.current.lastRenderTime = now;
  });

  // Intersection Observer for lazy loading
  const intersectionObserver = useMemo(() => {
    if (!enableLazyLoading || typeof window === 'undefined') return null;

    return new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const target = entry.target as HTMLElement;
            target.classList.add('visible');

            // Load lazy content
            const lazyElements = target.querySelectorAll('[data-lazy]');
            lazyElements.forEach((element) => {
              const src = element.getAttribute('data-lazy');
              if (src && element instanceof HTMLImageElement) {
                element.src = src;
                element.removeAttribute('data-lazy');
              }
            });
          }
        });
      },
      {
        rootMargin: '50px',
        threshold: 0.1,
      }
    );
  }, [enableLazyLoading]);

  // Lazy loading hook
  const observeElement = useCallback(
    (element: HTMLElement | null) => {
      if (element && intersectionObserver) {
        intersectionObserver.observe(element);

        return () => {
          intersectionObserver.unobserve(element);
        };
      }
    },
    [intersectionObserver]
  );

  // Memory cleanup
  useEffect(() => {
    return () => {
      if (intersectionObserver) {
        intersectionObserver.disconnect();
      }
    };
  }, [intersectionObserver]);

  // Frame rate optimization
  const requestAnimationFrameRef = useRef<number>();

  const optimizedAnimationFrame = useCallback((callback: FrameRequestCallback) => {
    if (requestAnimationFrameRef.current) {
      cancelAnimationFrame(requestAnimationFrameRef.current);
    }

    requestAnimationFrameRef.current = requestAnimationFrame(callback);

    return () => {
      if (requestAnimationFrameRef.current) {
        cancelAnimationFrame(requestAnimationFrameRef.current);
      }
    };
  }, []);

  // Batch state updates
  const batchUpdates = useCallback((updateFunctions: Array<() => void>) => {
    // Use React 18's automatic batching or manual batching for older versions
    Promise.resolve().then(() => {
      updateFunctions.forEach(fn => fn());
    });
  }, []);

  // Virtual scrolling helper
  const calculateVisibleItems = useCallback(
    (
      containerHeight: number,
      itemHeight: number,
      scrollTop: number,
      totalItems: number,
      overscan: number = 5
    ) => {
      const visibleStart = Math.floor(scrollTop / itemHeight);
      const visibleEnd = Math.min(
        visibleStart + Math.ceil(containerHeight / itemHeight),
        totalItems - 1
      );

      return {
        start: Math.max(0, visibleStart - overscan),
        end: Math.min(totalItems - 1, visibleEnd + overscan),
        offsetY: Math.max(0, visibleStart - overscan) * itemHeight,
      };
    },
    []
  );

  return {
    // Performance utilities
    debounce: (callback: (...args: any[]) => any) =>
      useDebounce(callback, debounceDelay),

    throttle: (callback: (...args: any[]) => any) =>
      useThrottle(callback, throttleDelay),

    memoize: useMemoizedValue,

    // Lazy loading
    observeElement,

    // Animation optimization
    optimizedAnimationFrame,

    // State optimization
    batchUpdates,

    // Virtual scrolling
    calculateVisibleItems,

    // Performance metrics
    getPerformanceMetrics: () => ({
      renderCount: performanceRef.current.renderCount,
      averageRenderTime: performanceRef.current.averageRenderTime,
    }),
  };
};

// Higher-order component for performance optimization
export const withPerformanceOptimization = <P extends object>(
  Component: React.ComponentType<P>,
  options: PerformanceOptions = {}
) => {
  return React.memo((props: P) => {
    const performanceHooks = usePerformanceOptimization(options);

    return (
      <Component
        {...props}
        performanceUtils={performanceHooks}
      />
    );
  });
};

export default usePerformanceOptimization;