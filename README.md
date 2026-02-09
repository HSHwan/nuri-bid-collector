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

## 🛠️ Environment & Dependencies

본 프로젝트는 다음 환경에서 개발 및 테스트되었습니다. 로컬 실행 시 아래 버전 충족을 권장합니다.

- **OS:** Windows 10/11, macOS, Linux (Ubuntu 20.04+)
- **Python:** 3.9 이상 (Type Hinting 및 최신 문법 사용)
- **Libraries:**
    - `playwright (>=1.58.0)`: 동적 웹 페이지 제어 및 렌더링
    - `sqlalchemy (>=2.0.0)`: ORM 기반 데이터베이스 추상화
    - `pymysql`: MySQL 드라이버 (순수 Python 구현체)
    - `pydantic (>=2.0.0)`: 엄격한 데이터 유효성 검사 및 스키마 정의
    - `pyyaml`: 설정 파일 로딩

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
docker-compose logs -f nuri-crawler

```

## 🚫 한계 및 개선 아이디어

### 한계점

1. **브라우저 리소스 부하:** Headless 브라우저를 구동하므로 단순 HTTP 요청 방식보다 CPU/Memory 사용량이 높습니다.
2. **DOM 의존성:** 웹사이트의 Class Name이나 ID 구조가 변경될 경우 파서(`Parser`) 코드의 수정이 필요합니다.
3. **동기 처리 속도:** 안정성을 위해 순차적으로 페이지를 탐색하므로, 대량의 데이터 수집 시 막대한 시간이 소요됩니다.

### 개선 아이디어

1. **비동기 병렬 처리:** `playwright.async_api`를 도입하여, 목록 수집과 상세 페이지 파싱을 비동기로 처리해 수집 속도를 향상시킬 수 있습니다.
2. **Headless 탐지 우회 강화:** User-Agent 로테이션 및 Stealth 플러그인을 적용하여 차단 가능성을 최소화합니다.
3. **알림 시스템 통합:** 크롤링 완료 또는 에러 발생 시 Slack/Email로 리포트를 전송하는 기능을 추가하여 모니터링 편의성을 높입니다.