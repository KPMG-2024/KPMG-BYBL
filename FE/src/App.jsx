import { ChatContextProvider } from './context/chatContext';
import SideBar from './components/SideBar';
import RightSideBar from './components/RightSideBar';
import ChatView from './components/ChatView';
import Dashboard from './components/Dashboard';
import { useEffect, useState } from 'react';
import Modal from './components/Modal';
import Setting from './components/Setting';
import { DBContextProvider } from './context/DBContext';

const App = () => {
  // usestate : 컴포넌트 상태 관리를 용이하게 해줌
  const [modalOpen, setModalOpen] = useState(false);
  const [showDashboard, setShowDashboard] = useState(false); // New state for toggling display

  // api key 설정
  useEffect(() => {
    const apiKey = window.localStorage.getItem('api-key');
    if (!apiKey) {
      setModalOpen(true);
    }
  }, []);
  return (
    <ChatContextProvider>
      <DBContextProvider>
        {/* 처음 킬 경우 나오는 setting */}
        <Modal title='Setting' modalOpen={modalOpen} setModalOpen={setModalOpen}>
          <Setting modalOpen={modalOpen} setModalOpen={setModalOpen} />
        </Modal>
        
        <div className='flex transition duration-500 ease-in-out'>
            <SideBar setShowDashboard={setShowDashboard} showDashboard={showDashboard} /> 
            {showDashboard ? <Dashboard /> : <ChatView />} {/* Conditional rendering */}
            <RightSideBar style={{ flex: '1 1 30%' }} /> {/* 우측 사이드바 너비 조정 */}
        </div>
      </DBContextProvider>
    </ChatContextProvider>

  );
};

export default App;
