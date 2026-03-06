import React from 'react';
import ReactDOM from 'react-dom/client';
import { Amplify } from 'aws-amplify';
import awsConfig from './aws-config';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

// Configure Amplify
Amplify.configure(awsConfig);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

reportWebVitals();
