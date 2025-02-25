import React, { useState, useEffect } from 'react';

const GmailView = ({ accessToken }) => {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchEmails = async () => {
      try {
        const response = await fetch(
          'https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=10',
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch emails');
        }

        const data = await response.json();
        
        // Fetch details for each email
        const emailPromises = data.messages.map(async (message) => {
          const detailResponse = await fetch(
            `https://gmail.googleapis.com/gmail/v1/users/me/messages/${message.id}`,
            {
              headers: {
                Authorization: `Bearer ${accessToken}`,
              },
            }
          );
          return detailResponse.json();
        });

        const emailDetails = await Promise.all(emailPromises);
        setEmails(emailDetails);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    if (accessToken) {
      fetchEmails();
    }
  }, [accessToken]);

  if (loading) return <div>Loading emails...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="gmail-container">
      <h2>Recent Emails</h2>
      <div className="email-list">
        {emails.map((email) => (
          <div key={email.id} className="email-item">
            <h3>{email.payload.headers.find(h => h.name.toLowerCase() === 'subject')?.value || 'No Subject'}</h3>
            <p>From: {email.payload.headers.find(h => h.name.toLowerCase() === 'from')?.value || 'Unknown Sender'}</p>
            <p>Date: {email.payload.headers.find(h => h.name.toLowerCase() === 'date')?.value || 'No Date'}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GmailView;
