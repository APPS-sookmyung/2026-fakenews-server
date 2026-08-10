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

### 환경 설정

`src/main/resources/application.properties`에 로컬 데이터베이스 연결 정보를 설정합니다.

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/fakenews
spring.datasource.username=your_username
spring.datasource.password=your_password
```

비밀번호와 같은 민감 정보는 Git에 커밋하지 않고 환경 변수 또는 별도의 로컬 설정 파일로 관리합니다.

### 실행

Windows:

```bash
./gradlew.bat bootRun
```

macOS/Linux:

```bash
./gradlew bootRun
```

### 테스트

Windows:

```bash
./gradlew.bat test
```

macOS/Linux:

```bash
./gradlew test
```

## 프로젝트 구조

```text
src/
├─ main/
│  ├─ java/com/fakenews/server/
│  │  ├─ domain/                 # 도메인별 기능
│  │  │  └─ {domain}/
│  │  │     ├─ controller/       # HTTP 요청 및 응답 처리
│  │  │     ├─ service/          # 비즈니스 로직
│  │  │     ├─ repository/       # 데이터 접근
│  │  │     ├─ entity/           # JPA 엔티티
│  │  │     └─ dto/              # 요청 및 응답 객체
│  │  ├─ global/                 # 전역 공통 기능
│  │  │  ├─ config/              # 애플리케이션 설정
│  │  │  ├─ exception/           # 공통 예외 처리
│  │  │  └─ response/            # 공통 응답 형식
│  │  └─ FakenewsServerApplication.java
│  └─ resources/
│     └─ application.properties  # 애플리케이션 설정
└─ test/
   └─ java/com/fakenews/server/  # 테스트 코드
```

새 기능은 `domain` 아래에 도메인 단위로 패키지를 만들고, 해당 도메인 안에서 역할별로 나눕니다. 예를 들어 회원 기능은 `domain/member/controller`, `domain/member/service`와 같이 구성합니다.

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

### Branch Convention

| 브랜치 | 설명 |
| --- | --- |
| `main` | 출시 가능한 프로덕션 코드 |
| `dev` | 다음 배포 버전의 개발 코드를 통합하는 브랜치 |
| `feat` | 기능 개발 |
| `fix` | 에러 및 버그 수정 |
| `docs` | README 및 문서 수정 |
| `refactor` | 기능 변화 없는 코드 리팩터링 |
| `modify` | 기능 변화가 있는 코드 수정 |
| `chore` | 빌드 설정 등 기타 작업 |

브랜치는 다음 형식으로 생성합니다.

```text
태그/#이슈번호-기능-이름
```

예시:

```bash
git switch -c feat/#1-member-signup
```

작업 완료 후 대상 브랜치에 Pull Request를 생성하고, 리뷰 및 확인을 거쳐 병합합니다.

### Issue Convention

| 태그 | 설명 |
| --- | --- |
| `feat` | 기능 추가 |
| `fix` | 에러 및 버그 수정 |
| `docs` | README 및 문서 수정 |
| `refactor` | 기능 변화 없는 코드 리팩터링 |
| `modify` | 기능 변화가 있는 코드 수정 |
| `perf` | 성능 개선 |
| `chore` | 그 외 작업 |

이슈 제목은 다음 형식으로 작성합니다.

```text
태그: 작업 내용
```

예시: `feat: 회원가입 API 구현`

### 개발 시 사용하는 패키지

#### `domain/`

회원, 게시글, 뉴스 등 도메인별 코드를 관리합니다. 각 도메인 내부는 `controller`, `service`, `repository`, `entity`, `dto`처럼 역할에 따라 구분합니다.

#### `controller/`

클라이언트의 HTTP 요청을 받고 응답을 반환합니다. 비즈니스 로직은 직접 작성하지 않고 `service`를 호출합니다.

#### `service/`

도메인의 비즈니스 로직과 트랜잭션을 관리합니다.

#### `repository/`

JPA를 사용해 데이터베이스에 접근합니다.

#### `entity/`

데이터베이스 테이블과 매핑되는 JPA 엔티티를 관리합니다. 엔티티를 API 응답으로 직접 반환하지 않습니다.

#### `dto/`

API 요청과 응답에 사용하는 객체를 관리합니다. 요청용과 응답용 DTO의 역할을 명확히 구분합니다.

#### `global/`

특정 도메인에 속하지 않는 설정, 공통 예외, 공통 응답 등 애플리케이션 전역 기능을 관리합니다.

#### `FakenewsServerApplication.java`

Spring Boot 애플리케이션의 시작점입니다. 실행 설정만 담당하며 개별 API나 비즈니스 로직을 직접 작성하지 않습니다.
