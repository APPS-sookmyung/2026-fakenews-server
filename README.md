# FakeNews Server


## 주요 기능


## 기술 스택

| 구분 | 기술 |
| --- | --- |
| Framework | Spring Boot 4.1.0 |
| Language | Java 17 |
| Build | Gradle |
| Web | Spring MVC |
| Database | MySQL |
| ORM | Spring Data JPA |
| Validation | Jakarta Bean Validation |
| Library | Lombok |
| Test | JUnit Platform, Spring Boot Test |

## 시작하기

### 요구 사항

- JDK 17 이상
- MySQL

Gradle은 Wrapper가 포함되어 있어 별도로 설치하지 않아도 됩니다.


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

