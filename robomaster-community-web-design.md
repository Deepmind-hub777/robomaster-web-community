# RoboMaster Community Web App — Design Proposal

**Status:** For user review; no implementation started  
**Product:** Community-built, cross-platform web app for RoboMaster EP Core first, with EP and S1 planned  
**Audience:** Classroom teachers and students using Android phones/tablets, Windows laptops, iPhone, and iPad

## Product direction

Treat this as a robotics control tool first and a classroom learning product later. The first release is only **connect, view video, safe drive, and stop**. Defer Learn, Code, lesson assignment, and class roster until the local bridge and media/control path pass a technical spike.

The UI concept remains a two-role product, but the first spike should not depend on designing either full experience:

1. **Teacher setup/bridge utility:** install and launch the local bridge, discover robots, verify network/video/control health, and show actionable diagnostics.
2. **Student control client:** select a robot, see its live camera and essential state, drive at a capped classroom speed, and stop immediately.

“No app install for students” does not mean “no installation.” The teacher’s Windows host must run a bridge. Make that a first-class product flow: a simple signed installer when release signing is available, a clear first-run network/firewall explanation, one-click start/stop, optional start-on-login, visible version/update status, and a diagnostic page that can produce a support bundle. Validate the simplest packaging path during the spike before committing to an installer technology.

## First-release screens (after spike passes)

### Connect

- Show bridge status separately from robot readiness.
- Discover/select a robot and show model, Wi-Fi/network, battery, and last response.
- Explain permission, firewall, and connection failures in place.

### Drive

- Live camera, capped speed selection, direction controls, and a persistent stop action.
- Indicate which user currently has control; only one controller may command a robot at a time.
- Student stop ends that controller’s motion; teacher stop is a separate higher-priority action in a later classroom console.

## Responsive behavior

| Form factor | Layout |
|---|---|
| Phone, 360–767 px | Single-column flow. Camera first on Drive; large, reachable controls below or overlaid only when they do not cover key video details. Bottom navigation respects safe areas. |
| Tablet, 768–1199 px | Two-pane workspace: camera and active task in the larger pane, controls/status in the adjacent pane. Teacher roster can collapse to a drawer. |
| Laptop, 1200 px+ | Teacher class overview can show teams, robot health, and lesson controls together. Student Drive keeps video dominant with controls and status alongside it. |

All layouts remain usable in portrait and landscape. Do not require hover, fixed desktop widths, or horizontal scrolling. Keep zoom enabled.

## Visual language

- **Character:** clear, technical, welcoming, classroom-ready; avoid military/tactical styling and excessive game chrome.
- **Color:** light neutral surfaces; deep ink text; education teal for primary actions; course amber for attention/safety actions; green/amber/red status colors paired with text and icons.
- **Typography:** legible sans serif with a 16 px body baseline and clear numeric readouts for battery, speed, and sensor values.
- **Components:** consistent SVG icon family; restrained card borders; status chips with labels; obvious focus rings; no emoji as functional icons.
- **Motion:** short feedback for connection, selection, and lesson progress. Honor reduced-motion preferences; never use animation as the only way to communicate a robot state.

The UI UX Pro Max search returned **Minimalism & Swiss Style**, an education-teal palette (`#0D9488` primary, `#D97706` accent, `#F0FDFA` background), and Fira Sans/Fira Code typography. Its first generated layout pattern was a generic Hero + Features + CTA landing page; the narrowed retry returned the same pattern. That pattern is a poor fit for a live control surface and is intentionally rejected. Use the palette and restrained style as a starting point only; verify text/button contrast and touch targets before freezing tokens. The UX search supported visible keyboard focus and at least 8 px spacing between touch targets. No implementation stack is selected, so no stack-specific search was run.

## Interaction and safety

- Show the selected robot, current mode, and connection state in the same persistent area as the driving controls.
- Use a prominent, always-reachable stop control during robot movement. The running bridge owns a command lease/watchdog: it requires periodic control heartbeats and sends a zero-motion command when the lease expires or the browser disconnects. UI release/focus events are helpful fast paths, not the safety mechanism. A crashed bridge cannot send a stop command, so robot-link loss behavior must be measured separately; if the robot does not stop promptly, the bridge alone is not a sufficient safety design.
- Make speed changes explicit and visible; provide a low-speed classroom default.
- Distinguish “connected to the classroom bridge” from “robot ready to drive.” Explain failures in place and provide a retry path.
- Require an explicit robot selection before taking control. MVP has one student controller per robot; teacher takeover and class-wide stop are deferred. Define controller lease acquisition, expiry, and handoff before adding multiple roles.
- Provide visible loading, reconnecting, disconnected, and command-failed states; do not imply a command succeeded until the bridge confirms it.
- Target 44 × 44 px minimum touch areas with breathing room. Support keyboard operation and screen readers for non-driving flows.

## Technical design boundary

Build the bridge against DJI’s official RoboMaster Python SDK and documented EP protocol surface. The official SDK repository is Apache-2.0 licensed; the developer guide describes the Python SDK for EP and Tello Edu and its motion, status, data-push, and video APIs. Do not transplant code or protocol discoveries from the reverse-engineered APK. Preserve the SDK’s license and verify the applicable DJI product terms before distributing a client. Do not assume the SDK covers S1; establish S1 support separately.

DJI documents the robot video output as H.264. A browser-facing WebRTC path does **not automatically require a full decode/re-encode**: WebRTC-compatible browsers are required to support H.264 Constrained Baseline. The spike must inspect the robot stream’s actual profile/framing and attempt low-latency H.264 packetization/relay first. Transcode only if the stream cannot be made compatible. MJPEG is a fallback to compare, not the default; decoding and JPEG encoding can add CPU use and bandwidth.

The spike must verify WSS/local-network access and measure media/control latency together. Also measure bridge setup friction: install/start time, firewall prompts, and recovery after laptop sleep or bridge restart. The bridge cannot be treated as a hidden implementation detail because it is required for every classroom.

## Go/no-go technical spike

Use one EP Core, the intended classroom router, and representative devices: Windows laptop, Android Chrome, and iOS Safari/iPadOS Safari. Record repeated runs in the actual classroom network, including a weak-signal case.

1. **Local browser path:** verify local-network permission, certificate trust, WSS signaling, WebRTC ICE/media establishment, and recovery after restart on each target browser. Record cold-start success out of 10 attempts per browser/device.
2. **Video glass-to-glass, separately by video path:** compare (A) H.264 pass-through/packetization to WebRTC without decode/re-encode and (B) a decode/transcode path to a browser-compatible WebRTC stream. Record at least 100 visible clock/LED events per path and condition using a high-frame-rate camera filming the robot event and browser display together. Report p50/p95/max latency, dropped/frozen frames, and bridge CPU use. Pilot target: p95 ≤ 250 ms for each path.
3. **Control response and stop:** capture at least 100 browser-input-to-physical-motion-onset trials per condition; report p50/p95/max, with a proposed pilot target of p95 ≤ 150 ms. Exercise manual stop, release-to-stop, browser close, Wi-Fi loss, bridge crash, and laptop sleep while the robot moves on the low-speed default with a recorded representative load. Run each fault type at least 30 times; every injected trial must trigger stop (100% observed success). Record the maximum total time from fault onset to the robot being physically stationary, with the proposed ceiling ≤ 1000 ms. Split it into fault detection/lease window (target range 300–500 ms; test 100 ms heartbeat with 3–5 missed beats) and braking-to-stationary (≤ 500 ms). Also record maximum coast distance from fault onset to stationary; proposed low-speed ceiling ≤ 30 cm. Recalibrate when the speed profile changes. Do not substitute command acknowledgement for physical stop time. If any fault does not stop the robot or exceeds either ceiling, add an independent fail-safe before classroom use.

The 250 ms video, 150 ms control, 1000 ms stop, and 30 cm coast-distance values are proposed classroom pilot thresholds, not published DJI or ISO guarantees. Safety is evaluated as 100% observed stop triggers for every tested fault mode plus maximum total stop time and maximum coast distance; do not summarize safety as a p95. Verify the watchdog does not nuisance-stop during normal classroom Wi-Fi jitter. If local browser permissions, ICE/media, or latency misses, test one simpler network topology and one alternate video transport before committing to full UI work. If the failure remains, reconsider the web-first assumption or require a dedicated teacher host/app.

## First release design scope

1. Teacher bridge setup, launch, health, and diagnostics.
2. EP Core discovery and connection.
3. Live video with low-latency display.
4. Safe low-speed driving with release-to-stop, disconnect handling, and emergency stop.
5. Responsive layouts for phone, tablet, and laptop, with accessible connection and error states.

EP and S1 are later model profiles. Do not imply feature parity until each robot’s supported capabilities have been verified.

## Decisions after the spike

Choose the student entry flow, portrait/landscape control layouts, and first coding environment only after the spike proves the browser/bridge/video/control path. They are not current go/no-go decisions.

## Workflow note

The UI UX Pro Max package was read from the user’s distribution repository and its design-system and UX searches were run from a temporary workspace copy. The repo’s README reports a mechanically patched copy of upstream UI UX Pro Max with attribution and MIT license retained. Search results are recorded above; the mismatched landing-page pattern is rejected rather than treated as a product fit.
