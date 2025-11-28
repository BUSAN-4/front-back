import { useEffect, useRef } from 'react';
import * as pbi from 'powerbi-client';
import type { PowerBIConfig } from '../../../types/dashboard';

interface PowerBIEmbedViewProps {
  config: PowerBIConfig | null;
  height?: string;
}

export default function PowerBIEmbedView({ config, height = '800px' }: PowerBIEmbedViewProps) {
  const embedContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!embedContainerRef.current || !config) return;

    const powerbi = new pbi.service.Service(
      pbi.factories.hpmFactory,
      pbi.factories.wpmpFactory,
      pbi.factories.routerFactory
    );

    const embedConfig: pbi.models.IEmbedConfiguration = {
      type: 'report',
      tokenType: pbi.models.TokenType.Embed,
      accessToken: config.accessToken,
      embedUrl: config.embedUrl,
      id: config.embedId,
      settings: {
        panes: {
          filters: { expanded: false, visible: false },
          pageNavigation: { visible: true },
        },
      },
    };

    const report = powerbi.embed(embedContainerRef.current, embedConfig);

    return () => {
      try {
        report.off('loaded');
      } catch (error) {
        console.error('PowerBI cleanup error:', error);
      }
    };
  }, [config]);

  if (!config) {
    return <div>PowerBI 설정을 불러오는 중...</div>;
  }

  return (
    <div
      ref={embedContainerRef}
      style={{
        width: '100%',
        height,
        border: '1px solid #e0e0e0',
        borderRadius: '4px',
      }}
    />
  );
}

