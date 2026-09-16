import { AnimatePresence } from 'framer-motion'
import { Route, Routes, useLocation } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Optimizer from './pages/Optimizer.jsx'
import Projections from './pages/Projections.jsx'

export default function App() {
  const location = useLocation()

  return (
    <Layout>
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<Projections />} />
          <Route path="/optimizer" element={<Optimizer />} />
        </Routes>
      </AnimatePresence>
    </Layout>
  )
}
