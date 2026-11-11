# FakeNews Server

## 참여자 기본 정보

`Participant`는 실험 ID(`simulationId`), 선택적인 로그인 사용자 ID(`userId`), 표시 이름(`displayName`),
페르소나·성향 설명(`description`), 관심사 목록(`interests`), 생성·수정 시각을 저장합니다.
로그인 계정이 없는 AI 참여자는 `userId`를 null로 생성합니다. 참여자 ID와 사용자 ID는 서로 다른 식별자입니다.
`Participant.create(...)`로 생성하고 `updateProfile(...)`로 프로필을 수정합니다.
관심사는 공백 제거·중복 제거 후 별도 `participant_interest` 테이블에 저장하며 빈 목록도 허용합니다.
추후 조회 API에서 `description`, `interests`를 에이전트의 `profile`로 전달할 수 있습니다.
참여자 프로필 조회 API와 RetrievalAgent→PlanningAgent 연결은 구현되어 있습니다.
사용법은 `agents/README.md`를 참고하세요. 상대별 관계 데이터는 아직 구현하지 않았습니다.

기존 participant 데이터가 있다면 새 필수 컬럼(`simulation_id`, `display_name`, `description`)과 시각 컬럼을
추가하기 전에 기존 행의 값을 채우는 별도 DB 마이그레이션이 필요합니다. `ddl-auto=update`만으로 기존 데이터가 보완되지는 않습니다.

## 실험 권한과 참여자 API

모든 API에 로그인 시 발급한 Bearer 토큰이 필요합니다. 실험 생성자는 서버가 JWT 사용자로 지정합니다.
실험 소유자만 참여자 등록·프로필 수정을 할 수 있고, 소유자와 해당 실험에 등록된 사용자만
실험 정보·참여자 프로필·실험 게시글을 조회할 수 있습니다. 외부 사용자는 403입니다.
존재하지 않는 실험, 또는 URL의 실험에 속하지 않은 참여자는 404입니다.

| Method | URL | 동작 |
| --- | --- | --- |
| POST | `/api/simulations` | 실험 생성. 본문 `{"name":"뉴스 반응 실험"}` |
| GET | `/api/simulations/{simulationId}` | 권한 확인 후 실험 정보 조회 |
| POST | `/api/simulations/{simulationId}/participants` | 소유자가 참여자 등록 |
| GET | `/api/simulations/{simulationId}/participants/{participantId}/profile` | 참여자 프로필 조회 |
| PUT | `/api/simulations/{simulationId}/participants/{participantId}/profile` | 소유자가 프로필 전체 수정 |
| POST | `/api/simulations/{simulationId}/participants/{participantId}/posts` | 실험 참여자 명의로 게시글 작성 |

참여자 생성 본문:

```json
{"userId":null,"displayName":"독서가","description":"주말에 도서관을 이용함","interests":["독서","지역 소식"]}
```

실제 사용자는 기존 계정의 `userId`로 연결하고, AI 참여자는 null 또는 생략합니다.
하나의 계정은 실험마다 한 번만 등록할 수 있으며 중복은 409, 없는 사용자 연결은 404입니다.
응답의 `participantId`를 후속 URL과 RetrievalAgent의 `actor_id`에 사용합니다.
수정 본문은 `displayName`, `description`, `interests`를 모두 포함하며 실험과 계정 연결은 변경하지 않습니다.
관심사는 빈 목록을 허용하고 최대 100개, 항목당 100자입니다. 이름은 50자, 설명은 5,000자 이하이며 필수입니다.

실험 게시글 본문은 일반 게시글과 같은 `{"content":"실험 게시글입니다."}`입니다.
서버는 URL의 실험과 참여자 소속을 확인한 뒤 `simulationId`, `participantId`, `userId`를 지정합니다.
계정이 연결된 참여자의 글은 해당 사용자만 작성할 수 있습니다. 소유자도 다른 사용자 명의를 사용할 수 없습니다.
계정이 없는 AI 참여자의 글은 소유자만 작성하며 `userId`는 null이고 `participantId`로 작성자를 식별합니다.
기존 `/api/posts`와 `/post/register`는 일반 글 작성으로 유지합니다.
실험 게시글은 `/api/posts/{postId}`, `/post/{postId}` 모두 같은 실험 접근 권한을 검사합니다.

기존 DB 전환 시에는 실제 소유자를 지정한 `simulation` 데이터를 준비하고 기존 참여자·게시글의
실험/작성자 ID를 검증·보완해야 합니다. 같은 실험·사용자로 중복된 참여자는 정리한 뒤
`uk_participant_simulation_user` 제약을 적용해야 합니다. 기존 일반 글을 특정 실험으로 자동 배정하지 않습니다.


## 주요 기능

## 개발 컨벤션

### Commit Convention

| 태그 | 설명 |
| --- | --- |
| `feat` | 새로운 기능 구현 |
| `modify` | 기능 변화가 있는 코드 수정 |
| `docs` | README, Wiki 등 문서 수정 |
| `add` | 부수적인 코드·라이브러리 추가 또는 새 파일 생성 |
| `remove` | 폴더·파일 또는 불필요한 코드 삭제 |
| `fix` | 버그 및 오류 해결 |
| `rename` | 파일 이름 변경 또는 이동 |
| `refactor` | 기능 변화 없이 코드 구조 개선 |
| `perf` | API 호출 횟수, 응답 시간 등 성능 개선 |
| `correct` | 비즈니스 로직 변화 없는 문법·타입·이름 수정 |
| `style` | 코드 포맷 등 스타일 수정 |
| `test` | 테스트 추가 또는 수정 |
| `chore` | 빌드·패키지 설정 등 운영 코드 외 기타 변경 |

커밋 메시지는 한 커밋에 한 가지 작업만 담고, 명령형의 간결한 문장으로 작성합니다.

```text
#이슈번호 태그: 작업 내용
```

예시:

```bash
git commit -m "#1 feat: 회원가입 API 구현"
```

## 게시글 작성 API (MVP)

로그인한 사용자가 텍스트 본문을 작성합니다. 이미지·영상 업로드, 해시태그, 게시글 타입 선택, AI 글쓰기 보조는 포함하지 않습니다.

| Method | URL | 인증 | 설명 |
| --- | --- | --- | --- |
| `POST` | `/api/posts` | Bearer | 게시글 작성 |
| `GET` | `/api/posts/{postId}` | Bearer | 작성된 게시글 조회 |

기존 `/post/register`, `/post/{postId}` 주소도 지원합니다.

요청 본문:

```json
{"content":"첫 번째 게시글입니다.\n본문을 작성합니다."}
```

`content`는 필수이며 공백만 입력할 수 없고 최대 10,000자입니다. 작성자는 JWT의 사용자로 지정합니다. 클라이언트가 작성자 ID를 전달해도 사용하지 않습니다.

성공 시 `201 Created`와 `{"postId":1}`을 반환합니다. 본문 검증 실패는 `400`, 인증 실패는 `401`, 없는 게시글 조회는 `404`를 반환합니다.
