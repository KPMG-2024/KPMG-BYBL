import PropTypes from 'prop-types';
import { MdComputer, MdPerson, MdFileCopy } from 'react-icons/md';
import moment from 'moment';
import Image from './Image';
import Markdown from './Markdown';
import { DBContext } from '../context/DBContext'; // 경로는 실제 구조에 맞게 조정하세요.
import React, { useContext } from 'react';


/**
 * A chat message component that displays a message with a timestamp and an icon.
 *
 * @param {Object} props - The properties for the component.
 */

const Message = (props) => {
  const { id, createdAt, text, ai = false, selected } = props.message;
  const [DBs, addDB, clearDB] = useContext(DBContext); // DBContext에서 addDB 함수 사용

  // 메시지 저장 버튼 클릭 핸들러
  const handleSaveClick = (texts, ai = false) => {
    // 선택된 메시지를 DB 상태에 추가
    const newDB = {
      text: texts,
    };
    addDB(newDB);
  };

  return (
    <div
      key={id}
      className={`flex items-end my-2 gap-2 ${
        ai ? 'flex-row-reverse justify-end' : 'flex-row justify-end'
      }`}>
      <div
        className={` w-screen overflow-hidden chat ${
          ai ? 'chat-start' : 'chat-end'
        }`}>
        <div className='chat-bubble text-neutral-content'>
          <Markdown markdownText={text}/>
          <div className={`flex justify-end items-center text-s`}>
            <button onClick={() => handleSaveClick(text)} className="flex items-center text-white-700">
              <MdFileCopy size="1em"/>
              <span>아카이브에 저장</span>
            </button>
          </div>
        </div>
      </div>
  
      <div className='avatar'>
        <div className='w-8 border rounded-full border-slate-400'>
          {ai ? (
            <MdComputer className='w-6 h-full m-auto' />
          ) : (
            <MdPerson className='w-6 h-full m-auto' />
          )}
        </div>
      </div>
    </div>
  );  
};

export default Message;

Message.propTypes = {
  message: PropTypes.shape({
    id: PropTypes.number.isRequired,
    createdAt: PropTypes.number.isRequired,
    text: PropTypes.string,
    ai: PropTypes.bool,
    selected: PropTypes.string,
  }).isRequired,
};
