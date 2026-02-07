import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { LLMConfigPage } from './pages/LLMConfig';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/llm-config" element={<LLMConfigPage />} />
      </Routes>
    </Router>
  );
}

export default App;
