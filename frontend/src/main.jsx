import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import { SleeperProvider } from './context/SleeperContext.jsx'
import './index.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <SleeperProvider>
        <App />
      </SleeperProvider>
    </BrowserRouter>
  </StrictMode>,
)
