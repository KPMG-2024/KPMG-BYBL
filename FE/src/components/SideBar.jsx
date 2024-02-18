import { useState, useEffect, useContext } from 'react';
import {
  MdClose,
  MdMenu,
  MdOutlineCoffee,
  MdOutlineVpnKey,
  MdDelete,
  MdDashboard
} from 'react-icons/md';
import { AiOutlineGithub } from 'react-icons/ai';
import { ChatContext } from '../context/chatContext';
import bot from '../assets/logo.svg';
import logo_text from '../assets/logo.png';
import ToggleTheme from './ToggleTheme';
import Modal from './Modal';
import Setting from './Setting';

/**
 * A sidebar component that displays a list of nav items and a toggle
 * for switching between light and dark modes.
 *
 * @param {Object} props - The properties for the component.
 */
const SideBar = ({ setShowDashboard, showDashboard }) => {
  const [open, setOpen] = useState(true);
  const [, , clearChat] = useContext(ChatContext);
  const [modalOpen, setModalOpen] = useState(false);
  // Function to toggle the dashboard view
  const toggleDashboard = () => {
    setShowDashboard(prevState => !prevState); // Toggle the showDashboard state
  };

  const iconBaseClass = 'border border-slate-500';
  // Define a class for active state
  const iconActiveClass = 'text-white bg-blue-600 border-blue-600 shadow-md'; 

  function handleResize() {
    window.innerWidth <= 720 ? setOpen(false) : setOpen(true);
  }

  useEffect(() => {
    handleResize();
  }, []);

  function clear() {
    clearChat();
  }

  return (
    <section
      className={`${
        open ? 'w-72' : 'w-16'
      } bg-neutral flex flex-col items-center gap-y-4 h-screen pt-4 relative duration-100 shadow-md`}>
      <div className='flex items-center justify-between w-full px-2 mx-auto'>
        <div
          className={` ${
            !open && 'scale-0 hidden'
          } flex flex-row items-center gap-2 mx-auto w-full`}>
          <img src={bot} alt='logo' className='w-10 h-10' />
          <h1 className={` ${!open && 'scale-0 hidden'}`}>BYBL</h1>
        </div>
        <div
          className='mx-auto btn btn-square btn-ghost'
          onClick={() => setOpen(!open)}>
          {open ? <MdClose size={20} /> : <MdMenu size={20} />}
        </div>
      </div>

      <ul className='w-full menu rounded-box'>
        <li className="my-1">
          <a className={`${iconBaseClass} ${showDashboard ? iconActiveClass : ''}`} onClick={toggleDashboard}>
            <MdDashboard size={20} />
            <p className={`${!open && 'hidden'}`}>대시보드</p>
          </a>
        </li>
        <li className="my-1">
          <a className='border border-slate-500' onClick={clear}>
            <MdDelete size={20} />
            <p className={`${!open && 'hidden'}`}>Clear chat</p>
          </a>
        </li>
      </ul>

      <ul className='absolute bottom-0 w-full gap-1 menu rounded-box'>
        <li>
          <ToggleTheme open={open} />
        </li>
        <li>
          <a onClick={() => setModalOpen(true)}>
            <MdOutlineVpnKey size={15} />
            <p className={`${!open && 'hidden'}`}>OpenAI Key</p>
          </a>
        </li>
      </ul>
      <Modal title='Setting' modalOpen={modalOpen} setModalOpen={setModalOpen}>
        <Setting modalOpen={modalOpen} setModalOpen={setModalOpen} />
      </Modal>
    </section>
  );
};

export default SideBar;
