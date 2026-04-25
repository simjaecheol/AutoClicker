# AutoClicker — Flow-Based Automation System

<p align="center">
  <img src="resources/icons/logo.png" alt="AutoClicker Logo" width="300">
</p>

사용자가 정의한 Flow(작업 흐름)를 순서대로 실행하는 데스크톱 자동화 시스템입니다. 단순 반복 클릭을 넘어 복잡한 매크로 시나리오를 구성하고 관리할 수 있습니다.

## 🚀 주요 기능

- **Flow-Based Automation**: 마우스 클릭, 키보드 입력, 지연(Delay) 등을 조합하여 하나의 실행 흐름(Flow) 생성
- **다양한 Action 지원**:
  - 마우스: 좌/우/더블 클릭, 드래그, 스크롤
  - 키보드: 단일 키 입력, 조합 키(Hotkeys), 텍스트 타이핑
- **정교한 실행 제어**: 실행 중 일시정지, 재개 및 즉시 중지 지원
- **Flow 관리**: JSON 기반의 Flow 저장, 불러오기 및 편집
- **스케줄링 (예정)**: 특정 시간 또는 반복 주기에 따른 자동 실행

## ⚙️ 설치 및 실행

### 요구 사항
- Python 3.10+
- PyQt5
- pynput

### 설치
```bash
pip install -r requirements.txt
```

### 실행
```bash
python -m src.main
```

## 📦 EXE 빌드 방법 (Windows)

PyInstaller를 사용하여 리소스를 포함한 단일 실행 파일을 만들 수 있습니다.

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --add-data "resources/icons/logo.png;resources/icons" --icon "resources/icons/logo.png" --name "AutoClicker" src/main.py
```

- `--add-data`: 로고 이미지 등 리소스 파일을 포함합니다.
- `--windowed`: 실행 시 콘솔 창이 나타나지 않게 합니다.
- `--icon`: 실행 파일 자체의 아이콘을 설정합니다.

## 📖 사용 방법 가이드

### 1. Flow 생성 및 관리
- **Flow 목록 (좌측 상단)**: 저장된 모든 자동화 흐름(Flow)을 확인할 수 있습니다.
- **새 Flow 만들기**: 상단 메뉴의 `File > New Flow` (Ctrl+N)를 선택하여 새로운 작업 흐름을 생성합니다.
- **Flow 선택**: 목록에서 항목을 클릭하면 해당 Flow의 상세 단계(Steps)가 중앙 에디터에 표시됩니다.

### 2. 입력 녹화 (Recording)
가장 빠르고 쉽게 Flow를 만드는 방법은 직접 동작을 수행하여 녹화하는 것입니다.
- **녹화 시작**: 상단 툴바의 `⏺ Record` 버튼을 누르거나, **Ctrl+Shift+R** 단축키를 입력합니다. (녹화 시작 시 프로그램이 최소화됩니다.)
- **일시 정지/재개**: 녹화 중 **Ctrl+Shift+P**를 눌러 잠시 멈추거나 다시 시작할 수 있습니다.
- **녹화 종료**: **Ctrl+Shift+R**을 다시 입력하거나 툴바의 `⏹ Stop` 버튼을 누르면 녹화가 완료되고 새로운 Flow로 자동 저장됩니다.

### 3. Step 편집 (Step Editor)
- **동작 추가 (하단 좌측)**: 'Action Palette'에서 원하는 동작(Click, Type, Delay 등)을 클릭하여 현재 Flow에 수동으로 추가할 수 있습니다.
- **단계 수정**: 중앙 에디터에서 각 단계의 좌표, 입력값, 지연 시간 등을 직접 수정할 수 있습니다.
- **순서 변경 및 삭제**: 단계를 선택하여 삭제하거나 순서를 조정할 수 있습니다.

### 4. 실행 제어 (Execution)
- **실행 시작**: 하단 우측의 `▶ Start` 버튼을 클릭합니다.
- **반복 횟수 설정**: 'Repeat Count'를 통해 Flow를 몇 번 반복할지 설정할 수 있습니다. (0으로 설정 시 무한 반복)
- **실행 중지**: `⏹ Stop` 버튼을 누르면 즉시 실행이 중단됩니다.

## ⌨️ 단축키 요약

| 기능 | 단축키 | 비고 |
| :--- | :--- | :--- |
| **녹화 시작/종료** | `Ctrl + Shift + R` | 전역(Global) 단축키 |
| **녹화 일시정지** | `Ctrl + Shift + P` | 전역(Global) 단축키 |
| **새 Flow 생성** | `Ctrl + N` | 앱 활성 시 |
| **Flow 저장** | `Ctrl + S` | 앱 활성 시 |

## 🛠 아키텍처 구조

본 프로젝트는 유지보수와 확장이 용이하도록 계층화된 아키텍처를 따릅니다.

- **UI Layer**: PyQt5 기반의 사용자 인터페이스
- **Coordinator**: UI와 엔진 간의 통신 중재 및 상태 관리
- **Flow Engine**: `threading.Event` 기반의 안전한 실행 및 제어 엔진
- **Action Registry**: 새로운 동작을 쉽게 추가할 수 있는 확장형 구조
- **Drivers**: `pynput`을 이용한 로우레벨 입력 제어 (Mouse, Keyboard)

## 📁 디렉토리 구조

```text
AutoClicker/
├── src/
│   ├── models/      # Action, Flow 데이터 모델
│   ├── engine/      # 실행 엔진 및 핸들러 레지스트리
│   ├── drivers/     # 마우스/키보드 제어 드라이버
│   ├── storage/     # JSON 기반 데이터 저장소
│   ├── ui/          # PyQt5 위젯 및 메인 윈도우
│   ├── coordinator.py # 전체 모듈 중재자
│   └── main.py      # 애플리케이션 진입점
├── docs/            # 설계 및 구현 문서
├── tests/           # 단위 테스트
└── requirements.txt
```

## 📝 라이선스
This project is licensed under the MIT License.
