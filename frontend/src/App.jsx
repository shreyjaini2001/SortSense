import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import SorterView from './SorterView'
import OpsView from './OpsView'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SorterView />} />
        <Route path="/ops" element={<OpsView />} />
      </Routes>
    </BrowserRouter>
  )
}
