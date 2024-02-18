// React에서 사용되는 주요 기능들을 가져옵니다.
import { useState, useRef, useEffect, useContext } from 'react';
import Message from './Message';
import { ChatContext } from '../context/chatContext';
import Thinking from './Thinking';
import { MdSend } from 'react-icons/md';
import { replaceProfanities } from 'no-profanity';
import { davinci } from '../utils/davinci';
import { dalle } from '../utils/dalle';
import Modal from './Modal';
import Setting from './Setting';


const options = ['일반','DB 기반 QA','아카이브 기반 QA'];
const gptModel = ['gpt-3.5-turbo', 'gpt-4'];
const template = [
  {
    title: '경제 관련 질문',
    prompt: '베트남 경제에 대해 알려줘',
  },
  {
    title: '시장 관련 질문',
    prompt: '태국 라면 시장 동향에 대해 알려줘',
  },
];

/**
 * A chat view component that displays a list of messages and a form for sending new messages.
 */
const ChatView = () => {
  const messagesEndRef = useRef();
  const inputRef = useRef();
  const [formValue, setFormValue] = useState('');
  const [thinking, setThinking] = useState(false);
  const [selected, setSelected] = useState(options[0]);
  const [gpt, setGpt] = useState(gptModel[0]);
  const [messages, addMessage] = useContext(ChatContext);
  const [modalOpen, setModalOpen] = useState(false);

  /**
   * Scrolls the chat area to the bottom.
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  /**
   * 새 메시지 업데이트
   *
   * @param {string} newValue - The text of the new message.
   * @param {boolean} [ai=false] - Whether the message was sent by an AI or the user.
   */
  const updateMessage = (newValue, ai = false, selected) => {
    const id = Date.now() + Math.floor(Math.random() * 1000000);
    const newMsg = {
      id: id,
      createdAt: Date.now(),
      text: newValue,
      ai: ai,
      selected: `${selected}`,
    };

    addMessage(newMsg);
  };

  /**
   * Send massage API에 대한 호출
   *
   * @param {Event} e - The submit event of the form.
   */
  const sendMessage = async (e) => {
    e.preventDefault();

    const key = window.localStorage.getItem('api-key');
    if (!key) {
      setModalOpen(true);
      return;
    }

    const cleanPrompt = replaceProfanities(formValue);

    const newMsg = cleanPrompt;
    const aiModel = selected;
    const gptVersion = gpt;

    setThinking(true);
    setFormValue('');
    updateMessage(newMsg, false, aiModel);
    console.log(gptVersion);
    console.log(selected);

    try {
      if (aiModel === options[1]) {
        // 아카이브 QA 모델
        const response = await fetch('http://localhost:3000/api/qa/db', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${key}`,
          },
          body: JSON.stringify({ query: cleanPrompt }),
        });
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        data && updateMessage(data.result, true, aiModel);
      } else if (aiModel === options[2]) {
        // 아카이브 QA 모델
        const response = await fetch('http://localhost:3000/api/qa/archive', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${key}`,
          },
          body: JSON.stringify({ query: cleanPrompt }),
        });
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        data && updateMessage(data.result, true, aiModel);

      } else {
        // Davinci 모델 사용 로직
        const LLMresponse = await davinci(cleanPrompt, key, gptVersion);
        LLMresponse && updateMessage(LLMresponse, true, aiModel);
      }
    } catch (err) {
      window.alert(`Error: ${err.message} please try again later`);
    } finally {
      setThinking(false);
    }
};

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      // 👇 Get input value
      sendMessage(e);
    }
  };

  /**
   * 키 다운 이벤트를 처리합니다. 'Enter' 키를 누르면 메시지를 보냅니다.
   */

  /**
   * 메시지가 업데이트 되면 내려줌
   */
  useEffect(() => {
    scrollToBottom();
  }, [messages, thinking]);

    /**
   * 컴포넌트가 처음 렌더링될 때 TextArea 입력에 포커스
   */
  useEffect(() => {
    inputRef.current.focus();
  }, []);

  return (
    <main className='relative flex flex-col w-screen h-screen p-1 overflow-hidden dark:bg-light-grey'>
      <div className='mx-auto my-4 tabs tabs-boxed w-fit'>
        <a
          onClick={() => setGpt(gptModel[0])}
          className={`${gpt == gptModel[0] && 'tab-active'} tab`}>
          GPT-3.5
        </a>
        <a
          onClick={() => setGpt(gptModel[1])}
          className={`${gpt == gptModel[1] && 'tab-active'} tab`}>
          GPT-4
        </a>
      </div>

      <section className='flex flex-col flex-grow w-full px-4 overflow-y-scroll sm:px-10 md:px-32'>
        {messages.length ? (
          messages.map((message, index) => (
            <Message key={index} message={{ ...message }} />
          ))
        ) : (
          <div className='flex my-2'>
            <div className='w-screen overflow-hidden'>
              <ul className='grid grid-cols-2 gap-2 mx-10'>
                {template.map((item, index) => (
                  <li
                    onClick={() => setFormValue(item.prompt)}
                    key={index}
                    className='p-6 border rounded-lg border-slate-300 hover:border-slate-500'>
                    <p className='text-base font-semibold'>{item.title}</p>
                    <p className='text-sm'>{item.prompt}</p>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {thinking && <Thinking />}

        <span ref={messagesEndRef}></span>
      </section>

      {/* 맨 아래 입력창 */}
      <form
        className='flex flex-col px-10 mb-2 md:px-32 join sm:flex-row'
        onSubmit={sendMessage}>

        {/* 모델 선택 */}
        <select
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
          className='w-full sm:w-40 select select-bordered join-item'>
          <option>{options[0]}</option>
          <option>{options[1]}</option>
          <option>{options[2]}</option>
        </select>

        <div className='flex items-stretch justify-between w-full'>
          <textarea
            ref={inputRef}
            className='w-full grow input input-bordered join-item max-h-[20rem] min-h-[3rem]'
            value={formValue}
            onKeyDown={handleKeyDown}
            onChange={(e) => setFormValue(e.target.value)}
          />
          <button type='submit' className='join-item btn' disabled={!formValue}>
            <MdSend size={30} />
          </button>
        </div>
      </form>
      <Modal title='Setting' modalOpen={modalOpen} setModalOpen={setModalOpen}>
        <Setting modalOpen={modalOpen} setModalOpen={setModalOpen} />
      </Modal>
    </main>
  );
};

export default ChatView;
