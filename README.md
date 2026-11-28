# StreamHDR

[English](README.en.md)

### 플러그인 소개

StreamHDR은 Steam Remote Play에 HDR 스트리밍을 지원하는 Decky 플러그인입니다. HDR 출력이 가능한 기기에 최신 SteamOS가 설치되어 있다면 이 플러그인을 통해 BT.2020 색역의 HDR 스트리밍이 가능하도록 설정할 수 있습니다.

### 어떻게 가능한가

SteamOS는 HDR 스트리밍을 하지 않습니다. HDR로 표시된 배지는 실제로는 미리 정해진 HDR 호환성 정보에 의한 표시일 뿐이고, 호스트에서 인코딩되어 전송되는 스트림은 BT.709 SDR 색역입니다. 즉 SDR 스트림을 그저 HDR 디스플레이로 렌더링만 하고 있다는 것이고, 그조차 미리 정해진 호환성 값이 없으면 SDR로 렌더링한다는 것입니다.

StreamHDR은 이러한 문제를 해결하기 위해 개발되었습니다. 이 플러그인이 하는 일은 단순합니다. Steam의 스트리밍 클라이언트(`streaming_client`)를 래핑하는 방법으로 Steam이 호스트에 보내는 스트리밍 요청을 HDR로 수정하고, 클라이언트에서 HDR 스트림이 정상적인 밝기로 렌더링되도록 설정합니다. 그것이 전부입니다.

## 설치 방법

스트리밍을 실행하는 기기에 [Decky Loader](https://decky.xyz/)가 먼저 설치되어 있어야 합니다.

### 빠른 설치

- 빠르게 설치하려면 Decky Loader의 개발자 메뉴에서 "URL에서 플러그인 설치"를 실행하고 릴리스 파일의 주소를 입력하여 설치합니다.

```text
https://github.com/gyuholee-dev/decky-stream-hdr/releases/download/v1.0.0/decky-stream-hdr-1.0.0.zip
```

### 압축 파일로 설치

1. [GitHub Releases](https://github.com/gyuholee-dev/decky-stream-hdr/releases)에서 `decky-stream-hdr-1.0.0.zip`을 내려받습니다.
2. Decky 설정에서 "개발자 모드"를 켭니다.
3. Decky 설정의 개발자 메뉴에서 "ZIP 파일에서 플러그인 설치"를 실행하고 내려받은 파일을 선택하여 설치합니다.

### 설치 후

설치가 완료되면 Decky 메뉴에서 StreamHDR을 열고 메뉴에서 HDR Streaming을 켠 뒤 Remote Play를 실행하십시오.

## 사용 방법

1. 플러그인 메뉴에서 HDR Streaming을 켠 뒤 Remote Play를 실행하십시오. 이미 실행 중이라면 스트리밍을 종료한 뒤 다시 실행해야 적용됩니다.
2. 스트리밍 콘텐츠 밝기는 HDR 스트리밍이 어느 정도의 밝기로 출력될지 결정하는 기준값입니다. 이 값을 변경하고자 할 경우 스트리밍을 종료해 주십시오.
3. Contrast, Gamma, Saturation은 HDR 출력 이미지를 사용자의 선호에 맞게 조정할 수 있는 설정입니다. 이 값들은 스트리밍 중에도 자유롭게 변경할 수 있습니다.
4. 플러그인의 모든 설정은 Remote Play에만 적용되며, 클라이언트 기기에 직접 설치하여 실행하는 게임의 화면에는 영향이 없습니다.

## HDR 스트리밍 요구사양

- 호스트(게임을 실행하는 PC): HDR 게임을 원활하게 실행 가능한 사양의 PC가 필요합니다.
- 클라이언트(스트리밍을 실행하는 기기): HDR 디스플레이가 내장되거나 또는 외장으로 연결된 기기에서 SteamOS를 게임 모드로 실행해야 합니다.
- 네트워크: 고대역폭 저지연 네트워크 환경을 권장합니다. 거치 기기일 경우 1GbE 이상 속도의 유선 연결을 권장하며, 핸드헬드 기기일 경우 Wi-Fi 절전을 끄는 걸 권장합니다. 공유기에서 MLO(Multi-Link Operation)를 켜 두면 MLO를 지원하지 않는 기기(Wi-Fi 6E 등)의 6GHz 연결에서 지연이 커지고 패킷 손실이 생겨 원활한 게임플레이가 어려울 수 있으니, MLO를 끄거나 5GHz Wi-Fi에 연결하십시오.
- Lenovo Legion Go 2 등 OLED 내장 디스플레이가 탑재된 기기에서 HDR 스트리밍을 할 경우, 콘텐츠 휘도 제한 완화가 확인된 SteamOS 3.10.1 이상 버전을 권장합니다.
- Steam에 2026년 10월부터 추가된 PyroWave 동영상 옵션을 필수로 사용해야 합니다. PyroWave는 Steam의 일반 대역폭 제한이 적용되지 않고 전송량이 1Gbps 이상으로 매우 큽니다(YUV 4:4:4 켬, 품질 조정 2에서 1080p 기준 최대 1.1Gbps, 6GHz Wi-Fi 연결에서 테스트). 스트리밍 플레이 중 프레임레이트 저하나 스터터링이 나타날 경우 YUV 4:4:4를 끄고 품질 조정을 1 이하로 낮추십시오 (1080p 기준 약 620~730Mbps).

## 호스트 권장 설정

- 호스트의 Steam 설정 > Remote Play > 고급 호스트 설정
- 고급 호스트 옵션 사용: 켬
- 스트리밍 시 기본 디스플레이: HDR 디스플레이
- 스트리밍 디스플레이 HDR: 기본 또는 맞춤 설정 (HDR 사용: 켬)
- NVIDIA GPU에서 NVFBC 캡처 사용: 끔
- 하드웨어 인코딩 사용: 켬
- 네트워크 트래픽 우선순위 조정: 켬
- Windows 설정 > 시스템 > 디스플레이 > HDR: HDR 사용 켬, SDR 콘텐츠 밝기 50
- 게임의 HDR 설정: 최대 밝기 1000 nits

## 클라이언트 권장 설정

- 클라이언트의 Steam 설정 > Remote Play > 고급 클라이언트 설정
- 고급 클라이언트 옵션 사용: 켬
- 동영상: 품질 우선
- 해상도 제한: 스트리밍을 실행하는 기기의 해상도
- 프레임 속도 제한: 스트리밍을 실행하는 기기의 주사율
- HDR: 사용
- 하드웨어 디코딩: 켬
- HEVC 동영상: 켬
- AV1 동영상: 끔
- PyroWave 동영상: 켬 (YUV 4:4:4 끔, 자동 비트 전송률 켬, 품질 조정 1)
- 낮은 지연 시간 네트워크: 켬
- 클라이언트의 Steam 설정 > 개발자 > HDR 호환성 테스트: 켬
- StreamHDR 플러그인: 스트리밍 콘텐츠 밝기 200 nits (기본값)

## 알려진 문제

- 이 플러그인은 Steam의 시스템 파일 streaming_client를 조건에 따라 자동으로 수정하거나 복원하는 동작을 합니다. 심각한 오류가 발생할 경우 사용자가 직접 해결하기 어려울 수 있으니 유의해 주십시오.
- 핸드헬드 기기의 내장 디스플레이에서 HDR 피크 휘도 영역에 클리핑이 생길 수 있습니다. SteamOS는 내장 디스플레이에서 HDR 콘텐츠의 최대 휘도를 약 600 nits로 제한하는 것으로 추정되며(밝기 슬라이더 최대 기준), 이 값을 넘는 휘도의 픽셀은 백색으로 표현됩니다. 게임 화면에서 하늘의 태양처럼 아주 밝은 곳이 백색으로 타는 것처럼 보일 경우, 호스트 게임의 최대 밝기를 800 nits 이하로 낮추거나 스트리밍 콘텐츠 밝기를 낮추는 방법으로 문제를 완화할 수 있습니다.
- 호스트의 "스트리밍 디스플레이 HDR" 옵션을 "클라이언트와 일치"로 설정할 경우 스트리밍 시작 직후 인코딩이 SDR로 되돌아가는 문제가 있습니다. 옵션을 반드시 "기본" 또는 "맞춤 설정"으로 두십시오.
- 호스트에서 "NVFBC 캡처" 옵션을 켤 경우 캡처된 데이터가 HDR 색역으로 인코딩되지 않습니다. 이 옵션은 반드시 끄십시오.
- Steam 업데이트로 streaming_client가 변경될 경우 플러그인이 동작하지 않을 수 있습니다. 플러그인을 업데이트할 수 없을 경우, 플러그인을 비활성화하거나 제거하고 Steam을 재시작하면 원래 상태로 복구할 수 있습니다.

---

# 개발 정보

## 개발 환경

Node.js, yarn(1.x), Python 3가 필요하고, 주입 라이브러리를 빌드하려면 Linux에서 `make`와 `gcc`가 필요합니다.

## 테스트 환경

- 클라이언트 기기: Lenovo Legion Go 2 OLED
- 클라이언트 OS: SteamOS 3.10.1, CachyOS(2026년 11월 26~27일 기준: gamescope 3.17.0, 커널 7.3.5, mesa 26.3.1). 모두 게임 모드로 실행
- 호스트: Windows 11, NVIDIA RTX 5090, LG 45GX950A, Samsung G80SD
- 네트워크: 2.5GbE 유선 연결, 5GHz Wi-Fi 연결, MLO를 끈 6GHz Wi-Fi 연결
- 이외의 기기와 OS 환경에서는 플러그인이 동작하지 않거나 동작이 불안정할 수 있습니다.

## 설계 원칙

- **수정하는 시스템 파일은 `streaming_client` 하나뿐입니다.** 원본은 항상 같은 폴더에 `streaming_client.real`로 보관하고, 플러그인을 제거하거나 Steam이 종료될 때 원래대로 되돌립니다.
- **Steam의 파일 검사에 맞춰 설치와 복원 시점을 정합니다.** Steam은 시작할 때마다 `streaming_client`의 크기를 검사하고, 다르면 업데이트로 복원한 뒤 스스로 다시 시작합니다. 이때 플러그인이 곧바로 래퍼를 다시 씌우면 Steam이 같은 절차를 되풀이하는 순환(래퍼 복원 루프)이 생겨 게임 모드가 부팅되지 않을 수 있습니다. 그래서 Steam이 종료되면 원본을 먼저 복원하고, Steam이 시작된 뒤 일정 시간이 지나야 래퍼를 설치합니다.
- **폴링 대신 이벤트로 동작합니다.** 파일 변경은 `inotify`로, 프로세스 종료는 `pidfd`로 감지하고 타이머로 주기 점검을 하지 않습니다. Steam이 실행되지 않는 동안에만 점검 간격을 늘려 가며 다시 확인합니다.
- **모든 기능은 스트리밍 전용입니다.** 래퍼는 `streaming_client`에만 영향을 주고, 색 조정은 스트리밍이 시작될 때 적용했다가 끝나면 제거합니다. 로컬 게임에는 영향을 주지 않습니다.
- **옵션 정의는 한 곳에 둡니다.** 범위, 단계, 기본값, 스트리밍 중 고정 여부를 `py_modules/streamhdr/options.json` 하나에 두고 프런트엔드, 백엔드, 브라우저 목업이 함께 읽습니다.

## 동작 방식

1. **래퍼 설치:** `streaming_client`를 `streaming_client.real`로 보관하고 같은 이름으로 쉘 스크립트(래퍼)를 둡니다. 래퍼는 HDR Streaming 플래그(`enabled`)와 `sdl_hdr_shim.so`가 있을 때만 `LD_PRELOAD`를 걸고, `stream_event` 파일에 `start <pid>`를 기록한 뒤 원본을 `exec`합니다. 래퍼는 HDR Streaming 설정과 상관없이 설치되며, 켜짐 여부는 플래그 파일이 정합니다.
2. **HDR 요청:** 리눅스용 Steam은 X11 위의 SDL에서 디스플레이의 HDR 여부를 물었을 때 항상 "없음"으로 답을 받아 호스트에 SDR을 요청합니다. 주입 라이브러리(`backend/src/sdl_hdr_shim.c`)가 `SDL.display.HDR_enabled` 질의에 `true`를 답해서 Steam이 HDR로 요청하게 만듭니다.
3. **스트리밍 콘텐츠 밝기:** X11의 SDL 렌더러는 SDR 흰색 기준을 80 nits로 잡아 스트림이 어둡게 보입니다. 주입 라이브러리가 렌더러를 만들기 직전에 창 속성 `SDL.window.SDR_white_level`을 `스트리밍 콘텐츠 밝기 ÷ 80`으로 설정합니다. 값은 `paper_white` 파일에서 읽으므로 다음 접속부터 적용됩니다.
4. **설치 시점:** 래퍼는 Steam이 실행 중일 때만 설치합니다. 원본이 깨끗하게 있었다면(플러그인이 로드될 때 원본이었거나 Steam 종료 때 복원했다면) Steam이 시작된 지 5초 뒤에, 래퍼가 남은 채 Steam이 시작됐다면(전원 강제 종료 등) 30초 뒤에 설치합니다.
5. **Steam 종료 시 복원:** `steamrt64/steam` 프로세스가 끝나면 즉시 원본을 복원합니다.
6. **스트리밍 감지:** 래퍼가 쓰는 `stream_event`를 읽어 스트림의 시작을 알고, 그 프로세스의 종료는 `pidfd`로 받습니다. 시작과 종료는 `status` 이벤트로 패널에 전달되어 알림 박스와 옵션 잠금에 쓰입니다.
7. **색 조정:** Contrast, Gamma, Saturation으로 17×17×17 3D LUT(`.cube`)를 만들어 gamescope의 `GAMESCOPE_COLOR_LOOK_PQ` 속성에 `xprop`으로 지정합니다. 설정 조합마다 `look_pq_s###_c###_g###_p###.cube` 파일을 쓰고 나머지는 정리하며, 세 값이 모두 기본값이면 속성을 제거합니다. `xprop`이 필요하며(SteamOS에는 기본 포함) 없으면 Contrast, Gamma, Saturation을 적용하지 못하고 오류 박스를 띄웁니다. HDR 스트리밍 자체와 스트리밍 콘텐츠 밝기는 `xprop`을 쓰지 않습니다.
8. **반복 복원 방지:** Steam이 원본을 10분 안에 3번 복원하면 재설치를 멈추고 오류 박스를 띄웁니다. HDR Streaming을 바꾸거나 플러그인을 다시 로드하면 다시 시도합니다.

## 옵션

| 옵션 | 기본값 | 범위 | 비고 |
|---|---|---|---|
| HDR Streaming | 켬 | 켬 / 끔 | 스트리밍 중 변경 불가, 다음 접속부터 적용 |
| 스트리밍 콘텐츠 밝기 | 200 nits | 80 ~ 480 nits, 10 nits 단위 | 스트리밍 중 변경 불가, 다음 접속부터 적용 |
| Contrast | 100% | 0 ~ 200%, 5 단위 | 스트리밍 중 변경 가능 |
| Gamma | 1.00 | 0.50 ~ 2.00, 0.05 단위 | 스트리밍 중 변경 가능 |
| Saturation | 100% | 0 ~ 200%, 5 단위 | 스트리밍 중 변경 가능 |

Reset All Settings는 모든 옵션을 기본값으로 되돌리며, 스트리밍 중에는 변경할 수 없는 옵션(HDR Streaming, 스트리밍 콘텐츠 밝기)은 그대로 둡니다.

## 밝기 계산

Windows 호스트와 SteamOS 3.10.1에서 테스트한 내용입니다. 스트림의 밝기는 다음 순서로 정해집니다.

1. 호스트 게임이 HDR 콘텐츠의 휘도를 정합니다(게임 설정의 최대 밝기 등).
2. 호스트 Windows의 SDR 콘텐츠 밝기(슬라이더 값 s)가 스트림의 기준 흰색을 `80 + 4 × s` nits로 정합니다. 슬라이더 50이면 280 nits입니다.
3. 클라이언트는 이 기준 흰색을 스트리밍 콘텐츠 밝기로 다시 그립니다. 콘텐츠 휘도가 `스트리밍 콘텐츠 밝기 ÷ 호스트 기준 흰색`배가 되며, 이 비를 PW 보정이라고 부릅니다. 호스트의 SDR 콘텐츠 밝기가 50이고 스트리밍 콘텐츠 밝기가 기본값 200 nits이면 PW 보정은 200 nits ÷ 280 nits ≈ 0.71입니다. 호스트의 SDR 콘텐츠 밝기를 낮추면 PW 보정이 커져 밝아지고, 높이면 어두워집니다.
4. gamescope가 밝기 슬라이더의 게인을 곱해 그립니다.

게임의 최대 밝기와 페이퍼 화이트는 호스트의 콘텐츠만 바꿀 뿐 PW 보정은 바꾸지 않습니다.

### 렌더링 제한값

렌더링 제한값은 실제 디스플레이에 몇 휘도로 표시되는지와는 상관없이, HDR 콘텐츠가 가질 수 있는 최대 휘도값의 제한입니다. 이 값을 넘는 콘텐츠 휘도는 모두 같은 흰색으로 그려져 클리핑이 생깁니다. 렌더링 제한값은 밝기 슬라이더의 게인에 반비례해 `약 1850 nits ÷ 게인`이며, 측정 오차는 약 ±5%입니다.

| 밝기 슬라이더 | 게인 | 렌더링 제한값 |
|---|---|---|
| 100 | 3.0 | 약 617 nits |
| 88 | 2.395 | 약 772 nits |
| 80 | 1.945 | 약 951 nits |
| 76 | 1.753 | 약 1055 nits |

호스트 콘텐츠 휘도에 PW 보정을 곱한 값이 렌더링 제한값을 넘으면 클리핑이 생깁니다. 호스트의 SDR 콘텐츠 밝기 50, 스트리밍 콘텐츠 밝기 200 nits에서 호스트 게임의 최대 밝기가 800 nits이면 콘텐츠 값이 약 571 nits라 슬라이더 100에서 클리핑이 없고, 1000 nits이면 약 714 nits라 클리핑이 생깁니다.

## 파일 구조

```
plugin.json, package.json    플러그인 정보와 빌드 설정 (version의 기준은 package.json)
main.py                      백엔드 진입점 (모듈에 위임)
py_modules/streamhdr/        백엔드
  options.json               옵션 정의의 단일 출처
  options.py                 옵션 읽기와 값 검증
  controller.py              설정, 래퍼, gamescope를 묶어 상태와 옵션 변경을 처리
  wrapper.py                 래퍼 설치, 점검, 복원
  streaming_client.sh.tmpl   래퍼 스크립트 템플릿
  events.py                  inotify와 pidfd 이벤트 (파일 변경, 스트리밍과 Steam의 시작·종료)
  look.py                    대비·감마·채도 LUT 생성
  gamescope.py               gamescope 환경 읽기, xprop 속성 설정과 제거
  paperwhite.py              스트리밍 콘텐츠 밝기 값 파일
  paths.py, settings.py, errors.py
src/                         프런트엔드 (React, Decky UI)
  index.tsx                  패널
  info-page.tsx              Plugin Info 페이지
  status.ts                  백엔드 상태와 이벤트
  locales/                   문구 (en.ts가 기준, ko.ts)
backend/                     주입 라이브러리 소스(src/sdl_hdr_shim.c)와 빌드 설정
preview/                     브라우저 목업 (Steam UI를 흉내 낸 mock_steam.css 사용)
scripts/                     package.sh (릴리스 zip), install-dev.sh (기기 설치)
tests/                       백엔드 단위 테스트
```

플러그인이 기기에 만드는 파일은 다음과 같습니다.

| 경로 | 내용 |
|---|---|
| `~/.local/share/Steam/steamrt64/streaming_client` | 래퍼 스크립트 (원본은 `streaming_client.real`) |
| `~/.local/share/decky-stream-hdr/sdl_hdr_shim.so` | 주입 라이브러리 |
| `~/.local/share/decky-stream-hdr/enabled` | HDR Streaming 플래그 (있으면 켬) |
| `~/.local/share/decky-stream-hdr/paper_white` | 스트리밍 콘텐츠 밝기 값 |
| `~/.local/share/decky-stream-hdr/stream_event` | 래퍼가 기록하는 스트리밍 시작 이벤트 |
| `~/.local/share/decky-stream-hdr/luts/` | 색 조정 LUT 파일 |
| `~/homebrew/settings/decky-stream-hdr/settings.json` | 옵션 값 |

## 개발 명령어

프런트엔드는 다음 명령으로 설치하고 검사, 테스트, 빌드합니다.

```bash
yarn install
yarn typecheck    # 타입 검사
yarn test         # 백엔드 단위 테스트 (unittest)
yarn build        # 프런트엔드 빌드 (dist/)
yarn serve        # 브라우저 목업: http://localhost:5173/ (?lang=english로 영어 확인)
```

목업은 Decky와 Steam UI의 모의 구현이라 간격과 글꼴이 근사치입니다. 최종 모양은 기기에서 확인해야 합니다.

주입 라이브러리는 Linux에서만 빌드할 수 있으므로 릴리스 zip은 Linux 기기에서 만듭니다.

```bash
make -C backend           # backend/out/sdl_hdr_shim.so
sh scripts/package.sh     # release/decky-stream-hdr-<version>.zip
```

개발 중에는 기기에서 저장소를 받아 한 번에 빌드하고 Decky에 설치할 수 있습니다. `sudo` 비밀번호를 묻습니다.

```bash
git pull
sh scripts/install-dev.sh
```

## 번역

문구는 `src/locales/en.ts`(기준 언어)와 `ko.ts`에 있으며, Steam의 언어 설정에 따라 고르고 없는 언어는 영어로 표시합니다. 영어 문구의 Steam 옵션 이름은 Steam 영어판 화면의 이름과 같게 씁니다. 새 언어를 추가하려면 `src/locales/<언어>.ts`를 만들고 `src/locales/index.ts`에 등록하십시오. 정보 페이지의 문구는 이 README의 소개 문단과 "사용 방법"부터 "알려진 문제"까지와 같은 내용으로 유지합니다(설치 방법은 정보 페이지에 없습니다).

## 수동 복구

플러그인을 제거할 수 없거나 Steam 업데이트 표시가 반복되고 게임 모드가 부팅되지 않을 때는 SSH나 TTY로 접속해서 다음을 순서대로 실행하십시오.

```bash
sudo systemctl stop plugin_loader
mv -f ~/.local/share/Steam/steamrt64/streaming_client.real ~/.local/share/Steam/steamrt64/streaming_client
sudo rm -rf ~/homebrew/plugins/decky-stream-hdr ~/.local/share/decky-stream-hdr
sudo reboot
```

두 번째 명령이 "없는 파일"이라고 하면 이미 원본으로 복원된 상태이니 건너뛰십시오.

## 라이선스

[GPL-3.0](LICENSE) 라이선스입니다. 이 프로젝트가 사용하는 서드파티 소프트웨어의 고지는 [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES)에 있습니다.
