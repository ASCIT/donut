import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// Mount the React app when the DOM is ready
const mountApp = () => {
  const rootElement = document.getElementById('gpt-sam-root')
  if (rootElement) {
    ReactDOM.createRoot(rootElement).render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    )
  }
}

// Check if DOM is already loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', mountApp)
} else {
  mountApp()
}
