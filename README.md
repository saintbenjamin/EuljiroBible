# EuljiroBible (을지로 바이블)

**EuljiroBible**은 대한예수교장로회(통합) 을지로교회의 주일예배를 포함한 모든 기도모임을 위해 개발된 성경 검색 및 슬라이드 고속 출력 애플리케이션입니다.  
GUI와 CLI 양쪽을 지원하며, 다국어 환경과 다양한 성경 버전을 지원합니다.

**EuljiroBible** is a Bible search and rapid slide-show application developed for  
**The Eulji-ro Presbyterian Church (TongHap)**.  
It supports both GUI and CLI modes, with multi-language support and advanced verse/keyword search.


---

## 📚 Documentation

Detailed developer-oriented documentation generated with **Sphinx (Read the Docs theme)** is available at:

👉 **https://saintbenjamin.github.io/EuljiroBible**

The documentation includes:
- Module and package references
- Detailed API documentation extracted from docstrings
- Internal design notes and responsibilities of each component

This documentation is intended for developers and maintainers who want to
understand or extend the internal architecture of EuljiroBible.

---

## 주요 기능 | Features

- 🔍 **구절 검색 / Verse Lookup** (GUI & CLI)
- 🔑 **키워드 검색 / Keyword Search** (GUI & CLI)
- 🌐 **다국어 지원 / Multi-language Support** (Korean, English, etc.)
- 📖 다양한 성경 번역본 / Multiple Bible Translations (개역개정, KJV, Hebrew, Greek, ...)
- 🖥️ PySide6 기반 GUI
- 🧑‍💻 빠르고 직관적인 CLI 환경
- 🗂️ JSON 기반 성경 텍스트 및 구조

---

## 설치 방법 | Installation

Python 3.10 이상이 필요합니다.  
다음 명령어로 필요한 패키지를 설치할 수 있습니다:

```bash
pip install -r requirements.txt
```

위 명령은 주로 GUI 실행에 필요한 의존성 설치용입니다.  
The command above mainly installs dependencies required for the GUI.

---

## CLI 설치 방법 | Installing the CLI

아직 PyPI에 배포하지 않았더라도, 저장소를 클론한 뒤 프로젝트 루트에서 아래처럼 설치하면
`bible` 명령어를 바로 사용할 수 있습니다:

Even if the package has not been published to PyPI yet, you can still enable the
`bible` command locally by installing the project from the cloned repository root:

```bash
pip install -e .
```

이 설치는 `pyproject.toml`에 정의된 CLI 엔트리포인트를 등록하므로,
설치 후에는 어디서든 `bible` 명령으로 실행할 수 있습니다.

This installs the CLI entry point defined in `pyproject.toml`, so after installation
you can run the `bible` command from anywhere.

예시:

```bash
cd /path/to/EuljiroBible
pip install -e .

bible --help
bible NKRV John 3:16
bible search NKRV 믿음 은혜
```

만약 macOS/Homebrew Python 등에서 `externally-managed-environment` 오류가 나면,
가상환경을 만든 뒤 같은 명령을 실행하면 됩니다:

If you see an `externally-managed-environment` error on environments such as
macOS/Homebrew Python, create a virtual environment first and then run the same install:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## GUI 실행 방법 | Launching the GUI

아래 파일을 더블클릭하거나 터미널에서 실행하면 GUI 모드가 시작됩니다:

```bash
python EuljiroBible.py
```

---

## CLI 사용법 | CLI Usage

```bash
# 구절 검색 / Verse lookup
bible NKRV John 3:16

# 키워드 검색 / Keyword search
bible search NKRV 믿음 은혜

# 도움말 / Help
bible --help
bible search --help
```

---

## 디렉토리 구조 | Directory Structure

```
EuljiroBible/
├── cli/                # CLI 진입점 및 명령어 / CLI entry and commands
├── core/               # 공통 로직 처리 / Core logic and data handling
├── data/               # 성경 본문 데이터 / Verse content in JSON format
├── gui/                # GUI 구성요소 (PySide6)
├── json/               # 버전 및 이름 메타데이터 / Version metadata (aliases, names)
├── .gitignore          # Git 추적에서 제외할 항목 / Git ignore rules
├── EuljiroBible.py     # GUI 모드 실행 스크립트 / Launch script for GUI mode
├── LICENSE             # 라이선스 / License (MIT + Attribution)
├── README.md           # 현재 문서 / This file
└── requirements.txt    # 필요한 패키지 목록 / Required Python packages
```

---

## 라이선스 | License

본 프로젝트는 **MIT 라이선스 (저작자 표기 요구 포함)** 하에 배포됩니다.  
This project is licensed under the **MIT License with Attribution Requirement**.  
자세한 사항은 [LICENSE](./LICENSE) 파일을 참조하세요.  
See [LICENSE](./LICENSE) for details.

---

## 개발자 | Author

**Benjamin Jaedon Choi**  
GitHub: [saintbenjamin](https://github.com/saintbenjamin)  
Affiliated Church: The Eulji-ro Presbyterian Church  
(대한예수교장로회(통합) 을지로교회, 대한민국 서울특별시 중구 을지로20길 24-10)
