import type { LocaleStrings } from "./types";

// 한국어. 플러그인 이름과 옵션 이름(StreamHDR, HDR Streaming, Saturation, Plugin Info, GitHub)은
// 영어 그대로 두고, 설명문과 메시지만 번역한다. 읽는 사람은 일반 사용자이므로 개발 용어는 쓰지 않는다.
// 여기에 없는 문구는 영어로 표시된다.
export const ko: LocaleStrings = {
  hdrToggleDescription: "스팀 스트리밍 시 인코딩 및 렌더링에 HDR 을 적용합니다. 호스트 및 클라이언트 설정은 Info 를 확인하세요.",
  paperWhiteDescription: "HDR 렌더링 시 기준 밝기를 조정합니다. 출력 디스플레이 피크 밝기가 1000 일 경우 230 nits 로 설정하길 권장합니다.",
  contrastDescription: "HDR 출력의 대비를 조정합니다. OLED 디스플레이일 경우 기본값을 권장합니다.",
  gammaDescription: "HDR 출력의 감마를 조정합니다. OLED 디스플레이일 경우 0.85~1.00 으로 설정하길 권장합니다.",
  saturationDescription: "HDR 출력의 채도를 조정합니다. OLED 디스플레이일 경우 125~135% 로 설정하길 권장합니다.",
  resetTitle: "Reset All Settings",
  resetDescription: "모든 설정을 기본 설정값으로 되돌리시겠습니까?",
  resetConfirmButton: "확인",
  cancelButton: "취소",
  info: {
    aboutHeading: "소개",
    about:
      "StreamHDR은 Steam Remote Play로 게임을 스트리밍할 때 이 기기에서 진짜 HDR 화면을 볼 수 있게 해 줍니다. " +
      "리눅스용 Steam은 이 기기의 화면이 HDR을 지원한다는 것을 알아차리지 못해서, " +
      "게임을 실행하는 PC(호스트)와 게임이 HDR을 지원해도 항상 일반(SDR) 화면을 받아 옵니다. " +
      "이 플러그인은 Steam이 HDR 화면을 보내 달라고 요청하게 만들며, 그 밖의 동작은 바꾸지 않습니다.",
    usageHeading: "사용 방법",
    usage: [
      "HDR Streaming을 켠 뒤 Remote Play로 호스트 PC에 연결하세요. 이미 연결되어 있다면 다시 연결해야 적용됩니다.",
      "게임 안에서 HDR 옵션을 끄면 화면이 일반(SDR) 화질로 바뀌고, 다시 켜면 HDR로 돌아옵니다. " +
        "HDR을 지원하지 않는 게임은 이 옵션을 켜 두어도 화면이 달라지지 않습니다.",
      "Saturation은 HDR 화면의 색이 일반 화면보다 조금 연하게 느껴질 때 쓰는 옵션입니다. 0~200% 범위에서 조절하며, " +
        "100%는 색을 바꾸지 않습니다. 150%를 권장하며, 값이 너무 높으면 진한 색의 세부 표현이 뭉개질 수 있습니다.",
      "Saturation은 스트리밍을 시작하면 적용되고, 끝나면 자동으로 원래대로 돌아옵니다. " +
        "두 옵션 모두 Remote Play 스트리밍에만 적용되며, 이 기기에서 직접 실행하는 게임은 달라지지 않습니다.",
    ],
    requirementsHeading: "요구사양",
    requirements: [
      "호스트 PC(게임을 실행하는 PC): Windows에서 HDR이 켜져 있어야 하고, HDR을 지원하는 모니터와 게임이 필요합니다. " +
        "확인된 환경은 Windows 11과 NVIDIA RTX 5090입니다.",
      "클라이언트(이 기기): Decky가 설치된 리눅스 기기에서 Steam을 게임 모드로 실행해야 하며, 화면이 HDR을 지원해야 합니다. " +
        "확인된 환경은 Lenovo Legion Go 2 OLED의 CachyOS Handheld입니다.",
      "Saturation을 쓰려면 이 기기에 xprop 프로그램이 설치되어 있어야 합니다. 설치되어 있지 않으면 오류 메시지로 알려 드립니다.",
      "호스트 PC와 이 기기의 Steam은 스테이블 버전과 베타 버전 모두에서 같은 결과를 확인했습니다.",
    ],
    hostHeading: "호스트 설정",
    host: [
      "설정 위치: 호스트 PC의 Steam 설정 > Remote Play > 고급 호스트 설정",
      "'고급 호스트 옵션 사용': 켬",
      "'호스트에서 오디오 플레이': 끔",
      "'스트리밍 시 기본 디스플레이': 기본",
      "'스트리밍 디스플레이 해상도': 기본",
      "'스트리밍 디스플레이 새로 고침 빈도': 기본",
      "'스트리밍 디스플레이 HDR': 기본",
      "'NVIDIA GPU에서 NVFBC 캡처 사용': 끔",
      "'하드웨어 인코딩 사용': 켬",
      "'소프트웨어 인코딩 스레드 수': 자동",
      "'네트워크 트래픽 우선순위 조정': 켬",
      "Windows 설정의 HDR: 켬, 게임 안의 HDR 옵션: 켬",
    ],
    clientHeading: "클라이언트 설정",
    client: [
      "설정 위치: 이 기기의 Steam 설정 > Remote Play > 고급 클라이언트 설정",
      "'고급 클라이언트 옵션 사용': 켬",
      "'창 모드': 끔",
      "'표시 형식': 레터박스",
      "'동영상': 품질 우선",
      "'오디오': 스테레오",
      "'마이크': 끔",
      "'성능 오버레이': 사용 안 함",
      "'대역폭 제한': 무제한",
      "'해상도 제한': 1920 x 1080(1080p)",
      "'프레임 속도 제한': 144FPS",
      "'HDR': 사용",
      "'하드웨어 디코딩': 켬",
      "'HEVC 동영상': 켬",
      "'AV1 동영상': 끔",
      "'PyroWave 동영상': 켬 ('YUV 4:4:4' 끔, '자동 비트 전송률' 켬, '품질 조정' 1)",
      "'낮은 지연 시간 네트워크': 켬",
      "Steam 설정 > 개발자의 'HDR 호환성 테스트': 켬",
      "게임 모드의 디스플레이 설정에서 'HDR 사용': 켬",
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
    client_not_found: "streaming_client 를 찾지 못했습니다. Steam이 기본 경로에 설치되어 있는지 확인해 주십시오.",
    shim_missing: "플러그인 파일이 손상되거나 누락되었습니다. 플러그인을 다시 설치해 주십시오.",
    original_missing: "streaming_client.real 을 찾을 수 없습니다. 스팀을 재시작하고 플러그인을 다시 로드해 주십시오.",
    unknown_format: "streaming_client 가 요구 형식과 불일치하여 플러그인이 올바르게 작동하지 않습니다.",
    file_operation_failed: "파일 처리에 실패했습니다: {detail}",
    env_missing: "gamescope 정보를 찾을 수 없습니다. Steam이 게임 모드로 실행 중인지 확인해 주십시오.",
    xprop_missing: "xprop 이 설치되어 있지 않아 HDR 출력 설정을 적용할 수 없습니다.",
    xprop_timeout: "HDR 출력 설정 적용이 응답시간 초과로 실패하였습니다.",
    xprop_failed: "HDR 출력 설정 적용을 실패하였습니다: {detail}",
    lut_failed: "LUT 파일 생성에 실패하였습니다: {detail}",
  },
};
