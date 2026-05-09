# JSM Linux Build Reproduction Handoff

This handoff extracts the build-enabling knowledge from
`docs/superpowers/2026-04-29-linux-build-record.md`.

It is written for a new Linux environment that may be a different distro from
the original host. It intentionally avoids package-manager commands,
machine-specific environment variables, and host-specific paths. Treat package
names, compiler versions, and session details as distro-local choices.

The working tree you receive may already contain the source patches described
below. Do not apply them blindly. The important thing is to know which local
changes were needed relative to upstream, why they were made, and which build
failures they resolved.

## What Worked

- A Linux build was achieved with the SDL backend enabled.
- SDL3 was built from source through the project's CMake/CPM flow.
- The successful build used clang for both C and C++ compilation.
- The final executable was produced under the CMake build tree at
  `JoyShockMapper/JoyShockMapper`.

Key rule: set both C and C++ compilers explicitly when configuring CMake.
Setting only the C++ compiler is not enough because SDL3 includes substantial C
source. If the C compiler is left as the distro default, SDL3 may compile with
a different compiler than the rest of the tree.

## Distro-Agnostic Dependency Knowledge

The baseline project dependencies are the usual Linux build and runtime
development components for:

- C and C++ compilation with C++23 support.
- CMake and a supported build tool.
- pkg-config.
- GTK 3 and gtkmm 3.
- appindicator3 or the distro's compatible Ayatana appindicator package.
- libevdev.
- libusb 1.0.
- hidapi.
- Linux input test/debug tools if runtime smoke testing is planned.

The original setup notes were not sufficient for SDL3-from-source. SDL3 also
needed development headers/libraries for common Linux platform integrations:

- ALSA, PulseAudio, JACK, sndio, and PipeWire audio.
- X11 core libraries plus Xext, Xrandr, Xcursor, Xfixes, Xi, XScrnSaver, and
  xkbcommon.
- DRM, GBM, OpenGL, GLES, and EGL.
- D-Bus and IBus.
- udev.
- Wayland and libdecor.
- liburing.

The first concrete dependency failure was SDL3 configure failing because
XScrnSaver support could not be found. On a new distro, translate this into
the distro package that provides the XScrnSaver development files.

## Optional Runtime Host Knowledge

The following is not required just to compile JSM, but it matters for later
Linux runtime smoke tests involving keyboard/mouse output through uinput:

- The `uinput` kernel module must be available and loaded.
- `/dev/uinput` must be accessible to the user running JSM.
- The distro's udev rules need to allow the JoyShockMapper virtual devices.
- The user may need membership in the distro's input-access group or equivalent
  permission mechanism.
- Existing login sessions may not pick up new group membership until refreshed.

This runtime setup is separate from compile success.

## Upstream-Delta Source Patches

These were the minimum source changes recorded while getting the Linux build
working. In a copied tree, they may already be present.

### `JoyShockMapper/include/Gamepad.h`

Problem: the header uses `std::chrono::time_point` and
`std::chrono::steady_clock` but did not include `<chrono>`. Windows builds had
apparently been relying on transitive includes. Linux clang did not.

Observed failure:

```text
error: no member named 'chrono' in namespace 'std'
error: unknown type name 'TimePoint'
```

Required upstream delta:

```diff
 #include "JoyShockMapper.h"
 #include "PlatformDefinitions.h"
+
+#include <chrono>
```

This is a real missing-include fix and should be safe upstream.

### `JoyShockMapper/src/TriggerEffectGenerator.cpp`

Problem: this file uses `std::find_if` without including `<algorithm>`.
Linux clang did not get `<algorithm>` transitively.

Observed failure:

```text
error: no member named 'find_if' in namespace 'std'
```

Required upstream delta:

```diff
 #include "TriggerEffectGenerator.h"
+
+#include <algorithm>
```

This is also a real missing-include fix and should be safe upstream.

### `JoyShockMapper/src/linux/Gamepad.cpp`

Problem: the Linux `GamepadImpl::isInitialized` stub had a `bool` return type
with an empty body. That produces undefined behavior if called and generated a
Linux-specific return-type warning.

Recorded local delta:

```diff
 virtual bool isInitialized(std::string* errorMsg = nullptr) {
+    return false;
 }
```

This does not implement Linux virtual gamepad output. It only makes the stub
explicitly report that it is not initialized. In the recorded tree,
`Gamepad::getNew` still returned `nullptr`.

### `JoyShockMapper/src/linux/Whitelister.cpp`

Problem: four Linux whitelister stubs returned `bool` but had empty bodies.
That has the same undefined-behavior risk as the gamepad stub.

Recorded local delta:

```diff
 virtual bool ShowConsole() override
 {
+    return false;
 }
 virtual bool IsAvailable() override
 {
+    return false;
 }

 virtual bool Add(string* optErrMsg = nullptr) override
 {
+    return false;
 }
 virtual bool Remove(string* optErrMsg = nullptr) override
 {
+    return false;
 }
```

This does not implement Linux process whitelisting. In the recorded tree,
`Whitelister::getNew` still returned `nullptr`.

## CMake And Compiler Knowledge

The original documented configure pattern only set the C++ compiler to clang.
That was insufficient because SDL3 C files still used the default C compiler.

On the original host, the default C compiler was gcc 15.2.0. SDL3 3.4.4 then
hit an internal compiler error while compiling Wayland support:

```text
during RTL pass: expand
.../SDL_waylandevents.c: In function 'Wayland_SeatDestroyKeyboard':
internal compiler error: Segmentation fault
```

The fix was to configure CMake with clang as both:

- `CMAKE_C_COMPILER`
- `CMAKE_CXX_COMPILER`

If a build directory was previously configured with a different C compiler,
reconfigure from a clean build tree. Mixed compiler state in SDL3's generated
build files can make later failures misleading.

If Wayland compilation is still a blocker with a chosen compiler, disabling
SDL Wayland support is a reasonable fallback for this lab. JSM uses SDL here
for controller input, not for rendering its own UI, so an X11-capable SDL build
can still be acceptable for build and input feasibility work.

## Known Build Failure Map

### SDL3 configure cannot find XScrnSaver

Meaning: SDL3's Linux development dependencies are incomplete.

Fix direction: install the distro's development package that provides
XScrnSaver headers/pkg-config metadata, and audit the rest of SDL3's Linux
development dependency set.

### SDL3 fails inside Wayland C source with a compiler internal error

Meaning: the C compiler selected for SDL3 may be the issue, not JSM source.

Fix direction:

- Ensure CMake is explicitly using clang for C as well as C++.
- Recreate the build tree after changing compilers.
- If the same class of failure persists, consider disabling SDL Wayland support
  for the lab build.

### JSM source fails on `std::chrono`

Meaning: `Gamepad.h` is missing `<chrono>`.

Fix direction: preserve or apply the `#include <chrono>` upstream delta.

### JSM source fails on `std::find_if`

Meaning: `TriggerEffectGenerator.cpp` is missing `<algorithm>`.

Fix direction: preserve or apply the `#include <algorithm>` upstream delta.

## Non-Blocking Warnings From Successful Build

The recorded successful build still emitted warnings that were not treated as
build blockers:

- `-Winconsistent-missing-override` in `JSMVariable.hpp`.
- `-Wswitch` enum coverage warnings in `main.cpp`, `JoyShock.h`, and
  `Mapping.cpp`.
- `SDLWrapper.cpp` has an incomplete `SDL_GamepadType` switch.

The `SDLWrapper.cpp` warning is potentially functional for controller
classification but did not prevent compilation.

## Runtime-Relevant Discovery That Is Not A Build Fix

Linux `Gamepad.cpp` and `Whitelister.cpp` were placeholders in the recorded
tree:

- Linux virtual gamepad output was not implemented.
- Linux app whitelisting was not implemented.
- Keyboard/mouse output paths are separate and may still work through uinput.

Do not confuse the `return false` stub patches with feature implementation.
They only remove undefined behavior from placeholder methods.

## Controller Classification Note

The recorded build warned that `SDLWrapper.cpp` did not handle several
`SDL_GamepadType` enum values, including standard and Xbox 360 style types.

For the lab controller used in the original session, Nintendo Switch Pro mode
reported a Nintendo VID/PID and was expected to classify cleanly. DInput and
XInput modes reported an 8BitDo VID/PID that was likely not in JSM's lookup
table and could remain `JS_TYPE_UNKNOWN`.

This matters for runtime smoke testing, not for compiling the project.

## Durable Follow-Up Fixes

These are the build-documentation or upstream-cleanup items worth preserving:

- Document SDL3 Linux development dependencies separately from the project's
  own direct dependencies.
- Document that both C and C++ compilers should be set explicitly for Linux
  SDL builds.
- Mention the gcc-15 plus SDL3 3.4.4 Wayland compiler failure as the reason
  for forcing clang for C sources on affected hosts.
- Keep the missing includes in `Gamepad.h` and `TriggerEffectGenerator.cpp`.
- Keep or improve the Linux stub methods so `bool` functions do not have empty
  bodies.
- Consider a separate controller-classification patch for `SDLWrapper.cpp`.
- The top-level CMake project label still said `JoyShockMapper_SDL2` despite
  SDL3 migration. That is cosmetic only.

## Fresh-Context Checklist

When continuing from a copied directory:

- Inspect whether the four upstream-delta source patches above are already
  present.
- Confirm the Linux distro has the equivalent development packages for the
  baseline project dependencies and SDL3's Linux platform dependencies.
- Configure from a clean build tree if compiler selection has changed.
- Ensure both C and C++ compiler selections are intentional.
- Treat missing SDL3 platform libraries and compiler selection as environment
  problems before changing JSM mapping/runtime semantics.
- Treat `Gamepad.cpp` and `Whitelister.cpp` as stubs unless a later patch has
  implemented real Linux behavior.
