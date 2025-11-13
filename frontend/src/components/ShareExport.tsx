'use client';

import { useState } from 'react';
import { Trip } from '@/types';

interface ExportShareProps {
  trip: Trip;
  messages?: Array<{ role: string; content: string; timestamp: Date }>;
}

export default function ExportShare({ trip, messages = [] }: ExportShareProps) {
  const [showShareMenu, setShowShareMenu] = useState(false);
  const [copied, setCopied] = useState(false);

  // shareable link
  const generateShareLink = () => {
    const baseUrl = window.location.origin;
    return `${baseUrl}/trip/${trip.id}`;
  };

  // copy link to clipboard
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(generateShareLink());
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // export chat as text
  const exportAsText = () => {
    const content = `
AI Travel Planner - Trip Summary
================================

Destination: ${trip.destination}
Dates: ${new Date(trip.start_date).toLocaleDateString()} - ${new Date(trip.end_date).toLocaleDateString()}
Budget: ${trip.budget ? `$${trip.budget}` : 'Not specified'}
Status: ${trip.status}

Chat History:
-------------

${messages.map((msg, idx) => `
[${msg.role.toUpperCase()}] ${msg.timestamp.toLocaleString()}
${msg.content}
`).join('\n---\n')}

Generated: ${new Date().toLocaleString()}
    `.trim();

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `trip-${trip.destination.replace(/\s+/g, '-')}-${trip.id}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // export as JSON
  const exportAsJSON = () => {
    const data = {
      trip,
      messages,
      exportDate: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `trip-${trip.destination.replace(/\s+/g, '-')}-${trip.id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // print  PDF export
  const exportAsPDF = () => {
    const printContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Trip: ${trip.destination}</title>
          <style>
            body {
              font-family: Arial, sans-serif;
              max-width: 800px;
              margin: 40px auto;
              padding: 20px;
              line-height: 1.6;
            }
            .header {
              border-bottom: 3px solid #3b82f6;
              padding-bottom: 20px;
              margin-bottom: 30px;
            }
            h1 {
              color: #1e40af;
              margin: 0;
            }
            .info-grid {
              display: grid;
              grid-template-columns: repeat(2, 1fr);
              gap: 15px;
              margin: 20px 0;
            }
            .info-item {
              padding: 10px;
              background: #f3f4f6;
              border-radius: 8px;
            }
            .info-label {
              font-weight: bold;
              color: #4b5563;
              font-size: 12px;
              text-transform: uppercase;
            }
            .info-value {
              color: #1f2937;
              font-size: 16px;
            }
            .message {
              margin: 20px 0;
              padding: 15px;
              border-left: 4px solid #3b82f6;
              background: #f9fafb;
            }
            .message.user {
              border-left-color: #8b5cf6;
              background: #faf5ff;
            }
            .message-header {
              font-weight: bold;
              color: #374151;
              margin-bottom: 8px;
            }
            .footer {
              margin-top: 40px;
              padding-top: 20px;
              border-top: 1px solid #e5e7eb;
              text-align: center;
              color: #6b7280;
              font-size: 12px;
            }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>🌍 ${trip.destination}</h1>
            <p style="color: #6b7280; margin: 10px 0 0 0;">AI Travel Planner - Trip Summary</p>
          </div>

          <div class="info-grid">
            <div class="info-item">
              <div class="info-label">Travel Dates</div>
              <div class="info-value">${new Date(trip.start_date).toLocaleDateString()} - ${new Date(trip.end_date).toLocaleDateString()}</div>
            </div>
            <div class="info-item">
              <div class="info-label">Budget</div>
              <div class="info-value">${trip.budget ? `$${trip.budget.toLocaleString()}` : 'Not specified'}</div>
            </div>
            <div class="info-item">
              <div class="info-label">Status</div>
              <div class="info-value" style="text-transform: capitalize;">${trip.status}</div>
            </div>
            <div class="info-item">
              <div class="info-label">Trip ID</div>
              <div class="info-value">#${trip.id}</div>
            </div>
          </div>

          <h2 style="margin-top: 40px; color: #1e40af;">Chat History</h2>
          ${messages.map(msg => `
            <div class="message ${msg.role}">
              <div class="message-header">
                ${msg.role === 'user' ? '👤 You' : '🤖 AI Assistant'} 
                • ${msg.timestamp.toLocaleString()}
              </div>
              <div>${msg.content}</div>
            </div>
          `).join('')}

          <div class="footer">
            <p>Generated on ${new Date().toLocaleString()}</p>
            <p>Powered by AI Travel Planner</p>
          </div>
        </body>
      </html>
    `;

    const printWindow = window.open('', '_blank');
    if (printWindow) {
      printWindow.document.write(printContent);
      printWindow.document.close();
      
      printWindow.onload = () => {
        printWindow.print();
      };
    }
  };

  // share w email
  const shareViaEmail = () => {
    const subject = encodeURIComponent(`Check out my trip to ${trip.destination}!`);
    const body = encodeURIComponent(`
I'm planning a trip to ${trip.destination}!

Dates: ${new Date(trip.start_date).toLocaleDateString()} - ${new Date(trip.end_date).toLocaleDateString()}
Budget: ${trip.budget ? `$${trip.budget}` : 'TBD'}

View my trip: ${generateShareLink()}

Created with AI Travel Planner
    `.trim());

    window.location.href = `mailto:?subject=${subject}&body=${body}`;
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowShareMenu(!showShareMenu)}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <span>📤</span>
        <span className="font-medium text-gray-700">Export & Share</span>
      </button>

      {/* Dropdown Menu */}
      {showShareMenu && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setShowShareMenu(false)}
          />
          
          {/* Menu */}
          <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-xl border border-gray-200 z-20">
            <div className="p-2">
              {/* Export  */}
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase">
                Export
              </div>

              <button
                onClick={() => {
                  exportAsPDF();
                  setShowShareMenu(false);
                }}
                className="w-full flex items-center gap-3 px-3 py-2 text-left hover:bg-gray-100 rounded-lg transition-colors"
              >
                <span className="text-xl">📄</span>
                <div>
                  <div className="font-medium text-gray-900">Export as PDF</div>
                  <div className="text-xs text-gray-500">Print-friendly format</div>
                </div>
              </button>

              <button
                onClick={() => {
                  exportAsText();
                  setShowShareMenu(false);
                }}
                className="w-full flex items-center gap-3 px-3 py-2 text-left hover:bg-gray-100 rounded-lg transition-colors"
              >
                <span className="text-xl">📝</span>
                <div>
                  <div className="font-medium text-gray-900">Export as Text</div>
                  <div className="text-xs text-gray-500">Plain text file</div>
                </div>
              </button>

              <button
                onClick={() => {
                  exportAsJSON();
                  setShowShareMenu(false);
                }}
                className="w-full flex items-center gap-3 px-3 py-2 text-left hover:bg-gray-100 rounded-lg transition-colors"
              >
                <span className="text-xl">💾</span>
                <div>
                  <div className="font-medium text-gray-900">Export as JSON</div>
                  <div className="text-xs text-gray-500">Raw data format</div>
                </div>
              </button>

              <div className="border-t border-gray-200 my-2"></div>

              {/* Share */}
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase">
                Share
              </div>

              <button
                onClick={() => {
                  copyToClipboard();
                }}
                className="w-full flex items-center gap-3 px-3 py-2 text-left hover:bg-gray-100 rounded-lg transition-colors"
              >
                <span className="text-xl">{copied ? '✅' : '🔗'}</span>
                <div>
                  <div className="font-medium text-gray-900">
                    {copied ? 'Link Copied!' : 'Copy Link'}
                  </div>
                  <div className="text-xs text-gray-500">Share with friends</div>
                </div>
              </button>

              <button
                onClick={() => {
                  shareViaEmail();
                  setShowShareMenu(false);
                }}
                className="w-full flex items-center gap-3 px-3 py-2 text-left hover:bg-gray-100 rounded-lg transition-colors"
              >
                <span className="text-xl">📧</span>
                <div>
                  <div className="font-medium text-gray-900">Share via Email</div>
                  <div className="text-xs text-gray-500">Send to inbox</div>
                </div>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}