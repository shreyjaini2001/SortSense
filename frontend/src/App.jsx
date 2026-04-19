import { BrowserRouter, Routes, Route } from 'react-router-dom'
import SorterView from './SorterView'
import OpsView from './OpsView'
import ArchView from './ArchView'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SorterView />} />
        <Route path="/ops" element={<OpsView />} />
        <Route path="/arch" element={<ArchView />} />
      </Routes>
    </BrowserRouter>
  )
}
