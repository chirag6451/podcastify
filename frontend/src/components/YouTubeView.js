import React, { useState, useEffect } from 'react';

const YouTubeView = ({ accessToken }) => {
  const [playlists, setPlaylists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPlaylists = async () => {
      try {
        const response = await fetch(
          'https://www.googleapis.com/youtube/v3/playlists?part=snippet&mine=true&maxResults=10',
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch playlists');
        }

        const data = await response.json();
        setPlaylists(data.items);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    if (accessToken) {
      fetchPlaylists();
    }
  }, [accessToken]);

  if (loading) return <div>Loading playlists...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="youtube-container">
      <h2>Your YouTube Playlists</h2>
      <div className="playlist-list">
        {playlists.map((playlist) => (
          <div key={playlist.id} className="playlist-item">
            <h3>{playlist.snippet.title}</h3>
            <p>{playlist.snippet.description}</p>
            {playlist.snippet.thumbnails?.default && (
              <img
                src={playlist.snippet.thumbnails.default.url}
                alt={playlist.snippet.title}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default YouTubeView;
