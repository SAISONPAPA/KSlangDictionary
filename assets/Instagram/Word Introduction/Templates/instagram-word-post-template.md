# HelloKSlang — Instagram "Word of the Day" Post Template

주 3회 인스타그램에 올리는 **단어 1개 소개 카드뉴스** 포맷의 재사용 스펙 문서.
이 문서 + `generate_photocard_post.py` 파일만 있으면 새 세션에서도 동일한 포맷으로 계속 생성 가능.

---

## 1. 포맷 개요

- **4페이지 캐러셀**, 1080×1350px (인스타 세로 비율)
- 디자인: 실제 hellokslang.com 단어 상세 페이지의 "포토카드" 스타일을 그대로 참조
  (크림 그레인 카드 + 골드 포일 타이틀 + 티켓 노치 구분선 + 크림슨 악센트 + 검정 REAL USAGE 박스)
- 언어: **영어 단일** (인스타 타겟이 영미권+라틴아메리카이므로)

### 페이지 구성
| 페이지 | 내용 |
|---|---|
| 1 | 단어 소개 — 카테고리 뱃지, 한글 단어(골드), 발음기호(`/ romanization /`), "Swipe to see what it means →" |
| 2 | 단어 의미 — 영어 정의 1~2문장, 하단에 짧은 사용 팁 |
| 3 | 실전 예문 — 검정 박스 안에 한글 예문 + 화살표 영어 번역, 하단에 "Commonly seen on: ..." |
| 4 | CTA — 1~3페이지와 동일한 크림 카드 디자인, hellokslang.com 홍보 문구 (사이트 전반 소개, 단일 단어 언급 X) |

### 페이지 4 고정 카피 방향 (합의된 버전)
- "500+ words" (651개 정확한 숫자 대신 라운드 넘버 사용 — 계속 늘어나는 숫자라 하드코딩 피함)
- K-pop/K-drama에 국한되지 않고 "everyday Korean pop culture" 뉘앙스로 확장
- 마지막에 "plus 4 more languages (ES/CN/JP)" 로 다국어 지원 언급
- "Link in bio" 문구 사용 금지 (정적 이미지라 클릭 불가하므로)

---

## 2. 파일 위치 & 사용법

- **생성 스크립트**: `generate_photocard_post.py` (Pillow 기반)
- **폰트**: Anton, Black Han Sans(한글), Manrope(가변폰트), JetBrains Mono, Noto Sans SC — 전부 Google Fonts 오픈소스, `google/fonts` GitHub repo에서 다운로드
- **새 단어로 재생성하는 법**: 스크립트 안 `WORD` 딕셔너리만 교체 후 재실행

```python
WORD = {
    "category": "ONLINE MEMES",       # 카테고리 뱃지 (영문 대문자로 표기)
    "hangul": "늙크크",                 # 한글 단어
    "roman": "neuk-keu-keu",          # 로마자 발음
    "meaning": "...",                  # 영어 정의 1~2문장
    "quote_kr": "...",                 # 한글 예문
    "quote_en": "...",                 # 예문의 영어 번역
    "meta": "Commonly seen on: ...",   # 어디서 쓰이는지
    "tip": "Tip: ...",                 # 2페이지 하단 팁
}
```

**주의**: 한글 문자를 유니코드 이스케이프(`\uXXXX`)로 직접 입력할 때 오타 나기 쉬움 — 가능하면 한글 원문 그대로 입력할 것 (이전에 `\ub721`≠`\ub299` 오타로 글자가 안 보이는 버그 있었음).

---

## 3. 디자인 토큰 (근사치 — 실제 CSS 확정되면 교체 필요)

| 요소 | 값 |
|---|---|
| 카드 배경 (크림) | `#E8DFC7` 근사 |
| 골드 (타이틀) | `#A17A21` |
| 크림슨 (악센트) | `#C41E3A` |
| 검정 박스 (REAL USAGE) | `#181311` |
| 잉크 (본문 텍스트) | `#231C18` |
| 카테고리 뱃지 배경 | `#B79A5A` |

> ⚠️ 이 색값은 스크린샷 눈대중 추출. 실제 사이트 리뉴얼 CSS(D-Day 컴백 스케줄 크림슨 톤)가 word 페이지까지 확정되면 정확한 hex로 교체할 것.

---

## 4. 캡션 & 해시태그 공식

### 캡션 구조 (깔끔하고 정보 중심 톤)
```
Today's word: [한글] ([로마자])

[정의 1~2문장]

[어디서/언제 쓰이는지 1문장]

Swipe through for the meaning and a real example →

500+ words like this one, romanized and explained in English, Spanish, Chinese, and Japanese — free at hellokslang.com.

[선택: 해시태그 5개]
```

### 해시태그
- **5개 이내 권장** (2026년 기준 인스타는 해시태그를 도달 증폭이 아닌 콘텐츠 분류 신호로만 사용, 5개 초과 시 오히려 손해)
- 기본 세트: `#hellokslang #kpopslang #koreanslang #kdrama #learnkorean`
- 해시태그보다 **캡션 안 키워드 자연스러운 배치**가 검색 노출에 더 중요해진 추세

---

## 5. 새 게시물 만드는 워크플로 (체크리스트)

1. 이번 주 소개할 단어 선정 (카테고리 로테이션 참고: 아이돌 필수/온라인 밈/팬덤 표현/방송 예능/연애 썸)
2. `WORD` 딕셔너리 교체
3. 스크립트 실행 → 4장 생성
4. 눈으로 검수 (한글 폰트 깨짐, 텍스트 잘림, 여백 등)
5. 캡션 작성 (위 구조 따라 단어만 교체)
6. 해시태그 5개 결정 (기본 세트 + 필요시 카테고리별 니치 태그 1~2개 교체)
7. 게시

---

*최초 작성: 2026년 8월. 실제 사이트 word 페이지 디자인(크림슨 톤) 확정되면 색상 토큰 섹션 업데이트 필요.*
