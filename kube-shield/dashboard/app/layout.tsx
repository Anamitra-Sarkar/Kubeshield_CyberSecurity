import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Kube-Shield | Zero-Trust Security Dashboard',
  description: 'Production-grade Zero-Trust Kubernetes Security Operator',
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="font-sans bg-slate-950 text-slate-100 antialiased">
        {children}
      </body>
    </html>
  );
}
