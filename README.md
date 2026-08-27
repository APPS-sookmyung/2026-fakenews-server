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

## 인증 API

비밀번호는 BCrypt로 해시해 저장하며, 로그인 후 발급된 JWT를 Bearer 헤더로 전달합니다.

| Method | URL | 인증 | 설명 |
| --- | --- | --- | --- |
| `POST` | `/api/auth/signup` | 불필요 | 회원가입 |
| `POST` | `/api/auth/login` | 불필요 | JWT 로그인 |
| `GET` | `/api/auth/me` | Bearer | 현재 사용자 조회 |

회원가입/로그인 요청 예시:

```json
{"email":"user@example.com","password":"password123","name":"홍길동"}
```

로그인 응답의 `accessToken`은 `Authorization: Bearer <accessToken>` 헤더로 전달합니다.
운영 환경에서는 `DB_URL`, `DB_USERNAME`, `DB_PASSWORD`, `JWT_SECRET` 환경 변수를 설정해야 합니다.

## 시작하기

### 요구 사항

- JDK 17 이상
- MySQL

Gradle은 Wrapper가 포함되어 있어 별도로 설치하지 않아도 됩니다.

### 1. 데이터베이스 생성

MySQL Workbench 또는 MySQL 콘솔에서 실행합니다.

```sql
CREATE DATABASE fakenews_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
```

### 2. 실행 환경 설정

PowerShell에서 현재 터미널 세션에 MySQL 비밀번호와 JWT 비밀키를 설정합니다.

```powershell
$env:DB_PASSWORD="MySQL root 비밀번호"
$env:JWT_SECRET="32바이트-이상의-충분히-긴-무작위-문자열"
```

MySQL 사용자 또는 주소가 기본값과 다르면 추가로 설정합니다.

```powershell
$env:DB_USERNAME="root"
$env:DB_URL="jdbc:mysql://localhost:3306/fakenews_db?useSSL=false&characterEncoding=UTF-8&serverTimezone=UTC"
```

### 3. 서버 실행

```powershell
java -version
.\gradlew.bat bootRun
```

`Started FakenewsServerApplication`이 출력되고 프로세스가 계속 실행되면 정상입니다.
최초 실행 시 JPA가 `users` 테이블을 자동으로 생성합니다.

### 4. 인증 동작 확인

서버를 실행한 상태에서 별도의 PowerShell 창을 열어 회원가입합니다.

```powershell
$signup = @{ email="test@example.com"; password="password123"; name="테스트" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/api/auth/signup" -ContentType "application/json" -Body $signup
```

로그인하고 토큰을 저장합니다.

```powershell
$login = @{ email="test@example.com"; password="password123" } | ConvertTo-Json
$response = Invoke-RestMethod -Method Post -Uri "http://localhost:8080/api/auth/login" -ContentType "application/json" -Body $login
$token = $response.accessToken
```

Bearer 토큰으로 현재 사용자 정보를 조회합니다.

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:8080/api/auth/me" -Headers @{ Authorization="Bearer $token" }
```


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
