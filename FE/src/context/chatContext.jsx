import PropTypes from 'prop-types';
import { createContext } from 'react';
import useMessageCollection from '../hooks/useMessageCollection';

/**
 * ChatContext는 메시지 컬렉션을 컴포넌트 간에 공유하기 위한 컨텍스트 객체입니다.
 */
const ChatContext = createContext({});

/**
 * ChatContextProvider는 ChatContext의 제공자 역할을 하는 함수형 컴포넌트입니다.
 * ChatContext를 하위 컴포넌트에 제공합니다.
 *
 * @param {Object} props - 컴포넌트에 전달된 속성들입니다.
 * @returns {JSX.Element} ChatContext.Provider 엘리먼트입니다.
 */
const ChatContextProvider = (props) => {
  const { messages, addMessage, clearChat } = useMessageCollection();

  return (
    <ChatContext.Provider value={[messages, addMessage, clearChat]}>
      {props.children}
    </ChatContext.Provider>
  );
};

export { ChatContext, ChatContextProvider };

ChatContextProvider.propTypes = {
  children: PropTypes.node.isRequired,
};