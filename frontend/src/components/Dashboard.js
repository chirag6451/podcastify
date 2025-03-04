import React from 'react';
import { Link } from 'react-router-dom';
import DriveView from './DriveView';
import GmailView from './GmailView';
import YouTubeView from './YouTubeView';

const Dashboard = () => {
    const userEmail = localStorage.getItem('userEmail');

    return (
        <div className="dashboard">
            <nav className="navbar navbar-expand-lg navbar-light bg-light mb-4">
                <div className="container-fluid">
                    <span className="navbar-brand">Dashboard</span>
                    <div className="navbar-nav ms-auto">
                        <a href="http://0.0.0.0:8011/manage_auth.html" className="nav-link" target="_blank">
                            <i className="bi bi-gear"></i> Manage Google Accounts
                        </a>
                        <span className="nav-link">
                            {userEmail}
                        </span>
                    </div>
                </div>
            </nav>

            <div className="container">
                <div className="row">
                    <div className="col-md-4">
                        <div className="card mb-4">
                            <div className="card-body">
                                <h5 className="card-title">Google Drive</h5>
                                <DriveView />
                            </div>
                        </div>
                    </div>
                    <div className="col-md-4">
                        <div className="card mb-4">
                            <div className="card-body">
                                <h5 className="card-title">Gmail</h5>
                                <GmailView />
                            </div>
                        </div>
                    </div>
                    <div className="col-md-4">
                        <div className="card mb-4">
                            <div className="card-body">
                                <h5 className="card-title">YouTube</h5>
                                <YouTubeView />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
