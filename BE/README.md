## 가상환경 정보
- conda 기반 가상환경
- **python == 3.9.18**
- requirements.txt에 있는 의존성 라이브러리 기반 작동


### 가상환경 만들기
```bash
conda create --name [your venv name] python=3.9  # 임의의 이름으로 가상환경 만들기
conda activate [your venv name] # 만든 가상환경 이름 실행
```

### 의존성 라이브러리 설치
```bash
pip install -r requirements.txt
```
