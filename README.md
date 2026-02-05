# Nuri Bid Collector

**Nuri Bid Collector**는 동적으로 렌더링되는 누리장터의 입찰 공고를 안정적으로 수집하기 위해 설계된 동적 크롤러입니다.

---

## 🚀 Quick Start

복잡한 환경 설정 없이, 제공되는 자동화 스크립트로 즉시 수집을 시작할 수 있습니다.
스크립트는 `가상환경 생성 → 의존성 설치 → 브라우저 바이너리 설정 → 크롤러 실행`의 전 과정을 자동으로 처리합니다.

### 1. Clone Repository

먼저 프로젝트를 로컬 환경으로 복제하고 디렉토리로 이동합니다.

```bash
git clone https://github.com/HSHwan/nuri-bid-collector.git
cd nuri-bid-collector

```

### 2. Run Script

운영체제에 맞는 스크립트를 실행하면 즉시 수집이 시작됩니다.

#### Windows

```batch
.\run.bat

```

#### macOS / Linux

```bash
chmod +x run.sh
./run.sh

```

---

## 🏗️ Architecture & Design

본 프로젝트는 **"지속 가능한 유지보수"** 를 핵심 가치로 삼아, **계층형 아키텍처**와 **객체 지향 디자인 패턴**을 적용했습니다.

### Design Patterns

- **Template Method Pattern (`BaseCrawler`):**
    - 크롤링의 생명주기(`Setup` → `Maps` → `Extract` → `Teardown`)를 부모 클래스에서 제어합니다.
    - **의도:** 리소스 해제(`close`) 누락 방지 및 공통 에러 처리를 강제하여 프로세스 안정성을 보장합니다.


- **Strategy Pattern (`BaseStorage`):**
    - 데이터 저장소 로직을 추상화하여, 비즈니스 로직 수정 없이 저장 매체(MySQL ↔ CSV)를 유연하게 교체할 수 있습니다.



### Project Structure

역할과 책임에 따라 명확히 모듈화된 디렉토리 구조를 가집니다.

```text
nuri-bid-collector/
├── config/             # [Config] 설정 파일 디렉토리
│   ├── search.yaml     # ├── [Biz] 검색 조건 및 필터 설정
│   └── system.yaml     # └── [Infra] DB 연결 및 시스템 환경 설정
├── src/
│   ├── core/           # [Core] BaseCrawler, BaseStorage, Container (DI)
│   ├── crawlers/       # [Impl] NuriCrawler (사이트별 구체적 로직)
│   ├── storage/        # [Impl] MySqlStorage (DB 저장 로직)
│   ├── models/         # [DTO] Pydantic 데이터 모델
│   ├── utils/          # [Util] ConfigLoader, Logger, CLI 파서
│   └── main.py         # [Entrypoint] 애플리케이션 진입점
├── docker-compose.yml  # [Infra] DB 및 App 컨테이너 구성
├── Dockerfile          # [Infra] Playwright 전용 이미지 빌드 설정
├── run.sh              # [Script] 자동 실행 스크립트 (Mac/Linux)
├── run.bat             # [Script] 자동 실행 스크립트 (Windows)
└── README.md

```

---

## 🛠️ Tech Stack & Environment

안정적인 운영을 위해 검증된 최신 기술 스택을 채택했습니다.

| Component | Technology | Selection Reason |
| --- | --- | --- |
| **Language** | Python 3.9+ | Type Hinting 지원 및 최신 라이브러리 호환성 |
| **Core** | `Playwright` | 동적 페이지의 `Auto-waiting` 지원 및 Selenium 대비 빠른 속도 |
| **Validation** | `pydantic` | 런타임 데이터 검증 및 객체 매핑 |
| **ORM** | `sqlalchemy` | SQL Injection 방지 및 DB 추상화 |
| **Infra** | `Docker` | 환경 독립적인 실행 보장 |

---

## 📝 Manual Execution (Docker)

자동화 스크립트 대신, Docker를 통해 격리된 환경에서 실행할 수도 있습니다.

```bash
# 1. Clone Repository
git clone https://github.com/HSHwan/nuri-bid-collector.git
cd nuri-bid-collector

# 2. Build & Run (MySQL + Crawler)
docker-compose up -d --build

# 3. Check Logs
docker-compose logs -f crawler

```
