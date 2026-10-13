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

**컨셉: 포토카드 바인더 + 폴꾸(포토카드 꾸미기) 레이어** — 2026년 10월 리뉴얼 완료. 옛 홀로그램 다크 테마(핑크/보라/시안 그라데이션)는 폐기.

### 기본 시스템 (자세한 토큰은 `DESIGN.md`)
- 배경 차콜 `#151217`, 카드는 크림 카드스톡 `#F2E9D8`(그레인 텍스처), 메인 악센트 가넷 `#B21B3E`, 단어 제목은 브라스/골드 포일
- 폰트: **Black Han Sans**(한글 단어·칩·스티커), **Bricolage Grotesque**(영문 제목/UI), **Hanken Grotesk**(본문), **JetBrains Mono**(로마자·라벨)

### 폴꾸 레이어 — `assets/pokku.css`
- **전 페이지 공용 파일 하나**. 메인 페이지는 `assets/pokku.css`, word 페이지는 `../assets/pokku.css`로 각 페이지 `<style>` **뒤에** 링크돼서 덮어씀. 톤 바꿀 땐 이 파일만 고치면 됨.
- 팝 컬러: `--pop-pink #FF6FAE` / `--pop-lilac #B9A2FF` / `--pop-mint #74E3C4` / `--pop-lemon #FFE16B`
  - ⚠️ **스티커·마스킹테이프·반짝이 전용.** 어두운 배경 위 본문 텍스트나 그라데이션 배경에 쓰지 말 것 (옛 홀로그램 톤으로 돌아가는 지름길). 메인 악센트는 계속 가넷.
- 구성 요소: die-cut 스티커(팝 컬러 + 크림 테두리 3px), 마스킹테이프(카드 `::after`), 반짝이 ✦, 살짝 기울어진 리스트 카드(±0.6~1.6deg), 튕기는 호버(`--ease-pop`)
- **긴 글 카드(단어 상세 카드, 제보 폼, 개인정보)는 기울이지 않음** — 테이프/스티커만. 스티커가 읽는 글자를 가리면 안 됨 (모바일 390px에서 꼭 확인).
- `prefers-reduced-motion`이면 스티커 등장 애니메이션·반짝임 끔.

### 페이지별 메모
- **홈(index.html)**: 2단 히어로 "Your bias said it. Now get the joke." + 오른쪽 실제 포토카드. 들어오면 오늘의 카드(`TODAYS_CARD_POOL`, 날짜별 로테이션)가 펼쳐지고 검색하면 결과로 플립. **오늘의 카드는 GA `search_word` 이벤트를 보내지 않음**(`dealCard` vs `selectWord` 분리 — 검색량 데이터 오염 방지). 아래로 트렌딩 3장(`HOME_TRENDING`) → 탐색 카드 → 가넷 CTA. 홈 전용 스티커 스타일은 index.html 안에 있음.
- **헤더**: 메뉴 라벨은 한 줄 유지 — 1260px 이하 DICTIONARY 뱃지 숨김, 1120px 이하 햄버거 메뉴 (pokku.css).
- **생성 파일**: whatsnew.html과 word/*.html의 꾸미기는 각각 `generate_whatsnew.py`, `generate_word_pages.py` **템플릿 안에** 있음 — 생성된 HTML 직접 수정 금지. 단어 카드 모서리 스티커는 slug 기반으로 ♥ ✦ ㅋㅋ ★ ♪ 중 하나가 고정 선택됨.
- 숫자(단어 개수 등)는 화면에 하드코딩하지 말 것 — About 통계도 "650+" 식으로.

⚠️ 디자인을 또 바꾸더라도 **다음 기능들은 그대로 유지해야 함** (비주얼과 무관하게 사이트 핵심 기능이라 디자인 리뉴얼 때 실수로 빠뜨리기 쉬움):
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
  assets/pokku.css      — 폴꾸 스티커 레이어, 전 페이지 공용 (위 "디자인" 참고)
  data/kslang-slang-database.xlsx  — build_kslang_db.py로 생성됨
  word/*.html            — 단어별 개별 페이지 651개, generate_word_pages.py로 생성됨
  guides/*.html          — 주제별 가이드(허브 + 컬렉션), generate_collections.py로 생성됨 (직접 수정 금지)
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
python3 generate_collections.py # → guides/index.html + guides/<slug>.html (주제별 가이드)
python3 update_main_pages.py   # → index/category/trending/submit의 SLANG_DB
python3 generate_whatsnew.py   # → whatsnew.html
python3 generate_sitemap.py    # → sitemap.xml
```

`build_kslang_db.py`(즉 단어 데이터나 번역)를 바꿨으면 이 5개 스크립트를 **전부** 순서대로 다시 돌려야 함. 하나라도 빼먹으면 페이지들끼리 데이터가 어긋남.

⚠️ 템플릿만 고쳐서 생성 스크립트 하나만 돌릴 때도 `build_kslang_db.py`가 import되면서 **xlsx가 바이트만 다르게 다시 써짐**(내용은 동일). 단어 데이터를 안 바꿨으면 커밋 전에 `git checkout -- data/kslang-slang-database.xlsx`로 되돌릴 것 — 안 그러면 쓸데없는 병합 충돌 원인이 됨.

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

### 단어 상세 콘텐츠 — `DETAILS` (build_kslang_db.py)

번역 사전처럼 **별도 선택 사전**이라 기존 튜플은 안 건드림. 들어있는 단어만 word 페이지에 뉘앙스 / 사용법 / 문화 맥락 / 톤 / 비슷한 표현 / 출처 섹션이 생기고, 빠진 필드는 섹션 자체가 안 보임.
- `nuance`·`usage`·`culture`는 **5개 언어 전부** 채울 것 (`{en, es, zh, cn, ja}`). 페이지에선 선택한 언어만 보이고(기본 영어), HTML엔 5개 다 들어감. 기존 뜻·예문은 지금처럼 5개 언어가 다 쌓여서 보임 — 의도된 차이.
- `similar`는 DB에 실제 있는 `kr`만, `tags`는 `TAG_LABELS` 키만, `register`는 `REGISTER_LABELS` 키만 (casual / everyday / text).
- `sources`는 **직접 열어서 내용 확인한 페이지만**. 못 찾으면 비워둘 것 (최애·감다살처럼). 유래가 불확실하면 불확실하다고 쓸 것 (대박 참고 — 국립국어원도 미확정이라고 함). 지어낸 통계·인용·가사·실존 인물 예문 금지.
- 출처로 확인되면 그 단어 `status`를 "Verified (web-checked)"로 올림.
- 관련 단어는 `similar` → 같은 `tags` → 같은 카테고리 순으로 채워짐 (`pick_related`).
- 주제별 가이드는 `COLLECTIONS`(같은 파일): 제목·소개·묶음 제목은 5개 언어, 단어 설명은 기존 5개 언어 뜻을 그대로 씀. **검증된 단어 위주**로 넣고, 단어 수가 부족한 주제는 억지로 만들지 말 것. 가이드에 실린 단어는 word 페이지에 "Featured in" 링크가 자동으로 붙음.
- UI 라벨 키 추가할 땐 **기존 키 이름과 겹치지 않는지** 확인 (`usage_h2`는 이미 "Real usage"로 쓰는 중 — 새 섹션은 `howto_h2`).

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
- `scripts/generate_instagram_cards.py` — 카드뉴스 PNG 자동 생성 도구. 5개 빌드 스크립트와 달리 자동 파이프라인에 안 걸려있음 (수동 실행).
  ```bash
  cd scripts
  python generate_instagram_cards.py --carousel "컴백"   # 요일별 로테이션용 4장 세트
  python generate_instagram_cards.py --new-word           # NEW_WORDS_LOG 최신 항목 → 신규 단어 1장씩
  ```
  출력은 `assets/instagram/<날짜>-<로마자슬러그>/slide-N.png`. 폰트는 `assets/fonts/`의 로컬 파일 사용 (Pillow는 폰트 폴백을 안 해줌 — 위 "겪었던 버그들" #3과 같은 함정).

## 대기 중인 작업

- [x] 디자인 리뉴얼 — 포토카드 + 폴꾸 레이어로 전 페이지 적용 완료 (2026-10)
- [ ] Instagram 카드뉴스/릴스 추가 제작
- [ ] Google AdSense 신청 (도메인 숙성 + 트래픽 확보 후, About 페이지는 이미 만들어놓음)
- [ ] 포르투갈어(브라질) 지원 — 원래 타겟(라틴아메리카)에 있는데 아직 없음, 큰 작업이라 별도 프로젝트로 취급할 것
- [ ] 데이터 기반 트렌딩 (현재 trending.html은 큐레이션 픽 5개, GA4 `search_word` 이벤트가 쌓이면 실제 검색량 기반으로 전환 가능)

## Anthropic 제품 관련 참고

- Claude Design은 claude.ai Projects랑 **별개의 "프로젝트" 개념**을 씀 (디자인 시스템 저장용). 자동 연동 안 됨 — 브랜드 색상/폰트 정보를 매번 수동으로 전달해야 함.
