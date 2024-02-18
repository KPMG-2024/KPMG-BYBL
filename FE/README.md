## 실행 방법
- 해당 서비스는 프론트엔드와 백엔드 서버 모두 npm을 활용해 동시 실행하도록 구성

### 1. 라이브러리 설치
```bash
npm install
```

### 2. Front-End 라이브러리 설치
```bach
cd FE ## FE 폴더에 들어가서 다시 의존성 패키지 설치
npm install
cd ..
```

### 3. Back-End 가상환경 실행
- 사전에 가상환경을 만들어 놓은 후 의존성 라이브러리 설치(BE README.md 참조)
```
conda activate [your venv name]
```

### 4. 실행
```bash
npm start
```
