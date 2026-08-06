# CLAUDE.md — HelloKSlang Dictionary

이 파일은 Claude Code가 이 프로젝트에서 작업할 때 자동으로 참고하는 컨텍스트야. claude.ai 채팅에서 이 사이트를 처음부터 만들면서 나눈 대화 내용을 정리한 것.

## 프로젝트 개요

- **이름**: HelloKSlang (HelloKSlang Dictionary)
- **도메인**: hellokslang.com (실제 라이브, GitHub Pages 호스팅)
- **정체성**: K팝/K드라마 신조어·슬랭 사전. "그게 무슨 뜻이야? What did your bias just say?"
- **타겟**: 해외 거주, 영미권+라틴아메리카, 10~30대 여성, K-Culture 관심층
- **GitHub 저장소**: SAISONPAPA/KSlangDictionary (public)
- **인스타그램**: @hellokslang (막 개설, 홍보 준비 중)

## 디자인

**리뉴얼 진행 중.** Claude Code + Impeccable 플러그인으로 기존 홀로그램 다크 테마를 완전히 새 디자인으로 교체할 예정. 기존 디자인에 종속된 내용은 이 문서에서 의도적으로 빼놓았으니, 새 디자인이 정해지면 이 섹션에 새 색상/폰트/톤을 채워 넣을 것.

⚠️ 단, 디자인이 바뀌어도 **다음 기능들은 그대로 유지해야 함** (비주얼과 무관하게 사이트 핵심 기능이라 디자인 리뉴얼 때 실수로 빠뜨리기 쉬움):
- 5개 언어 토글 (EN/ES/繁/简/日) — 데스크톱 버튼 + 모바일 드롭다운
- localStorage 기반 언어 유지, 현재 페이지 네비 active 표시
- 651개 word 페이지의 개별 SEO 메타태그·구조화 데이터(JSON-LD)
- 검색/카테고리 필터링 JS 로직

## 저장소 구조

```
kslang-repo/
  index.html          — 홈/검색 페이지
  category.html        — 카테고리별 브라우징
  trending.html        — "대세" 인기 단어 페이지
  submit.html           — 단어 제보 폼
  whatsnew.html        — 신규 단어 (generate_whatsnew.py로 생성됨, 직접 수정 금지)
  about.html            — 소개 페이지 (정적 파일, 스크립트로 생성 안 됨)
  privacy.html          — 개인정보처리방침 (언어 토글 없음, 영어 단일)
  robots.txt / sitemap.xml  — sitemap.xml은 generate_sitemap.py로 생성됨
  assets/og-image.png   — 소셜 공유 미리보기 이미지 (1200×630)
  data/kslang-slang-database.xlsx  — build_kslang_db.py로 생성됨
  word/*.html            — 단어별 개별 페이지 651개, generate_word_pages.py로 생성됨
  scripts/
    build_kslang_db.py       — ⭐ SINGLE SOURCE OF TRUTH. 모든 단어 데이터 + 4개 번역 딕셔너리
    generate_word_pages.py   — word/*.html 651개 재생성
    update_main_pages.py     — index/category/trending/submit의 SLANG_DB(JS) 재생성
    generate_whatsnew.py     — whatsnew.html 재생성
    generate_sitemap.py      — sitemap.xml 재생성
    safety_check.py          — 19+/선정적 콘텐츠 차단 (배포 전 필수 실행)
  .github/workflows/rebuild.yml  — GitHub Actions 자동화
```

## 빌드 명령어 (순서 중요)

```bash
cd scripts
python3 safety_check.py        # 반드시 제일 먼저
python3 build_kslang_db.py     # → data/kslang-slang-database.xlsx
python3 generate_word_pages.py # → word/*.html (651개)
python3 update_main_pages.py   # → index/category/trending/submit의 SLANG_DB
python3 generate_whatsnew.py   # → whatsnew.html
python3 generate_sitemap.py    # → sitemap.xml
```

`build_kslang_db.py`(즉 단어 데이터나 번역)를 바꿨으면 이 5개 스크립트를 **전부** 순서대로 다시 돌려야 함. 하나라도 빼먹으면 페이지들끼리 데이터가 어긋남.

## GitHub Actions 자동화

`.github/workflows/rebuild.yml`이 `scripts/build_kslang_db.py`가 바뀐 push에서만 자동 트리거됨. 자동 커밋은 생성된 파일들만 건드리므로 무한루프 안 남.

- **최초 1회 설정 필요**: 저장소 Settings → Actions → General → Workflow permissions → "Read and write permissions"
- push가 자동으로 워크플로우를 트리거했다면 **수동으로 "Run workflow" 또 누르지 말 것** — 두 실행이 겹치면 push 충돌 남. (재시도 로직은 이미 넣어놨지만 애초에 안 겹치는 게 나음.)
- xlsx는 GitHub Actions가 재생성할 때마다 바이트 단위로 미묘하게 달라져서 **병합 충돌이 거의 항상 남** — 이건 정상. 충돌 뜨면 "main(서버) 버전 사용"으로 골라도 안전함, 데이터 내용은 어차피 동일함.

## 데이터: 651개 단어, 5개 카테고리, 5개 언어

| 카테고리 | 개수 |
|---|---|
| 아이돌 필수 용어 (Idol Essentials) | 149 |
| 팬덤 표현 (Fandom Feels) | 118 |
| 방송·예능 (Broadcast & Variety) | 125 |
| 온라인 밈 (Online Memes) | 177 |
| 연애·썸 표현 (Dating & Romance) | 82 |

**언어**: 한국어(원본) + 영어 + 스페인어(기본 필드) + 번체중문(`ZH_TW_TRANSLATIONS`) + 간체중문(`ZH_CN_TRANSLATIONS`) + 일본어(`JA_TRANSLATIONS`) — 전부 651/651 완료 상태.

### 새 단어 추가할 때 반드시 지킬 것

새 단어 하나 추가 = **6개 언어 필드를 한 번에 다 채워야** 함 (kr/rom/en/es는 `CATEGORIES` 튜플에, zh/cn/ja는 각각 별도 딕셔너리에). **하나라도 빼먹으면 그 언어 토글에서 조용히 영어로 폴백됨** (깨지진 않지만 미완성 상태로 남음 — 이게 실제로 여러 번 발생했던 버그의 원인, 아래 참고).

번체→간체는 OpenCC(`tw2sp` 프로필)로 자동 변환 가능하지만, **일본어는 자동변환 불가** — 일본에 이미 정착된 고유 팬덤 용어가 있어서(예: 최애→推し) 매번 손으로 새로 써야 함.

## 겪었던 버그들 (같은 실수 반복 방지용)

1. **`data-en`은 있는데 특정 언어 속성이 없는 요소 → `setLang()`이 `null`을 그대로 텍스트에 박아버림.** submit.html 폼 라벨/placeholder에서 두 번이나 발생 (번체·간체 추가할 때 한 번, 일본어 추가할 때 한 번 — 매번 "급하게 만든 특수 페이지"를 깜빡하고 놓침). **새 언어 추가하거나 새 페이지 만들 때마다 `data-en` 있는 요소 전수 검사**할 것:
   ```python
   import re
   html = open('파일명').read()
   all_data_en = re.findall(r'<[^>]*data-en="[^"]*"[^>]*>', html)
   missing = [m for m in all_data_en if 'data-XX=' not in m]  # XX = 확인할 언어코드
   ```

2. **`.foot-row`가 `justify-content: space-between`인데 링크를 div로 안 묶고 형제 요소로 추가하면 양 끝으로 벌어짐.** 여러 링크를 한 그룹으로 붙이려면 반드시 wrapper `<div>`로 묶을 것.

3. **PIL로 이미지 생성 시 Plus Jakarta Sans는 한글(Hangul) 글리프가 아예 없음.** 브라우저는 폰트 폴백을 자동으로 해주지만 PIL은 안 해줌 — 깨진 사각형(tofu)으로 나옴. 한글 본문 텍스트엔 Noto Sans KR 같은 한글 지원 폰트를 따로 써야 함 (Black Han Sans는 큰 단어 하나 표시용이지 긴 문장엔 안 어울림).

4. **`ZH_CN_TRANSLATIONS`를 OpenCC로 자동변환할 때 著/着 오변환 버그**가 있었음 (原著→原着처럼 잘못 바뀜). 자동변환 후엔 `원저작물이 원著이어야 하는 단어들` 재검사 필요.

5. **xlsx 컬럼을 늘릴 때마다 `HEADERS`, 행 데이터 구성 부분, `widths` 배열 3곳을 다 같이 늘려야 함** — 하나라도 안 맞으면 컬럼이 밀림.

6. **딕셔너리를 문자열 매칭으로 병합할 때 "마지막 항목"을 마커로 쓰면, 파이썬 dict 삽입 순서가 내가 예상한 것과 다를 수 있어서 매칭 실패할 수 있음** — 병합 직전에 실제 파일의 마지막 줄을 `view`로 확인하고 마커를 잡을 것.

## 소셜/SEO 관련

- 모든 페이지(657개: 메인 6 + word 651)에 `og:title`/`og:description`/`og:image`/twitter card 완비. 이미지는 전부 동일한 `assets/og-image.png` 하나 공유 (단어별 개별 이미지는 아직 없음 — 나중에 클릭률 보고 재검토 가능).
- **OG 이미지에 숫자(단어 개수, 언어 개수)를 절대 넣지 말 것** — 계속 바뀌는 값이라 이미지 재생성 없인 stale해짐. "in many languages" 같은 식으로 숫자 없이 표현.
- 모바일에서 언어 토글 5개가 다 버튼으로 나오면 옆으로 삐져나감 → 860px 이하에서는 `<select>` 드롭다운으로 전환됨 (`.lang-switch` 숨기고 `.lang-select` 표시). `setLang()`이 버튼 active 상태랑 select value를 항상 동기화시킴.
- 언어 선택은 `localStorage`(`kslang_lang` 키)에 저장되고, 페이지 로드 시 자동 적용됨 (예전엔 페이지 이동마다 영어로 리셋되는 버그가 있었음, 지금은 고쳐진 상태).
- 현재 페이지는 네비게이션에 pink underline(데스크톱)/pink text(모바일 메뉴)로 active 표시됨.

## 인스타그램 홍보 (@hellokslang)

- 콘텐츠 우선순위: **릴스(주 3~4개, 신규 팔로워 유입용) > 캐러셀(주 2~3개, 저장/공유 유도용) > 스토리(거의 매일, 기존 팔로워 유지용)**
- 카테고리 5개를 요일별 테마로 로테이션 (월 아이돌용어 → 화 밈 → 수 팬덤 → 목 방송예능 → 금 연애썸)
- 인스타그램 자동 게시는 아이디/비번 공유 방식이 아니라 **Meta Business Suite(무료, 공식 OAuth 방식)**로 해야 함 — 계정 정지 위험 없음.
- 해시태그는 3~5개면 충분 (많이 넣던 시절 지남). 저장/공유 유도 문구가 2026년 알고리즘에서 제일 중요한 신호.

## 대기 중인 작업

- [ ] 디자인 리뉴얼 여부 결정 (Impeccable 목업 검토 후)
- [ ] Instagram 카드뉴스/릴스 추가 제작
- [ ] Google AdSense 신청 (도메인 숙성 + 트래픽 확보 후, About 페이지는 이미 만들어놓음)
- [ ] 포르투갈어(브라질) 지원 — 원래 타겟(라틴아메리카)에 있는데 아직 없음, 큰 작업이라 별도 프로젝트로 취급할 것
- [ ] 데이터 기반 트렌딩 (현재 trending.html은 큐레이션 픽 5개, GA4 `search_word` 이벤트가 쌓이면 실제 검색량 기반으로 전환 가능)

## Anthropic 제품 관련 참고

- Claude Design은 claude.ai Projects랑 **별개의 "프로젝트" 개념**을 씀 (디자인 시스템 저장용). 자동 연동 안 됨 — 브랜드 색상/폰트 정보를 매번 수동으로 전달해야 함.
