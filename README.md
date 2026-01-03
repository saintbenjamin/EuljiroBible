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
