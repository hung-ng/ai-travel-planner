
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Link from 'next/link';
import UserMenu from '@/components/UserMenu'; 

const inter = Inter({
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'AI Travel Planner',
  description: 'Plan your trips with AI assistance',
};


export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang='en'>
      <body className={inter.className}>
        <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
          <div className="px-8 py-3 flex items-center justify-between">
            <Link href="/" className="text-2xl font-bold flex items-center gap-2">
              <span>🌍</span>
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">AI Travel Planner</span>
            </Link>
            <UserMenu />
          </div>
        </nav>
        
        {children}
      </body>
    </html>
  );
}

