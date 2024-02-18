import { useState, useEffect } from 'react';

/**
 * 사용자와 AI 간의 대화를 관리하기 위한 커스텀 훅입니다.
 *
 * @returns {Object} `messages` 배열, `addMessage` 함수, `clearMessages` 함수, `loadMessage` 함수를 포함하는 객체입니다.
 */
const useMessageCollection = () => {
  // 대화 메시지 배열을 관리하기 위한 상태
  const [messages, setMessages] = useState([]);

  // 페이지 로드 시 로컬 스토리지에서 메시지 불러오기
  useEffect(() => {
    const storedMessages = JSON.parse(localStorage.getItem('messages'));
    if (storedMessages) {
      setMessages(storedMessages);
    }
  }, []);

  // 메시지 배열이 변경될 때마다 로컬 스토리지에 메시지 저장
  useEffect(() => {
    if (messages.length) {
      localStorage.setItem('messages', JSON.stringify(messages));
    }
  }, [messages]);

  /**
   * 컬렉션에 새로운 메시지를 추가하는 함수입니다.
   *
   * @param {Object} message - 컬렉션에 추가할 메시지입니다.
   */
  const addMessage = (message) => {
    setMessages((prev) => [...prev, message]);
  };

  /**
   * 컬렉션 내의 모든 메시지를 지우고 초기 메시지로 재설정하는 함수입니다.
   */
  const clearChat = () => {
    localStorage.setItem('messages', JSON.stringify([]));
    setMessages([]);
  };

  return { messages, addMessage, clearChat };
};

export default useMessageCollection;
