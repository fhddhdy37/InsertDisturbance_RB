# 데이터 평가 진행 상황

| 모델    |  프롬프팅       | 결과 파일                                                     |
| -----   | -------------- | ------------------------------------------------------------- |
| gemini  | few-shot       | [파일](experiment/results/20250608_170253_gemini_fs.csv)    |
|         | cot            | [파일](experiment/results/20250608_174954_gemini_cot.csv)    |
|         | least-to-most  | [파일](experiment/results/20250608_185034_gemini_ltm.csv)    |
|         | fs + cot       | [파일](experiment/results/20250608_185034_gemini_fs_cot.csv)    |
|         | fs + ltm       | [파일](experiment/results/20250608_185034_gemini_fs_ltm.csv)    |
| gpt     | few-shot       | [파일](experiment/results/20250608_161254_gpt_fs.csv)    |
|         | cot            | [파일](experiment/results/20250608_172748_gpt_cot.csv)  |
|         | least-to-most  | [파일](experiment/results/20250608_172748_gpt_ltm.csv)  |
|         | fs + cot       | [파일](experiment/results/20250608_172748_gpt_fs_cot.csv)  |
|         | fs + ltm       | [파일](experiment/results/20250608_203143_gpt_fs_ltm.csv)  |


# result.csv 속성 설명

| 컬럼              | 설명                  |
| ----------------- | --------------------- |
| experiment count  | 실험 반복 횟수, 3회 실험 결과의 평균을 평가치로 사용      | 
| level             | 예제 문장의 외란 복합 수준, 단일 상황 ~ 4중 복합 상황으로 구성      |
| index             | 현재 복합 수준에서 예제 문장 번호      |
| model             | 사용한 모델      |
| prompting         | 사용한 프롬프팅 기법      |
| scenario file path| 출력 시나리오 파일의 경로      |
| log file path     | 로그 파일의 경로      |
| success           | 시나리오 생성 성공/실패 여부      |
| generating time   | 시나리오 생성에 걸린 시간, LLM에 질문을 요청한 시점부터 생성 완료 시점까지의 시간을 측정, 생성에 실패한 경우도 시간 측정      |
| video path        | 성공한 시나리오의 정성평가를 위한 영상 데이터      |
