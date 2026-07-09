import React from 'react';
import Header from './components/Layout/Header';
import LogInteraction from './pages/LogInteraction/LogInteraction';

function App() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <LogInteraction />
      </main>
    </div>
  );
}

export default App;
