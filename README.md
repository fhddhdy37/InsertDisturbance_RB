# 시작하기 전에
---
1. [esmini runner](https://github.com/esmini/esmini/releases/tag/v2.46.3) 설치
   * 본인 OS에 맞게 esmini-demo_OS.zip 다운로드
   * 적당한 위치에 압축 해제
     
2. 필요 패키지 설치
   * `pip install -r requirements.txt`
     
3. `GD/config.py` 파일에 API key 및 esmini 경로 추가
   * ```
     GPT_API : gpt api key
     GEMINI_API : gemini api key
     ESMINI_PATH : esmini 설치 경로 (ex: ~/esmini-demo)
     ```

# 실행 방법
---
1. `main.py` 실행
2. `mode` 를 수정하여 gemini 또는 gpt 모델 사용 가능
3. `input_text` 내용을 수정하여 다양한 외란 상황 생성
4. `GD/prompts.py` 에 다양한 프롬프팅 기법 추가 가능
5. `GD/controller.py` 의 `Controller` 을 상속받는 클래스에서 적용 모델 수정 가능