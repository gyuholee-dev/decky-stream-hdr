import type { LocaleStrings } from "./types";

// 한국어. 플러그인 이름과 옵션 이름(StreamHDR, HDR Streaming, Saturation, Plugin Info, GitHub)은
// 영어 그대로 두고, 설명문과 메시지만 번역한다. 읽는 사람은 일반 사용자이므로 개발 용어는 쓰지 않는다.
// 여기에 없는 문구는 영어로 표시된다.
export const ko: LocaleStrings = {
  hdrToggleDescription: "스팀 스트리밍 시 인코딩 및 렌더링에 HDR을 적용합니다. 호스트 및 클라이언트 설정은 Info를 확인하세요.",
  paperWhiteDescription: "HDR 렌더링 시 기준 밝기를 조정합니다. 출력 디스플레이 피크 밝기가 1000일 경우 230 nits로 설정하길 권장합니다.",
  contrastDescription: "HDR 출력의 대비를 조정합니다. OLED 디스플레이일 경우 기본값을 권장합니다.",
  gammaDescription: "HDR 출력의 감마를 조정합니다. OLED 디스플레이일 경우 0.85~1.00으로 설정하길 권장합니다.",
  saturationDescription: "HDR 출력의 채도를 조정합니다. OLED 디스플레이일 경우 125~135% 로 설정하길 권장합니다.",
  resetTitle: "Reset All Settings",
  resetDescription: "모든 설정을 기본 설정값으로 되돌리시겠습니까?",
  resetConfirmButton: "확인",
  cancelButton: "취소",
  info: {
    aboutHeading: "소개",
    about:
      "StreamHDR은 Steam Remote Play에 BT.2020 PQ HDR 스트리밍을 지원하는 Decky 플러그인입니다. " +
      "스팀OS 및 포크와 스팀 게임모드가 설치된 리눅스 기기가 HDR 스트리밍이 가능한 사양일 경우, 이 플러그인을 통해 스팀의 스트리밍 과정에 개입하여 호스트에 대한 HDR 인코딩 요청을 수정하고 클라이언트의 HDR 렌더링 출력을 가능하게 설정할 수 있습니다.",
    usageHeading: "사용 방법",
    usage: [
      "플러그인 메뉴에서 HDR Streaming을 켠 뒤 Remote Play를 실행하십시오. 이미 실행 중이라면 스트리밍을 종료한 뒤 다시 실행해야 적용됩니다.",
      "Paper White는 HDR 스트리밍이 어느 정도의 밝기로 출력될지 결정하는 기준값입니다. 이 값을 변경하고자 할 경우 스트리밍을 종료해 주십시오.",
      "Contrast, Gamma, Saturation은 HDR 출력 이미지를 사용자의 선호에 맞게 조정할 수 있는 설정입니다. 이 값들은 스트리밍 중에도 자유롭게 변경할 수 있습니다.",
      "플러그인의 모든 설정은 Remote Play에만 적용되며, 스트리밍을 실행하는 기기에 직접 설치하여 실행하는 게임에는 영향이 없습니다.",
    ],
    requirementsHeading: "HDR 스트리밍 요구사양",
    requirements: [
      "호스트 (게임을 실행하는 PC): HDR 지원 게임 및 HDR 모니터와, HDR 게임을 직접 원활하게 실행 가능한 사양의 PC가 필요합니다. " +
        "확인된 환경은 Windows 11, RTX 50, 삼성 OLED 모니터입니다.",
      "클라이언트(스트리밍을 실행하는 기기): HDR 디스플레이가 내장되거나 또는 외장으로 연결된 기기에서 스팀OS를 게임 모드로 실행해야 합니다. " +
        "확인된 환경은 Lenovo Legion Go 2 OLED와 CachyOS Handheld입니다.",
      "네트워크: 고대역폭 저지연 네트워크 환경을 권장합니다. 거치 기기일 경우 1GbE 이상 속도의 유선 연결을 권장하며, 핸드헬드 기기일 경우 Wi-Fi 절전을 끄는 걸 권장합니다. 공유기에서 MLO(Multi-Link Operation)를 켜 두면 MLO를 지원하지 않는 기기(Wi-Fi 6E 등)의 6GHz 연결에서 지연이 커지고 패킷 손실이 생겨 원활한 게임플레이가 어려울 수 있으니, MLO를 끄거나 5GHz Wi-Fi에 연결하십시오. 확인된 환경은 2.5GbE 유선 연결, 5GHz Wi-Fi 연결, MLO를 끈 6GHz Wi-Fi 연결입니다.",
      "스팀에 2026년 10월부터 추가된 PyroWave 동영상 옵션을 필수로 사용해야 합니다. (NVFBC 캡처는 반드시 꺼 주십시오) PyroWave는 Steam의 일반 대역폭 제한이 적용되지 않고 전송량이 1Gbps 이상으로 매우 큽니다(YUV 4:4:4 켬, 품질 조정 2에서 1080p 기준 최대 1.1Gbps, 6GHz Wi-Fi 연결에서 확인). 스트리밍 플레이 중 프레임레이트 저하나 스터터링이 나타날 경우 YUV 4:4:4를 끄고 품질 조정을 1 이하로 낮추십시오 (1080p 기준 약 620~730Mbps).",
    ],
    hostHeading: "호스트 설정",
    host: [
      "호스트의 Steam 설정 > Remote Play > 고급 호스트 설정",
      "고급 호스트 옵션 사용: 켬",
      "스트리밍 시 기본 디스플레이: HDR 디스플레이",
      "스트리밍 디스플레이 HDR: 기본 또는 맞춤 설정 (HDR 사용: 켬)",
      "NVIDIA GPU에서 NVFBC 캡처 사용: 끔",
      "하드웨어 인코딩 사용: 켬",
      "네트워크 트래픽 우선순위 조정: 켬",
    ],
    clientHeading: "클라이언트 설정",
    client: [
      "클라이언트의 Steam 설정 > Remote Play > 고급 클라이언트 설정",
      "고급 클라이언트 옵션 사용: 켬",
      "동영상: 품질 우선",
      "해상도 제한: 스트리밍을 실행하는 기기의 해상도",
      "프레임 속도 제한: 스트리밍을 실행하는 기기의 주사율",
      "HDR: 사용",
      "하드웨어 디코딩: 켬",
      "HEVC 동영상: 켬",
      "AV1 동영상: 끔",
      "PyroWave 동영상: 켬 (YUV 4:4:4 끔, 자동 비트 전송률 켬, 품질 조정 1)",
      "낮은 지연 시간 네트워크: 켬",
      "클라이언트의 Steam 설정 > 개발자 > HDR 호환성 테스트: 켬",
    ],
    detailsHeading: "상세 정보",
    version: "버전",
    author: "제작자",
    license: "라이선스",
    repository: "저장소",
  },
  streamingNotice: "스팀이 스트리밍 중입니다. 스트리밍 중에는 HDR 및 페이퍼 화이트 설정을 변경할 수 없습니다.",
  statusLoading: "로드하는 중...",
  statusUnavailable: "플러그인에 연결할 수 없습니다. 플러그인을 다시 로드해 주십시오.",
  unknownError: "알 수 없는 오류가 발생했습니다. 오류 코드: {code}",
  errors: {
    client_not_found: "streaming_client를 찾지 못했습니다. Steam이 기본 경로에 설치되어 있는지 확인해 주십시오.",
    shim_missing: "플러그인 파일이 손상되거나 누락되었습니다. 플러그인을 다시 설치해 주십시오.",
    original_missing: "streaming_client.real을 찾을 수 없습니다. 스팀을 재시작하고 플러그인을 다시 로드해 주십시오.",
    unknown_format: "streaming_client가 요구 형식과 불일치하여 플러그인이 올바르게 작동하지 않습니다.",
    file_operation_failed: "파일 처리에 실패했습니다: {detail}",
    env_missing: "gamescope 정보를 찾을 수 없습니다. Steam이 게임 모드로 실행 중인지 확인해 주십시오.",
    xprop_missing: "xprop이 설치되어 있지 않아 HDR 출력 설정을 적용할 수 없습니다.",
    xprop_timeout: "HDR 출력 설정 적용이 응답시간 초과로 실패하였습니다.",
    xprop_failed: "HDR 출력 설정 적용을 실패하였습니다: {detail}",
    wrapper_unstable: "Steam이 스트리밍 클라이언트를 계속 복원하고 있어 자동 설치를 중단했습니다. HDR Streaming을 껐다 켜거나 플러그인을 다시 로드해 주십시오.",
    lut_failed: "LUT 파일 생성에 실패하였습니다: {detail}",
  },
};
