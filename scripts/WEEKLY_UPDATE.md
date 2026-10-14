# 주간 자동 업데이트 플레이북

매주 월요일 예약 작업이 이 파일을 보고 그대로 실행함. **main에 직접 push 금지.** 결과는 PR로만 올리고, 머지는 Jay가 직접 함.
CLAUDE.md의 규칙(특히 "Jay의 단어 선정 규칙", DETAILS 규칙, 빌드 순서)이 이 문서보다 우선함.

## 0. 시작 전 확인

```bash
cd <repo>   # SAISONPAPA/KSlangDictionary
git fetch origin main
# gh pr 명령은 GraphQL이라 막혀 있음 → REST API(gh api)만 사용
gh api 'repos/SAISONPAPA/KSlangDictionary/pulls?state=open&per_page=50' --jq '[.[]|select(.head.ref|startswith("weekly/"))|{number,title}]'
```

- **열려 있는 `weekly/` PR이 이미 있으면 새로 만들지 말 것.** Jay가 아직 머지를 안 한 거라서, 새 PR을 만들면 `build_kslang_db.py`에서 충돌이 남. 그 PR에 "이번 주 업데이트는 이 PR 머지 후로 미룸" 코멘트만 남기고 종료:
  `gh api repos/SAISONPAPA/KSlangDictionary/issues/<번호>/comments -f body='...'`
- 없으면 브랜치 생성: `git checkout -B weekly/<YYYY-MM-DD> origin/main` (날짜는 KST 오늘).

## 1. 새 단어 추가 (목표 10개, 최소 0개)

**고르는 법**
- 최근 1~3개월 사이 한국 뉴스/매체에서 다룬 신조어·유행어·팬덤 용어를 WebSearch로 찾기. 예: `2026 신조어`, `요즘 유행어 뜻`, `MZ 신조어 기사`, `아이돌 팬덤 용어`, `예능 유행어`.
- 카테고리는 단어가 적은 쪽(특히 DATING) 위주로 고르기. 너무 한쪽으로 몰리지 않게.
- **출처 없이는 넣지 않음.** 뉴스 기사·국립국어원·위키백과처럼 직접 열어서 뜻이 확인되는 페이지가 있는 단어만 추가. 나무위키·블로그·위키 미러는 출처로 쓰지 않음. 그래서 새 단어는 전부 `status="Verified (web-checked)"` + `sources`가 붙음.
- 10개를 못 채우면 찾은 만큼만. 억지로 채우지 말 것.

**넣으면 안 되는 것** (CLAUDE.md 규칙 요약)
- 특정 개인(연예인·정치인·유튜버 등 실존 인물)을 조롱하는 표현 → 절대 금지.
- 성적·노골적 표현 → 금지 (애드센스 때문에 확정, 2026-10-14).
- 이미 DB에 있는 단어, 표기만 다른 같은 말, 사실상 같은 현상 → 스킵.
- 예측성 신조어(아직 안 쓰이는 말), 지어낸 통계·인용·가사·실존 인물 예문.
- 욕설·비속어는 허용 → `reg="vulgar"`, `tags`에 `"swear"`.

중복 확인:
```bash
cd scripts && python3 -c "import build_kslang_db as d; print(sorted(t[0] for c in d.CATEGORIES for t in c[-1]))" | tr ',' '\n' | grep <단어>
```
(이 import는 xlsx를 다시 쓰지만, 단어를 추가하는 주라서 어차피 커밋함.)

**작성법**
- 배치 파일(예: `/tmp/batch.py`, 저장소 밖)에 단어마다 `W(...)` 한 줄씩 쓰고 → `cd scripts && python3 add_words.py <YYYY-MM-DD> /tmp/batch.py`. 형식은 `add_words.py` 맨 위 설명 참고.
- 뜻·예문·nuance·usage(·culture)는 **en / es / zh(번체) / ja 직접 작성**. 간체는 스크립트가 OpenCC로 변환함. 일본어는 번역기 말투 말고 일본 팬들이 쓰는 표현으로(예: 최애→推し).
- `rom`은 URL이 됨: 소문자·숫자·하이픈, 기존과 겹치면 안 됨. 초성 약어는 짧은 영문(`ok`, `gs`).
- 예문은 일반 상황으로만. 실존 인물 이름을 넣지 말 것.

## 2. 에디터 픽 교체

`scripts/build_kslang_db.py`의 `EDITOR_PICKS`(5개)와 `TODAYS_CARD_POOL`(7개)을 수정함. 페이지 JS에는 `update_main_pages.py`가 자동으로 넣어줌.
- `EDITOR_PICKS`: Verified 단어 5개. 그중 2~3개는 최근 `NEW_WORDS_LOG`(이번 주 포함)에서, 나머지는 지금 뉴스·예능에서 화제인 말 중 DB에 있는 것. 첫 3개가 홈 화면에 나오니까 제일 재밌는 걸 앞에.
- 지난주 픽 5개를 전부 그대로 두지 말 것 (최소 3개 교체).
- `TODAYS_CARD_POOL`: Verified 단어 7개, 이번 주 신규 위주로 교체.
- 욕(`vulgar`) 단어는 픽·오늘의 카드에 넣지 않음 (홈 첫 화면이라서).

## 3. 퀴즈 교체

`QUIZ`는 **항상 12문제**를 유지함 (소개 문구가 "12 quick questions"라서). 매주 **가장 앞의 4문제를 빼고 새 4문제를 맨 뒤에 추가**하는 식으로 로테이션.
- 보기 4개 전부 **Verified 단어**, 정답이 딱 하나만 맞게. 헷갈리게 비슷한 단어를 보기로 쓰되, 정답이 두 개처럼 읽히면 안 됨.
- "meaning" 2문제 + "situation" 2문제. situation은 상황 문장을 5개 언어로 직접 쓰고(cn은 OpenCC 변환 후 따옴표 “ ”), 필요하면 `note`(5개 언어)로 왜 그 단어인지 설명.
- 이번 주 새 단어를 1~2개 정답으로 쓰면 좋음. 욕(`vulgar`) 단어는 퀴즈에 쓰지 않음.
- 형식은 기존 QUIZ 항목을 그대로 따라 할 것.

## 4. 빌드 + 검사

```bash
cd scripts
python3 safety_check.py
python3 build_kslang_db.py
python3 generate_word_pages.py
python3 generate_collections.py
python3 generate_quiz.py
python3 update_main_pages.py     # submit.html WARNING은 정상
python3 generate_whatsnew.py
python3 generate_sitemap.py
python3 check_site.py            # 반드시 "check_site OK"가 나와야 함
```
- 하나라도 실패하면 고치고 다시. 못 고치면 PR 본문 맨 위에 실패 내용을 적고, 그래도 PR은 올림 (Jay가 알 수 있게).
- `git status`로 의도한 파일만 바뀌었는지 확인 (build_kslang_db.py, xlsx, word/ 새 페이지·관련 페이지, guides/, quiz/, index/category/trending, whatsnew, sitemap).

## 5. PR 올리기

```bash
git add -A
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -m "Weekly update <YYYY-MM-DD>: N new words, picks, quiz"
git push -u origin weekly/<YYYY-MM-DD>
gh api repos/SAISONPAPA/KSlangDictionary/pulls -f base=main -f head=weekly/<YYYY-MM-DD> \
  -f title="주간 업데이트 <YYYY-MM-DD>" -F body=@/tmp/pr.md --jq .html_url
```

PR 본문(`/tmp/pr.md`)은 **한국어**로, Jay가 폰에서 훑어보고 머지할 수 있게:
1. 요약 한 줄 (새 단어 N개 / 픽 교체 / 퀴즈 4문제 교체 / 검사 결과)
2. 새 단어 표: 단어 · 카테고리 · 한 줄 뜻(영어) · 출처 링크
3. 에디터 픽: 이전 → 이후
4. 퀴즈: 뺀 문제 4개 / 새 문제 4개 (정답 단어 + 문제 요약)
5. 확인해 줄 것: 애매했던 판단이 있으면 여기 (예: "이 단어는 특정 그룹 팬덤에서만 써서 넣을지 고민")
6. "머지하면 GitHub Pages에 자동 배포됨" 한 줄

**PR을 직접 머지하지 말 것.** main에 push하지 말 것.
