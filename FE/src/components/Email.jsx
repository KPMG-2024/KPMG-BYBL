import React, { useState, useRef } from 'react';
import '../assets/email.css'; // 이 줄은 CSS를 별도의 파일로 관리한다고 가정한 것입니다.
import searchIcon from '../assets/search.png';

const Email = () => {
  const [input, setInput] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [loading, setLoading] = useState(false);
  const debounceTimeoutRef = useRef(null); // 디바운스를 위한 ref 사용
  const [buyerEmail, setBuyerEmail] = useState('');
  const [buyerlanguage, setBuyerLanguage] = useState('');
  const [buyerData, setBuyerData] = useState('');
  const [ourData, setOurData] = useState('');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);

  const fetchSuggestions = async (searchTerm) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:3000/api/buyer/buyercollect?search=${encodeURIComponent(searchTerm)}`);
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      setSuggestions(data);
      setShowSuggestions(true);
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
      setSuggestions([]);
      setShowSuggestions(false);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const value = e.target.value;
    setInput(value);
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }
    debounceTimeoutRef.current = setTimeout(() => {
      if (value.length > 1) {
        fetchSuggestions(value);
      } else {
        setSuggestions([]);
        setShowSuggestions(false);
      }
    }, 500);
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion.trgtpsnNm);
    setBuyerEmail(suggestion.email); // 바이어 이메일을 자동 완성된 값으로 설정
    setBuyerData(suggestion.search_total_info); // 바이어 데이터를 자동 완성된 값으로 설정
    setBuyerLanguage(suggestion.korNm); // 바이어 데이터를 자동 완성된 값으로 설정
    setShowSuggestions(false);
    // 제안 클릭 시 디바운스 함수 호출을 방지하기 위해 setTimeout 취소
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }
  };

  const fetchEmailData = async () => {
    try {
      const response = await fetch('http://localhost:3000/api/email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          input,
          buyerEmail,
          buyerData,
          ourData,
          buyerlanguage
        }),
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const data = await response.json();
      setTitle(data.title);
      setContent(data.content);
      
      alert('이메일 초안이 작성되었습니다.');
    } catch (error) {
      alert('이메일 초안 작성에 실패했습니다. 다시 시도해주시길 바랍니다.');
      console.error('Failed to fetch email data:', error);
    }
  };

  // '만들기' 버튼 클릭 시 이벤트 핸들러
  const handleCreate = () => {
    fetchEmailData();
  };

  const sendEmail = async () => {
    try {
      const formData = new FormData();
      formData.append('buyerEmail', buyerEmail);
      formData.append('title', title);
      formData.append('content', content);
      formData.append('file', file);
  
      const response = await fetch('http://localhost:3000/api/email/send', {
        method: 'POST',
        body: formData,
      });
  
      if (!response.ok) {
        throw new Error('Failed to send email');
      }
      alert('이메일을 성공적으로 보냈습니다.');
    } catch (error) {
      alert('이메일 발신에 실패했습니다. 다시 시도해주시길 바랍니다.');
      console.error('Failed to send email:', error);
    }
  };
  

  const handleSend = () => {
    sendEmail();
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  return (
    <div className="grid grid-cols-2 gap-2">
    <div className="w-full max-w-md">
      <div className="flex flex-col items-center justify-center gap-4 w-full">
        <div className="w-full flex justify-center items-center gap-4">
          <p className="text-2xl font-bold">바이어 정보</p>
        </div>
        <div className="flex items-center w-full gap-2 relative">
          <label className="block text-large font-large text-white-700">
            기업명 :
          </label>
          <div className="flex-1 mt-1 relative rounded-md shadow-sm">
            <input
              id="searchInput"
              type="text"
              value={input}
              onChange={handleChange}
              className="form-input block w-full pl-4 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              placeholder="검색"
              autoComplete="off"
              style={{backgroundImage: `url(${searchIcon})`, backgroundPosition: 'right 10px center', backgroundRepeat: 'no-repeat', backgroundSize: '20px 20px'}}
            />
            {loading && <div className="absolute top-0 right-0 h-full flex items-center pr-3">
              <div>Loading...</div>
            </div>}
          </div>
          {showSuggestions && suggestions.length > 0 && (
            <ul className="suggestions-list absolute z-10 w-full border border-gray-200 rounded-md shadow-lg bg-gray-700 mt-1 right-0 w-72 max-h-36 overflow-y-auto">
              {suggestions.slice(0, 3).map((suggestion, index) => (
                <li
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="suggestion-item px-4 py-2 hover:bg-gray-100 cursor-pointer"
                >
                  {suggestion.trgtpsnNm}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div style={{ height: '1rem' }}></div>

      <div className="flex items-center w-full gap-2">
          <label className="block text-large font-large text-white-700">
            바이어 이메일 :
          </label>
          <div className="flex-1 mt-1 relative rounded-md shadow-sm">
            <input
              type="text"
              value={buyerEmail}
              onChange={(e) => setBuyerEmail(e.target.value)}
              placeholder="바이어 이메일을 입력해주세요"
              className="form-input block w-full pl-4 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            />
          </div>
      </div>

      <div style={{ height: '1rem' }}></div>

      <div className="flex items-center w-full gap-2">
          <label className="block text-large font-large text-white-700">
            작성 언어 :
          </label>
          <div className="flex-1 mt-1 relative rounded-md shadow-sm">
            <input
              type="text"
              value={buyerlanguage}
              onChange={(e) => setBuyerLanguage(e.target.value)}
              placeholder="작성 언어을 입력해주세요"
              className="form-input block w-full pl-4 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            />
          </div>
      </div>
      
      <div style={{ height: '1rem' }}></div>

      <div className="items-center w-full gap-2">
        <label className="block text-large font-large text-white-700">
            바이어 정보
        </label>
        <div className="mt-1 relative rounded-md shadow-sm">
          {/* 바이어 데이터 입력란 */}
          <textarea
            value={buyerData}
            onChange={(e) => setBuyerData(e.target.value)}
            placeholder="바이어 정보를 입력해주세요"
            className="form-textarea block w-full pl-4 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            rows="7" // 원하는 줄 수 설정
            style={{ resize: "none" }} // 크기 조절 비활성화
          />
        </div>
      </div>

      <div style={{ height: '1rem' }}></div>

      <div className="items-center w-full gap-2">
        <label className="block text-large font-large text-white-700">
            자사 정보
        </label>
        <div className="mt-1 relative rounded-md shadow-sm">
          {/* 우리 데이터 입력란 */}
        <textarea
            value={ourData}
            onChange={(e) => setOurData(e.target.value)}
            placeholder="바이어 정보를 입력해주세요"
            className="form-textarea block w-full pl-4 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            rows="6" // 원하는 줄 수 설정
            style={{ resize: "none",  overflow: "auto" }} // 크기 조절 비활성화
          />
        </div>
      </div>

      <div className="flex justify-center mt-4">
        <button
          onClick={handleCreate}
          className="px-6 py-3 text-lg font-bold text-white bg-blue-500 rounded hover:bg-blue-600 focus:outline-none focus:bg-blue-600"
        >
          이메일 초안 만들기
        </button>
      </div>
    </div>

    <div className="w-full max-w-md">
      <div className="flex flex-col items-center justify-center gap-4 w-full">
        <div className="w-full flex justify-center items-center gap-2">
        <p className="text-2xl font-bold">이메일 초안</p>
        </div>

        <div className="flex items-center w-full gap-2">
          <label className="block text-large font-large text-white-700">
            제목 :
          </label>
          <div className="flex-1 mt-1 relative rounded-md shadow-sm">
            {/* 우리 데이터 입력란 */}
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="이메일 제목을 입력해주세요"
              className="form-input block w-full pl-4 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            />
          </div>
        </div>

        <div className="w-full gap-2">
          <label className="block text-large font-large text-white-700">
              이메일 내용
          </label>
          <div className="mt-1 relative rounded-md shadow-sm">
            {/* 우리 데이터 입력란 */}
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="이메일 본문을 입력해주세요"
              className="form-input block w-full pl-4 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              rows="17"
              style={{ resize: "none",  overflow: "auto", whiteSpace: "pre-wrap" }} // 크기 조절 비활성화
            />
          </div>
        </div>

        <div className="w-full gap-2">
          <label className="block text-large font-large text-white-700">
              첨부 파일
          </label>
          <div className="mt-1 relative rounded-md shadow-sm">
            {/* 첨부파일 입력란 */}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              className="file-input"
            />
          </div>
        </div>
      </div>

      <div className="flex justify-center mt-4">
        <button
          onClick={handleSend}
          className="px-6 py-3 text-lg font-bold text-white bg-blue-500 rounded hover:bg-blue-600 focus:outline-none focus:bg-blue-600"
        >
          메일 발송하기
        </button>
      </div>


    </div>
  </div>
    
  );
};

export default Email;
