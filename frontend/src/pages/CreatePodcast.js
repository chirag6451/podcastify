import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://0.0.0.0:8011/api';

function CreatePodcast() {
    const navigate = useNavigate();
    const [channels, setChannels] = useState([]);
    const [playlists, setPlaylists] = useState([]);
    const [status, setStatus] = useState({ message: '', type: '' });
    const customerId = localStorage.getItem('customerId');

    useEffect(() => {
        if (!customerId) {
            navigate('/manage_auth');
            return;
        }
        loadChannels();
    }, [customerId, navigate]);

    const loadChannels = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/publish/youtube/channels?user_email=${encodeURIComponent(customerId)}`);
            if (response.ok) {
                const data = await response.json();
                setChannels(data);
                if (data.length > 0) {
                    loadPlaylists(data[0].id);
                }
            }
        } catch (error) {
            console.error('Error loading YouTube channels:', error);
            setStatus({ message: 'Error loading YouTube channels', type: 'danger' });
        }
    };

    const loadPlaylists = async (channelId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/publish/youtube/playlists/${channelId}?user_email=${encodeURIComponent(customerId)}`);
            if (response.ok) {
                const data = await response.json();
                setPlaylists(data);
            }
        } catch (error) {
            console.error('Error loading playlists:', error);
            setStatus({ message: 'Error loading playlists', type: 'danger' });
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const formData = {
            profile_name: e.target.profile_name.value,
            conversation_type: e.target.conversation_type.value,
            customer_id: customerId,
            youtube_channel_id: e.target.youtube_channel_id.value,
            youtube_playlist_id: e.target.youtube_playlist_id.value || null,
            topic: e.target.topic.value,
            title: e.target.title.value,
            sub_title: e.target.sub_title.value,
            theme: e.target.theme.value,
            voice_settings_num_turns: parseInt(e.target.voice_settings_num_turns.value),
            voice_settings_conversation_mood: e.target.voice_settings_conversation_mood.value,
            voice_settings_language: e.target.voice_settings_language.value,
            voice_settings_voice_accent: e.target.voice_settings_voice_accent.value,
            video_type: e.target.video_type.value,
            main_video_style: e.target.main_video_style.value
        };

        try {
            const response = await fetch(`${API_BASE_URL}/podcasts/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': 'indapoint2025',
                    'accept': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            if (response.ok) {
                setStatus({ message: `Podcast created successfully! Job ID: ${result.job_id}`, type: 'success' });
            } else {
                setStatus({ message: `Error: ${result.detail || 'Unknown error'}`, type: 'danger' });
            }
        } catch (error) {
            setStatus({ message: `Error: ${error.message}`, type: 'danger' });
        }
    };

    return (
        <div className="container mt-5">
            <h2 className="mb-4">Create New Podcast</h2>
            
            <div className="card">
                <div className="card-body">
                    <form onSubmit={handleSubmit}>
                        <div className="row mb-3">
                            <div className="col-md-6">
                                <label className="form-label">Topic</label>
                                <textarea className="form-control" name="topic" rows="3" required />
                            </div>
                            <div className="col-md-6">
                                <label className="form-label">Title</label>
                                <input type="text" className="form-control" name="title" required />
                            </div>
                        </div>

                        <div className="row mb-3">
                            <div className="col-md-6">
                                <label className="form-label">Subtitle</label>
                                <input type="text" className="form-control" name="sub_title" required />
                            </div>
                            <div className="col-md-6">
                                <label className="form-label">Profile Name</label>
                                <input type="text" className="form-control" name="profile_name" defaultValue="indapoint" required />
                            </div>
                        </div>

                        <div className="row mb-3">
                            <div className="col-md-6">
                                <label className="form-label">YouTube Channel</label>
                                <select 
                                    className="form-select" 
                                    name="youtube_channel_id" 
                                    onChange={(e) => loadPlaylists(e.target.value)}
                                    required
                                >
                                    <option value="">Select a channel</option>
                                    {channels.map(channel => (
                                        <option key={channel.id} value={channel.id}>
                                            {channel.title || channel.id}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div className="col-md-6">
                                <label className="form-label">YouTube Playlist</label>
                                <select className="form-select" name="youtube_playlist_id">
                                    <option value="">Select a playlist</option>
                                    {playlists.map(playlist => (
                                        <option key={playlist.id} value={playlist.id}>
                                            {playlist.title} ({playlist.itemCount} items)
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div className="row mb-3">
                            <div className="col-md-4">
                                <label className="form-label">Theme</label>
                                <select className="form-select" name="theme" required>
                                    <option value="dark">Dark</option>
                                    <option value="light">Light</option>
                                </select>
                            </div>
                            <div className="col-md-4">
                                <label className="form-label">Number of Turns</label>
                                <input type="number" className="form-control" name="voice_settings_num_turns" defaultValue="10" required />
                            </div>
                            <div className="col-md-4">
                                <label className="form-label">Language</label>
                                <input type="text" className="form-control" name="voice_settings_language" defaultValue="en" required />
                            </div>
                        </div>

                        <div className="row mb-3">
                            <div className="col-md-4">
                                <label className="form-label">Conversation Mood</label>
                                <select className="form-select" name="voice_settings_conversation_mood" required>
                                    <option value="neutral">Neutral</option>
                                    <option value="excited">Excited</option>
                                    <option value="professional">Professional</option>
                                </select>
                            </div>
                            <div className="col-md-4">
                                <label className="form-label">Voice Accent</label>
                                <select className="form-select" name="voice_settings_voice_accent" required>
                                    <option value="neutral">Neutral</option>
                                    <option value="british">British</option>
                                    <option value="american">American</option>
                                </select>
                            </div>
                            <div className="col-md-4">
                                <label className="form-label">Conversation Type</label>
                                <select className="form-select" name="conversation_type" required>
                                    <option value="podcast">Podcast</option>
                                </select>
                            </div>
                        </div>

                        <div className="row mb-3">
                            <div className="col-md-6">
                                <label className="form-label">Video Type</label>
                                <select className="form-select" name="video_type" required>
                                    <option value="podcast">Podcast</option>
                                </select>
                            </div>
                            <div className="col-md-6">
                                <label className="form-label">Main Video Style</label>
                                <select className="form-select" name="main_video_style" required>
                                    <option value="video">Video</option>
                                    <option value="images">Images</option>
                                </select>
                            </div>
                        </div>

                        <div className="d-flex justify-content-between">
                            <button type="submit" className="btn btn-primary">Create Podcast</button>
                            {status.message && (
                                <div className={`alert alert-${status.type}`}>
                                    {status.message}
                                </div>
                            )}
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default CreatePodcast;
