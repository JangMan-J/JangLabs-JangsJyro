# Linux Environment Setup For JSM/Steam Input Lab

## Recommendation

Do not use WSL2 for the real Steam Input/JSM runtime lane. Use WSL2 only for build-only discovery.

Best options, in order:

1. Native Linux on a spare SSD or dual boot.
2. VMware Workstation Pro on Windows with an Ubuntu Desktop VM and USB passthrough.
3. VirtualBox as a fallback if VMware is not practical.
4. Avoid WSL2, Hyper-V, and cloud VMs for real controller/Steam Input runtime validation.

The project needs real Linux desktop behavior, Steam, SDL controller detection, `/dev/input`, `/dev/uinput`, `hidraw`, udev rules, focus/window behavior, and direct access to the controller or its dongle. WSL2 is useful for compiling code, but it is not a good authority for Steam Input or controller behavior because its GUI and USB paths are mediated by Windows.

## Best Practical Choice

Use VMware Workstation Pro with Ubuntu 24.04 LTS Desktop.

VMware Workstation Pro is the preferred Windows-hosted VM option because it has mature USB passthrough and desktop graphics support. Broadcom states that VMware Desktop Hypervisor products, including Workstation Pro, are free for commercial, educational, and personal users starting with Workstation Pro 17.5.2 and Fusion Pro 13.5.2.

Create snapshots at these points:

- Clean Ubuntu install.
- Dependencies installed.
- Steam installed and controller visible.
- JSM build succeeds.

## VM Settings

Use:

- Ubuntu 24.04 LTS Desktop.
- Xorg session if possible.
- 4 vCPU minimum.
- 8 GB RAM minimum, 16 GB preferred.
- 80 GB disk minimum.
- 3D acceleration enabled.
- USB 3.x controller enabled.
- Bridged or NAT networking.
- USB passthrough for the 8BitDo dongle or wired controller.

Prefer passing through the 8BitDo 2.4 GHz dongle or the controller in wired mode. Do not rely on host Bluetooth sharing for the first lab environment.

## Ubuntu Packages

Install baseline build and observation tools:

```sh
sudo apt update
sudo apt install -y git clang cmake ninja-build pkg-config build-essential \
  libgtk-3-dev libgtkmm-3.0-dev libevdev-dev libusb-1.0-0-dev libhidapi-dev \
  evtest joystick jstest-gtk
```

Try the repo's expected appindicator package first:

```sh
sudo apt install -y libappindicator3-dev
```

If Ubuntu only provides Ayatana appindicator packages, treat that as a small non-semantic Linux build-fix task. Do not silently alter mapper behavior to get past this.

## JSM Runtime Device Access

Enable uinput and install the JSM udev rules:

```sh
sudo modprobe uinput
echo uinput | sudo tee /etc/modules-load.d/uinput.conf
sudo usermod -aG input "$USER"
sudo cp dist/linux/50-joyshockmapper.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
reboot
```

After reboot, check:

```sh
ls -l /dev/uinput
ls -ld /dev/input
ls /dev/hidraw* 2>/dev/null || true
id
```

The user running JSM must have read/write access to the relevant input devices.

## Steam

Install Steam from Valve's normal Debian package rather than Snap or Flatpak. Sandboxed packaging can distort device access and would make early behavior evidence less trustworthy.

```sh
wget https://cdn.akamai.steamstatic.com/client/installer/steam.deb
sudo apt install ./steam.deb
```

Then:

- Launch Steam once interactively.
- Sign in.
- Verify the controller appears in Steam.
- Verify Steam Input can be enabled for the controller.
- Record Steam version and controller connection mode in any run artifact.

## Controller Check

Before running the Phase 1a/1b plan, confirm the controller is visible in Linux:

```sh
lsusb
ls /dev/input/by-id/ 2>/dev/null || true
ls /dev/hidraw* 2>/dev/null || true
jstest-gtk
```

For output observation, install and use `evtest` or an equivalent input-event observer. The first JSM smoke behavior expects:

- `S = SPACE`: pressing/releasing JSM input `S` should produce one `KEY_SPACE` down/up pair from the JSM virtual keyboard.
- `ZR = LMOUSE`: pressing/releasing JSM input `ZR` should produce one `BTN_LEFT` down/up pair from the JSM virtual mouse.

Do not claim this behavior passed unless the input was actually driven and output events were observed.

## WSL2 Position

WSL2 can be used to answer narrow build questions, but it should not be the main lab runtime.

Reasons:

- WSL GUI support is app-focused, not a normal full Linux desktop session for this use case.
- USB access requires explicit USB/IP attachment from Windows.
- `/dev/input`, `/dev/uinput`, `hidraw`, focus, tray, Steam runtime behavior, and controller routing can differ materially from a real Linux desktop.
- Any data from WSL should be labeled build-only unless explicitly proven otherwise.

## Virtualization Options

### Native Linux

Highest confidence. Use this if VMware controller passthrough, Steam Input, or timing behavior becomes questionable.

Pros:

- Most faithful Linux runtime.
- Best chance of reliable controller, uinput, hidraw, and Steam behavior.
- Fewer host/guest timing artifacts.

Cons:

- Requires rebooting or separate hardware.
- Less convenient for Windows-side comparison.

### VMware Workstation Pro

Best Windows-hosted VM choice.

Pros:

- Mature USB passthrough.
- Good desktop graphics support.
- Snapshot workflow is convenient for agents.
- Broadcom currently makes Workstation Pro free for personal, educational, and commercial users on supported versions.

Cons:

- USB passthrough can still have device-specific quirks.
- Host Hyper-V/Windows Hypervisor features can interfere with VMware on some systems.
- Still less authoritative than native Linux if timing or device HID behavior is under investigation.

### VirtualBox

Acceptable fallback.

Pros:

- Free and easy to install.
- Supports USB passthrough with USB controllers and filters.

Cons:

- USB/device capture tends to be more fragile.
- 3D acceleration and desktop behavior may be weaker than VMware.
- May require Extension Pack setup depending on version and USB mode.

### Hyper-V

Not recommended for this lab.

The core problem is not general Linux VM support; it is direct, repeatable controller HID/uinput behavior plus Steam Input. Hyper-V is not the best fit for that.

## First Run Target

Once the Linux environment is ready, run:

```sh
cmake -B build-linux -S . -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=clang++
cmake --build build-linux
```

Expected binary:

```text
build-linux/JoyShockMapper/JoyShockMapper
```

Then follow:

```text
docs/superpowers/plans/2026-04-29-jsm-linux-feasibility.md
```

## Sources

- Microsoft WSL GUI apps documentation: https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps
- Microsoft USB devices in WSL/USBIPD guidance: https://devblogs.microsoft.com/commandline/connecting-usb-devices-to-wsl/
- Broadcom VMware desktop hypervisor licensing note: https://knowledge.broadcom.com/external/article/368667/download-and-license-vmware-desktop-hype.html
- VMware Workstation Pro user guide PDF, including USB controller notes: https://techdocs2-prod.adobecqms.net/content/dam/broadcom/techdocs/us/en/pdf/vmware/desktop-hypervisors/workstation/vmware-workstation-pro-17-0.pdf
- Oracle VirtualBox USB support documentation: https://docs.oracle.com/en/virtualization/virtualbox/6.0/user/usb-support.html
- Valve Steam installer page: https://store.steampowered.com/about/
