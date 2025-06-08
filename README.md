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

4. 녹화가 필요한 경우 (선택)
   * [ffmpeg](https://ffmpeg.org/download.html) 설치
   * 본인 OS에 맞게 설치
   * 설치 경로를 환경변수에 추가

# 실행 방법
---
1. `main.py` 실행
2. `mode` 를 수정하여 gemini 또는 gpt 모델 사용 가능
3. `input_text` 내용을 수정하여 다양한 외란 상황 생성
4. `GD/prompts.py` 에 다양한 프롬프팅 기법 추가 가능
5. `GD/controller.py` 의 `Controller` 을 상속받는 클래스에서 적용 모델 수정 가능

# 실험 방법
---
1. `main_experiment.py` 실행
2. `src/logs/` 에 각 실험 당 로그파일 생성
3. `./experiment/results/` 에 실험 결과를 .csv 파일로 저장

* [실험 결과](/experiment_results.md) 데이터는 제공되나 생성된 데이터는 제공되지 않음
