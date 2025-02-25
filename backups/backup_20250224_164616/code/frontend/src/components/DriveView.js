import React, { useState, useEffect } from 'react';

const DriveView = ({ accessToken }) => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const response = await fetch(
          'https://www.googleapis.com/drive/v3/files?pageSize=10&fields=files(id,name,mimeType,webViewLink,createdTime)',
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch files');
        }

        const data = await response.json();
        setFiles(data.files);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    if (accessToken) {
      fetchFiles();
    }
  }, [accessToken]);

  if (loading) return <div>Loading files...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="drive-container">
      <h2>Recent Files</h2>
      <div className="file-list">
        {files.map((file) => (
          <div key={file.id} className="file-item">
            <h3>{file.name}</h3>
            <p>Type: {file.mimeType}</p>
            <p>Created: {new Date(file.createdTime).toLocaleDateString()}</p>
            {file.webViewLink && (
              <a href={file.webViewLink} target="_blank" rel="noopener noreferrer">
                View File
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default DriveView;
