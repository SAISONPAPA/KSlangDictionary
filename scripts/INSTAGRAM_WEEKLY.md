# 인스타그램 주간 예약 플레이북 (@hellokslang)

매주 월요일 예약 작업이 이 파일을 보고 그대로 실행함. 이번 주 **화·목·토 오전 10시(KST)**에 올라갈 캐러셀 3개를 만들어서 Metricool에 예약함.
CLAUDE.md의 규칙(단어 선정 규칙, 인스타그램 섹션)이 이 문서보다 우선함. **main 브랜치에는 아무것도 커밋하지 않음** — 이미지는 `social` 브랜치에만 올림.

## 0. 준비

```bash
cd <repo>   # SAISONPAPA/KSlangDictionary
git fetch origin main social
git checkout -B main origin/main          # 단어 데이터는 라이브(main) 기준
git worktree add ../social origin/social -B social   # 이미지·게시 기록용 브랜치
cat ../social/posted.json                 # 지금까지 올린 단어 목록
```

- Metricool 도구(`createScheduledPost`, `getScheduledPosts`, `getBrandSettings`)가 없으면: 3~5단계(카드 생성·social 브랜치 push)까지만 하고, 캡션과 이미지 주소를 결과에 남겨서 Jay가 직접 예약하게 할 것.
- 브랜드: blogId `7434570`, 시간대 `Asia/Seoul`, Instagram `hellokslang`.

## 1. 이번 주 이미 예약된 게 있는지 확인

`getScheduledPosts`(brandId 7434570, 이번 주 월요일 00:00 ~ 다음 주 월요일 00:00, Asia/Seoul).
- 이미 예약된 날(화/목/토)은 건너뜀. 3개 다 있으면 종료.
- 무료 플랜은 **한 달에 예약 20개까지**. 이번 달 예약 수(이번 달 1일~말일 조회)가 18개 이상이면 남은 만큼만 만들 것.

## 2. 단어 고르기 (3개)

조건 — 전부 지킬 것:
- `status`가 `"Verified (web-checked)"`인 단어만.
- `posted.json`에 있는 단어는 다시 쓰지 않음.
- `DETAILS`의 `register`가 `"vulgar"`이거나 `tags`에 `"swear"`가 있으면 제외 (피드 게시물이라서).
- 실존 인물·특정 그룹만 아는 내부 용어보다 **해외 팬이 바로 써먹을 수 있는 말** 우선.
- 카테고리는 CLAUDE.md의 요일별 로테이션 순서(아이돌용어 → 밈 → 팬덤 → 방송예능 → 연애썸)를 이어서 씀. `posted.json`의 마지막 항목 카테고리 다음 것부터 3개.
- 최근 `NEW_WORDS_LOG`(사이트 신규 단어)에 있는 Verified 단어가 조건에 맞으면 1개는 그걸로 (사이트 신규 단어 홍보).

후보 뽑기:
```bash
cd scripts && python3 -c "
import json, build_kslang_db as d
posted = {p['kr'] for p in json.load(open('../../social/posted.json'))}
for cat_kr, cat_en, terms in d.CATEGORIES:
    for t in terms:
        det = d.DETAILS.get(t[0], {})
        if t[-1].startswith('Verified') and t[0] not in posted and det.get('register') != 'vulgar' and 'swear' not in det.get('tags', []):
            print(cat_en, '|', t[0], '|', t[2])
"
git checkout -- ../data/kslang-slang-database.xlsx   # import 때문에 xlsx가 다시 써짐 → 되돌림
```

## 3. 카드 만들기 + 눈으로 확인

```bash
cd scripts
python3 generate_instagram_cards.py --carousel "<단어>"     # 3개 각각
git checkout -- ../data/kslang-slang-database.xlsx
```
출력: `assets/instagram/<오늘>-<slug>/slide-1..4.png` (.gitignore라 main에 안 올라감).
- **4장 전부 Read로 열어서 확인**: 글자가 카드 밖으로 넘치거나, 스티커·테이프가 글자를 가리거나, 한글이 네모(□)로 깨지면 안 됨.
- 문제가 있으면 그 단어는 버리고 다른 단어로 교체 (생성기 코드를 이번 작업에서 고치지 말 것 — 결과에 "생성기 문제: …"로 적어서 Jay에게 알림).

## 4. 캡션 쓰기 (영어 메인 + 스페인어 한 줄)

형식 (입덕 게시물 기준):
```
<첫 줄 훅 — 상황/공감, 이모지 1개>

<단어> (<rom>) = <영어 뜻 한 줄>

"<예문 kr>" → "<예문 en>"

<댓글 유도 질문> 👇
Save this so you never forget the word ✨

🇪🇸 <단어> = <스페인어 뜻 한 줄>. <짧은 스페인어 질문>

#kpop #koreanslang #learnkorean #<주제 태그 1개> #hellokslang
```
- 뜻·예문은 DB의 en/es 값을 그대로 쓸 것 (지어내지 않음). 실존 인물 이름, 가사, 지어낸 통계 금지.
- 해시태그는 4~5개. 주제 태그 예: #kdrama #kpopfans #koreanmemes #kvariety #koreanculture.

## 5. 이미지 올리기 (social 브랜치)

```bash
cp -r ../assets/instagram/<오늘>-<slug> ../../social/cards/    # 3개 전부
cd ../../social && git add cards && git commit -m "Cards for week of <월요일 날짜>" && git push origin social
# 공개 주소가 열리는지 확인 (200 image/png 이어야 함)
curl -s -o /dev/null -w "%{http_code} %{content_type}\n" https://raw.githubusercontent.com/SAISONPAPA/KSlangDictionary/social/cards/<폴더>/slide-1.png
```
커밋할 때 `-c user.name="Claude" -c user.email="noreply@anthropic.com"` 사용.

## 6. Metricool 예약

단어마다 `createScheduledPost` 한 번씩:
- 날짜: 이번 주 화·목·토 `10:00:00`, `publicationDate.timezone` = `Asia/Seoul`, `date`는 `+09:00`.
- `providers`: `[{"network":"instagram"}]`, `instagramData`: `{"type":"POST","collaborators":[],"showReelOnFeed":true,"isAiGenerated":false}`
- `media`: slide-1~4의 raw.githubusercontent.com 주소 4개 (순서대로) → 캐러셀이 됨.
- `autoPublish: true`, `draft: false`.
- 에러가 나면 같은 내용으로 계속 재시도하지 말고 에러 메시지를 결과에 남김.

## 7. 기록 + 결과

- `posted.json`에 `{"kr", "rom", "category", "date", "planner_url"}`로 3개 추가 → social 브랜치에 커밋·push.
- 결과는 한국어로 짧게 (Jay가 폰 알림으로 봄):
  - 예약한 단어 3개: 요일 · 단어 · 한 줄 뜻 · Metricool 링크(`plannerUrl`)
  - 이번 달 예약 수 / 20
  - 건너뛴 게 있으면 이유
- 링크는 `[제목](URL)` 형식만.
