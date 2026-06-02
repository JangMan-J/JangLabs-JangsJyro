# Repository Guidelines

## Project Structure & Module Organization

The root `CMakeLists.txt` selects the backend and delegates the real build to `JoyShockMapper/CMakeLists.txt`. Main C++ code lives in `JoyShockMapper/src/`, with headers in `JoyShockMapper/include/`. Platform-specific implementations are under `JoyShockMapper/src/win32`, `JoyShockMapper/src/linux`, and matching include subfolders. Runtime config templates and packaging assets are in `dist/`; diagrams and reference docs are in `JoyShockMapper/doc/`. `JSM_GUI/jsm-gui-app/` is a separate GUI subtree and is not built by the root CMake project. `gamepad/` is the gamepad-input research lab (8BitDo Ultimate 2 / gyro / Steam-Input-vs-JSM behavioral lab); it is not part of the build and carries its own conventions in `gamepad/CLAUDE.md`.

## Build, Test, and Development Commands

```powershell
cmake -B build -S . -G "Visual Studio 17 2022" -A x64
cmake --build build --config Release
```

Builds the default SDL3 backend. Use CMake 3.28+ and VS 2022 on Windows.

```powershell
cmake -B build-jsl -S . -G "Visual Studio 17 2022" -A x64 -DSDL=OFF
cmake --build build-jsl --config Release
```

Builds the legacy JoyShockLibrary backend. Run locally with `build/JoyShockMapper/Release/JoyShockMapper.exe dist`.

## Coding Style & Naming Conventions

C++ uses C++23. Follow `JoyShockMapper/.clang-format`: Allman braces, tab indentation width 4, `PointerAlignment: Middle`, CRLF, and no column limit. Formatting is not uniformly enforced, so match the surrounding file and keep upstream-facing diffs small. Prefer existing module names and patterns such as `*Wrapper`, `*Manager`, and platform overrides in `win32/` or `linux/`.

## Testing Guidelines

There is no active C++ unit test suite in the main tree. For shared code, build both SDL3 and JSL backends when practical. For controller, gyro, or HID changes, verify manually on relevant hardware and record the device, connection mode, inputs tested, and backend used in the PR notes.

## Commit & Pull Request Guidelines

Recent history uses short imperative, sentence-case commit subjects, for example `Fix Switch pro controller mapping` and `Honor timer resolution when using Windows 11`. Keep one logical change per commit. PRs should include a summary, affected backend/platform, manual test results, linked issue or upstream context, and screenshots only for visible GUI or documentation changes.

## Security, Configuration, and Agent Notes

Do not include local-only workspace files such as `.mcp.json`, `.claude/`, `handoffs/`, or machine-specific configs in upstream PRs. Before reverse-engineering controller behavior, check the existing findings in this repo's `gamepad/findings/` (e.g. `gyro_hid.md`, `jsm_linux_port.md`, `steam_input_linux.md`) and prefer primary sources such as SDL HIDAPI code. Always use the OpenAI developer documentation MCP server when working with the OpenAI API, ChatGPT Apps SDK, Codex, or related OpenAI developer products.
