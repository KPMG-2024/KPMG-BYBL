import PropTypes from 'prop-types';
import { createContext } from 'react';
import useDBCollection from '../hooks/useDBCollection';

/**
 * DBContext는 메시지 컬렉션을 컴포넌트 간에 공유하기 위한 컨텍스트 객체입니다.
 */
const DBContext = createContext({});

/**
 * DBContextProvider는 DBContext의 제공자 역할을 하는 함수형 컴포넌트입니다.
 * DBContext를 하위 컴포넌트에 제공합니다.
 *
 * @param {Object} props - 컴포넌트에 전달된 속성들입니다.
 * @returns {JSX.Element} DBContext.Provider 엘리먼트입니다.
 */
const DBContextProvider = (props) => {
  const { DBs, addDB, clearDB } = useDBCollection();

  return (
    <DBContext.Provider value={[DBs, addDB, clearDB]}>
      {props.children}
    </DBContext.Provider>
  );
};

export { DBContext, DBContextProvider };

DBContextProvider.propTypes = {
  children: PropTypes.node.isRequired,
};