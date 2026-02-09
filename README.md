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

## ✨ Key Features

### 오류 복구 시스템

크롤링 중 인터넷이 끊기거나 예기치 못한 에러로 중단되더라도 걱정할 필요가 없습니다.

- **Checkpointing:** 수집된 페이지와 인덱스 위치를 `crawling_state.json`에 실시간으로 기록합니다.
- **Auto-Resume:** 재실행 시, 마지막으로 수집했던 지점부터 자동으로 작업을 이어갑니다.
- **State Cleaning:** 작업이 정상적으로 완료되면 상태 파일은 자동으로 삭제됩니다.

### 하이브리드 데이터 추출

상세 페이지의 정보 누락과 DOM 구조 변화에 대응하기 위해 이원화된 수집 전략을 사용합니다.

- **Grid First:** 목록(Grid) 화면에서 `공고일자`, `공고분류(공사/용역)`, `공고구분` 등 핵심 정보를 우선 추출합니다.
- **Conditional Merge:** 상세 페이지 데이터가 비어있을 경우, 목록에서 수집한 데이터를 유지하여 데이터 유실을 원천 차단합니다.

---

## 🏗️ Architecture & Design

본 프로젝트는 **"지속 가능한 유지보수"** 를 핵심 가치로 삼아, **계층형 아키텍처**와 **객체 지향 디자인 패턴**을 적용했습니다.

### Design Patterns

- **Template Method Pattern (`BaseCrawler`):**
    - 크롤링의 생명주기(`Setup` → `Maps` → `Extract` → `Teardown`)를 부모 클래스에서 제어합니다.
    - **의도:** 리소스 해제(`close`) 누락 방지 및 공통 에러 처리를 강제하여 프로세스 안정성을 보장합니다.

- **Factory Pattern (`BidFactory`):**
    - Raw Data를 도메인 모델(`BidNotice`)로 변환하는 책임을 분리하여, 데이터 정제 로직(날짜 포맷팅, 금액 파싱)을 일원화했습니다.

- **Strategy Pattern (`BaseStorage`):**
    - 데이터 저장소 로직을 추상화하여, 비즈니스 로직 수정 없이 저장 매체(MySQL ↔ CSV)를 유연하게 교체할 수 있습니다.



### Project Structure

역할과 책임에 따라 명확히 모듈화된 디렉토리 구조를 가집니다.

```text
nuri-bid-collector/
├── config/             # [Config] 설정 파일
│   ├── search.yaml     # ├── 검색 키워드 및 날짜 조건
│   └── system.yaml     # └── DB 연결 및 시스템 설정
├── src/
│   ├── core/           # [Core] BaseCrawler, PageContext
│   ├── crawlers/       # [Impl] NuriCrawler (상태 복구 및 네비게이션 로직)
│   │   └── components/ #      ├── NuriParser, NuriNavigator, Extractor
│   ├── storage/        # [Impl] MySqlStorage (SQLAlchemy)
│   ├── models/         # [DTO] Pydantic 데이터 모델
│   └── main.py         # [Entrypoint] 실행 진입점
├── run.sh              # [Script] Mac/Linux 실행 스크립트
├── run.bat             # [Script] Windows 실행 스크립트
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
