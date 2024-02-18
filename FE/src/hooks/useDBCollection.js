import { useState, useEffect } from 'react';

/**
 * 사용자와 AI 간의 대화를 관리하기 위한 커스텀 훅입니다.
 *
 * @returns {Object} `DBs` 배열, `addDB` 함수, `clearDBs` 함수, `loadDB` 함수를 포함하는 객체입니다.
 */
const useDBCollection = () => {
  // 대화 메시지 배열을 관리하기 위한 상태
  const [DBs, setDBs] = useState([]);

  // 페이지 로드 시 로컬 스토리지에서 메시지 불러오기
  useEffect(() => {
    const storedDBs = JSON.parse(localStorage.getItem('DBs'));
    if (storedDBs) {
      setDBs(storedDBs);
    }
  }, []);

  // 메시지 배열이 변경될 때마다 로컬 스토리지에 메시지 저장
  useEffect(() => {
    if (DBs.length) {
      localStorage.setItem('DBs', JSON.stringify(DBs));
    }
  }, [DBs]);

  /**
   * 컬렉션에 새로운 메시지를 추가하는 함수입니다.
   *
   * @param {Object} DB - 컬렉션에 추가할 메시지입니다.
   */
  const addDB = (DB) => {
    setDBs((prev) => [...prev, DB]);
  };

  /**
   * 컬렉션 내의 모든 메시지를 지우고 초기 메시지로 재설정하는 함수입니다.
   */
  const clearDB = () => {
    localStorage.setItem('DBs', JSON.stringify([]));
    setDBs([]);
  };

  return { DBs, addDB, clearDB };
};

export default useDBCollection;
