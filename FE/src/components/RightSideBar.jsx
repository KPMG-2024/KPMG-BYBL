import React, { useState, useEffect, useContext } from 'react';
import { MdOutlineVpnKey, MdFileCopy, MdStorage, MdEmail, MdDelete } from 'react-icons/md';
import { ChatContext } from '../context/chatContext';
import { DBContext } from '../context/DBContext'; // 경로는 프로젝트 구조에 따라 다를 수 있습니다.
import Modal from './Modal';
import Email from './Email';
import PropTypes from 'prop-types';

/**
 * A sidebar component that displays a list of nav items and a toggle
 * for switching between light and dark modes.
 *
 * @param {Object} props - The properties for the component.
 */

const RightSideBar = () => {
  const [open, setOpen] = useState(true);
  const [messages, , clearChat] = useContext(ChatContext);
  const [DBs, , clearDB] = useContext(DBContext);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedDB, setSelectedDB] = useState('archive'); // 'archive' or 'buyer'
  const [buyerDB, setBuyerDB] = useState([]); // 바이어 DB 데이터를 위한 상태


  function handleResize() {
    window.innerWidth <= 720 ? setOpen(false) : setOpen(true);
  }

  function clear() {
    clearDB();
  }

  function uploadDataToMongoDB(DBs) {
    fetch('http://localhost:3000/api/archive/upload', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(DBs), // DBs는 업로드할 데이터를 담고 있는 배열
    })
    .then(response => {
      if (response.ok) {
        alert('아카이브를 업로드해두었습니다.'); // 성공 알림
        return response.json();
      }
      throw new Error('Network response was not ok.');
    })
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
  }

  function clearDBOnServer() {
    fetch('http://localhost:3000/api/archive/clear', {
      method: 'DELETE', // 데이터를 비우기 위해 DELETE 메소드 사용
    })
    .then(response => {
      if (response.ok) {
        // 응답 성공 시 clear 함수 호출, 응답 데이터에 관계없음
        clear();
      } else {
        // 서버 응답이 OK가 아닐 경우 오류를 던짐
        throw new Error('Network response was not ok.');
      }
    })
    .catch(error => console.error('Error:', error));
  }

  // MongoDB에서 바이어 DB 데이터를 조회하는 함수
  function fetchBuyerDBData() {
    fetch('http://localhost:3000/api/buyer/buyerlist', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    .then(response => response.json())
    .then(data => setBuyerDB(data)) // 조회한 데이터로 buyerDB 상태 업데이트
    .catch(error => console.error('Error:', error));
  }

  useEffect(() => {
    handleResize();
    // 선택된 DB가 바이어 DB일 경우 해당 데이터를 조회
    if (selectedDB === 'buyer') {
      fetchBuyerDBData();
    }
  }, [selectedDB]); // selectedDB가 변경될 때마다 useEffect 트리거

  useEffect(() => {
    handleResize();
  }, []);

  const CopyButton = ({ text }) => {
    const copyToClipboard = () => {
      navigator.clipboard.writeText(text).then(() => {
        alert('해당 내용이 클립보드에 복사되었습니다.');
      }).catch(err => {
        console.error('Error copying text: ', err);
      });
    };
  
    return (
      <button onClick={() => copyToClipboard(text)} className="flex items-center text-white">
        <MdFileCopy size="1em"/>
        <span> 텍스트 복사</span>
      </button>
    );
  };


  return (
    <section
      className={`${
        open ? 'w-72' : 'w-16'
      } bg-neutral flex flex-col items-center gap-y-4 h-screen pt-4 relative duration-100 shadow-md`}>
     
      <div className="flex justify-around w-full">
        <button
          className={`px-4 py-2 ${selectedDB === 'archive' ? 'bg-blue-500 text-white' : 'bg-transparent'}`}
          onClick={() => setSelectedDB('archive')}>
          아카이브 DB
        </button>
        <button
          className={`px-4 py-2 ${selectedDB === 'buyer' ? 'bg-blue-500 text-white' : 'bg-transparent'}`}
          onClick={() => setSelectedDB('buyer')}>
          바이어 DB
        </button>
      </div>

      <div className={`flex flex-col items-center w-full ${!open && 'hidden'}`} style={{ marginBottom: '6rem', maxHeight: 'calc(100vh - 17rem)', overflowY: 'auto' }}>
        {selectedDB === 'archive' ? (
          <div className={`flex flex-col items-center w-full ${!open && 'hidden'}`}>
            <h3 className="text-lg font-semibold">아카이브 DB</h3>
            <ul className="w-full">
              {DBs.map((message, index) => (
                <li key={index} className="p-2">
                  <div className="flex flex-col items-left gap-2 rounded-lg shadow p-3" style={{ backgroundColor: 'rgb(72,115,255)' }}>
                    <span style={{ color: 'rgb(255, 255, 255)' }}>{message.text}</span>
                    <CopyButton text={message.text} />
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <div className={`flex flex-col items-center w-full ${!open && 'hidden'}`}>
            <h3 className="text-lg font-semibold">바이어 DB</h3>
            <ul className="w-full">
              {buyerDB.map((company, index) => (
                <li key={index} className="p-2">
                  <div className="flex flex-col items-left gap-2 rounded-lg shadow p-3" style={{ backgroundColor: 'rgb(72,115,255)', whiteSpace: 'pre-wrap' }}>
                    <span style={{ color: 'rgb(255, 255, 255)' }}> 
                      {`국가명: ${company.korNm}\n회사명: ${company.trgtpsnNm}\n상품명: ${company.prod1Nm}`}
                    </span>
                    <CopyButton text={`국가명: ${company.korNm}\n회사명: ${company.trgtpsnNm}\n상품명: ${company.prod1Nm}`} />
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <ul className='absolute bottom-0 w-full gap-1 menu rounded-box'>
        <li>
          <a onClick={() => clearDBOnServer()}>
            <MdDelete size={20} />
            <p className={`${!open && 'hidden'}`}>아카이브 DB 비우기</p>
          </a>
        </li>
        <li>
          <a onClick={() => uploadDataToMongoDB(DBs)}>
            <MdStorage size={20} />
            <p className={`${!open && 'hidden'}`}>아카이브 DB 업로드</p>
          </a>
        </li>
        <li>
          <a onClick={() => setModalOpen(true)}>
            <MdEmail size={20} />
            <p className={`${!open && 'hidden'}`}>Cold Mail 작성</p>
          </a>
        </li>
      </ul>
      <Modal title='Cold Mail 작성' modalOpen={modalOpen} setModalOpen={setModalOpen}>
        <Email modalOpen={modalOpen} setModalOpen={setModalOpen} />
      </Modal>
    </section>
    
    
  );
};

export default RightSideBar;
