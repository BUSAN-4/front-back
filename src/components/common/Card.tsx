import { Card as MuiCard, CardContent, CardHeader, CardActions, Box, Typography } from '@mui/material';

interface CardProps {
  title?: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
}

export default function Card({ title, children, actions }: CardProps) {
  return (
    <MuiCard
      sx={{
        borderRadius: 2,
        boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
        transition: 'transform 0.2s ease-in-out',
        '&:hover': {
          transform: 'translateY(-4px)',
        },
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {title && (
        <CardHeader
          title={title}
          titleTypographyProps={{ variant: 'h6', fontWeight: 'bold', color: 'white' }}
          sx={{ bgcolor: 'primary.main', color: 'white', py: 1.5, px: 2, borderTopLeftRadius: 8, borderTopRightRadius: 8 }}
        />
      )}
      <CardContent sx={{ flexGrow: 1 }}>{children}</CardContent>
      {actions && <CardActions sx={{ p: 2, borderTop: '1px solid #eee' }}>{actions}</CardActions>}
    </MuiCard>
  );
}

