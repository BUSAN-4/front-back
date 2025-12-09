import { useEffect, useState } from 'react';
import type { PowerBIConfig } from '../types/dashboard';

export const usePowerBI = (reportId: string) => {
  const [config, setConfig] = useState<PowerBIConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchToken = async () => {
      try {
        setLoading(true);
        await new Promise((resolve) => setTimeout(resolve, 1000));
        setConfig(null);
        setError(null);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    if (reportId) {
      fetchToken();
    }
  }, [reportId]);

  return { config, loading, error };
};




