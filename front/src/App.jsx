import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Register from './components/Auth/register';
import Login from './components/Auth/login';
import Reserva from './components/Reserva/reseva';
import UserProfile from './components/UserProfile/UserProfile';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/reserva" element={<Reserva />} />
        <Route path="/profile" element={<UserProfile />} />
        <Route path="/" element={<Login />} />
      </Routes>
    </Router>
  );
}

export default App;