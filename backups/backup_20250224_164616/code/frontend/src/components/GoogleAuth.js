import React from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';

const API_URL = 'http://localhost:8011';

const GoogleAuth = () => {
    const navigate = useNavigate();

    const login = useGoogleLogin({
        onSuccess: async (codeResponse) => {
            console.log('Login Success:', codeResponse);
            try {
                // Send authorization code to our backend
                const response = await fetch(`${API_URL}/api/auth/google/callback`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        code: codeResponse.code
                    })
                });

                const data = await response.json();
                if (response.ok) {
                    console.log('Successfully authenticated:', data);
                    localStorage.setItem('userEmail', data.email);
                    localStorage.setItem('userId', data.user_id);
                    navigate('/dashboard');
                } else {
                    console.error('Authentication failed:', data);
                    alert('Authentication failed. Please try again.');
                }
            } catch (error) {
                console.error('Error during authentication:', error);
                alert('Error during authentication. Please try again.');
            }
        },
        onError: () => {
            console.log('Login Failed');
        },
        scope: 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile https://mail.google.com/ https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.compose https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/drive.appdata https://www.googleapis.com/auth/drive.metadata https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.force-ssl',
        flow: 'auth-code'
    });

    return (
        <div>
            <button onClick={() => login()} className="google-login-button">
                Sign in with Google
            </button>
        </div>
    );
};

export default GoogleAuth;
