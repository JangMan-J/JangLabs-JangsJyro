# Steam Deck Controller Guide - A Visual Introduction

## Overview

This guide will get you started on how to use the Steam Deck's controls and how to customize layouts through Steam Controller Settings.

## Table of Contents

1. [Introduction](#introduction)
2. [A Brief Tour - Gaming Mode - Part 1](#a-brief-tour---gaming-mode---part-1)
3. [A Brief Tour - Gaming Mode - Part 2](#a-brief-tour---gaming-mode---part-2)
4. [A Brief Tour - External Peripherals](#a-brief-tour---external-peripherals)
5. [A Brief Tour - Desktop Mode](#a-brief-tour---desktop-mode)
6. [Steam Deck Controls](#steam-deck-controls)
7. [Controller Settings](#controller-settings)
8. [Getting Started - Binding a Command](#getting-started---binding-a-command)
9. [Other Commands](#other-commands)
10. [Load, Save, and Delete Layouts](#load-save-and-delete-layouts)
11. [Commands and Game Actions - Part 1](#commands-and-game-actions---part-1)
12. [Commands and Game Actions - Part 2](#commands-and-game-actions---part-2)
13. [Triggers](#triggers)
14. [Controller Settings - Without Steam Input API](#controller-settings---without-steam-input-api)
15. [Controller Settings - With Steam Input API](#controller-settings---with-steam-input-api)
16. [Action Sets and Action Layers - Introduction](#action-sets-and-action-layers---introduction)
17. [Action Sets and Action Layers - Commands](#action-sets-and-action-layers---commands)
18. [Behaviors - Introduction](#behaviors---introduction)
19. [Behaviors - Virtual Menus](#behaviors---virtual-menus)
20. [Trackpads - As Mouse](#trackpads---as-mouse)
21. [Trackpads - As Joystick - Part 1](#trackpads---as-joystick---part-1)
22. [Trackpads - As Joystick - Part 2](#trackpads---as-joystick---part-2)
23. [Trackpads - Scroll Wheel](#trackpads---scroll-wheel)
24. [Trackpads - Mouse Region](#trackpads---mouse-region)
25. [Trackpads - Radial Menu (Virtual Menu)](#trackpads---radial-menu-virtual-menu)
26. [Trackpads - Touch Menu (Virtual Menu)](#trackpads---touch-menu-virtual-menu)
27. [Trackpads - Single Button](#trackpads---single-button)
28. [Trackpads - Directional Swipe](#trackpads---directional-swipe)
29. [Gyro - As Mouse](#gyro---as-mouse)
30. [Gyro - As Joystick](#gyro---as-joystick)
31. [Joysticks - Directional Pad](#joysticks---directional-pad)
32. [Joysticks - Joystick](#joysticks---joystick)
33. [Joysticks - Joystick Mouse](#joysticks---joystick-mouse)
34. [Joysticks - Flick Stick](#joysticks---flick-stick)
35. [D-Pad - Directional Pad](#d-pad---directional-pad)
36. [D-Pad - Hotbar Menu (Virtual Menu)](#d-pad---hotbar-menu-virtual-menu)
37. [Buttons Pad - Button Pad](#buttons-pad---button-pad)
38. [Mode Shift](#mode-shift)
39. [Misc.](#misc)

## Introduction

### Preface

The next few chapters are a brief overview of the Steam Deck. If you are already familiar with it, you can skip to **Controller Settings**.
- Warning. This guide is extremely data heavy (about 775 MB of data). To reduce their file sizes, GIFs have reduced visual quality and are sped up.
- Presence of visual artifacts in the recordings such as moiré, lack of sharpness, and incorrect color reproduction are due to improper filming on my part.
- If this page does not load, try refreshing or using a different browser.

### What is Steam Deck?

The Steam Deck is a handheld gaming PC designed to play all sorts of video games on the go. Along with being equipped with the processing power to play games at a satisfying visual fidelity, its controls include not only those found on a standard gamepad but also has a gyro, two trackpads, four grip buttons, and a multitouch touchscreen. This richness in input helps enable the Steam Deck to play games designed for gamepad, keyboard & mouse, and touch input across all types of genres.

To learn more about the Steam Deck, visit the following:

- [Youtube - Introducing Steam Deck](https://www.youtube.com/watch?v=AlWgZhMtlWo)
- [Steam Deck - Homepage](https://www.steamdeck.com/)
- [Steam Deck - News Hub](https://store.steampowered.com/news/app/1675200)
- [Steamworks - Steam Deck](https://partner.steamgames.com/doc/steamdeck)

### Showcase

### How do I know which games on Steam officially support the Steam Deck's controls?

As seen in the Steam Store and your Library, games are labeled by Valve as Verified, Playable, Unsupported, and Unknown to indicate the game's out of the box experience on Deck.

As one of the criteria is input, games that are  Verified have a smooth controller experience, whereas  Playable means that there may be minor issues (can be non-controller related problems). Games that are  Unsupported do not (fully) work, and those that are  Unknown have yet to be evaluated by Valve.

Games that are not Verified when last evaluated by Valve can change to a higher rating in the future as Valve and game developers carry on with improving compatibility with the Steam Deck.

For more information on Steam Deck Compatibility program, visit the following:

- [Youtube - Steam Deck: Introducing Deck Verified](https://www.youtube.com/watch?v=_OAqvtlgfGA)
- [Steamworks - Steam Deck Compatibility Review Process](https://partner.steamgames.com/doc/steamdeck/compat)

You can find compatibility information in the store and your Steam Library via the following:

- [Steam Store - Great On Deck](https://store.steampowered.com/greatondeck)
- [Steam Store - Search](https://store.steampowered.com/search/?term=) - Filter the store search using Narrow by Deck Compatibility on the right side, and additionally sort by Steam Deck Compatibility Review Date at the top.
- Filter through your Steam Library in the desktop Steam client
- Games that have been evaluated have a Compatibility Report on their store page.

### Can I modify the Steam Deck's controls and how would I do so? Or, can I play games that do not have (full) controller support on the Deck?

If you feel like tweaking the controls for a game to align with your play style preference and find yourself unable to do so through the game's built-in controls options, or if you want to play a game that does not have controller support, consider taking a look at Controller Settings in Steam. Formally called Steam Input Configurator (SIC) and popularly known as Steam Input, Controller Settings offer a plethora of ways for you to customize your game input experience.

Examples include:

- To jump or reload your weapon in a shooting game while simultaneously controlling your aim, you can bind those commands to the grip buttons.
- Quickly access shortcuts by setting a trackpad to behave as a menu and storing multiple commands into it.
- Access shortcuts with a single button by pressing and holding it in different ways.
- To use gyro aiming in a game that does not natively support it, you can set the Deck's gyro to behave as a mouse or as a joystick. You can also set the condition for activating gyro.
- Invert an analog stick along one or both axes.
- Or do whatever you want.

Changes to the bindings in Controller Settings can be saved as a layout specific to that game or as a template that is reusable across any game. Alternatively, you can get a jump start on your layout or simply get into gaming by downloading layouts created by contributors in Community Layouts.

While I consider most of the options to be individually self-explanatory, the breadth and depth of the customization that is possible is quite vast and is the subject of this guide. Along with giving an overview of the Steam Deck's Controls, I will be going over all aspects of Controller Settings.

## A Brief Tour - Gaming Mode - Part 1

The Steam Deck can run in two modes: Gaming Mode and Desktop Mode.

### Gaming Mode

When turned on, the Steam Deck runs in a state dedicated to gaming called Gaming Mode.

You can navigate the Gaming Mode's UI called Big Picture Mode (BPM) using the device's controls and touch screen or a physical keyboard & mouse. Besides listing your recently played games, Home presents various points of interests such as game news updates and recommendations for which game in your Library to play next.

#### Steam button

Pressing the Steam button brings up a list of menu items for navigating to other parts of Steam. When you are in a game, it also brings up the Steam Overlay where you can access game-specific items such as Achievements and Guides. There are a few features worth further description.

##### Simultaneously play and use other apps

While playing, you can launch and switch to other applications such as a web browser with add-ons, a chat application, and even another game.

To run non-Steam applications in Gaming Mode, you need to first add them while in Desktop Mode. Do either of the following:

- Right-click an application, such as those in the Application Launcher (or Start Menu), and select Add to Steam.
- In the Steam client, go to either Games in the menu bar or Add a Game at the bottom-left corner and select Add a Non-Steam Game. Then select the application.

Added apps are found in your Library under Non-Steam.
For each one, be sure to create or apply an appropriate layout through Controller Settings, such as Mouse Only and Web Browser.

##### Switch to another window

When running an app or game that has multiple windows, you can switch windows through the overlay. The active window has a blue highlight next to it.

##### Notes

Via Notes in the overlay, you can create notes for any game, and they will be synchronized to your Steam account. Notes created in Gaming Mode are also accessible in the desktop Steam Client, and vice versa.

Currently, the Gaming Mode UI supports basic text editing. The full editor is currently only available in the desktop Steam client. Furthermore, images can be captured by using your keyboard's PrntScrn and pasted into Notes, which is also only available in the desktop client.

#### Universal Search

You can quickly search through your Library, Steam Friends, and Store by using the Universal Search at the top of the UI.

#### Typing on the Steam Deck

With the Steam's on-screen keyboard (OSK), you can type using the touchscreen, D-pad, joysticks, or trackpads.

For games that require you to input text but do not include an in-game keyboard nor automatically open Steam's OSK for you, in other words Steam games without full controller support, you can manually invoke the on-screen keyboard by simultaneously pressing STEAM + X button.

If the keyboard is blocking the text field, consider moving it between the top and bottom positions by holding the Shift key or Left Trigger and pressing the Move key at the bottom-right.

#### Global Shortcuts

Hold the Steam button or Quick Access button for a few seconds to bring up a reference for global shortcuts. You can use either button for invoking these shortcuts.

## A Brief Tour - Gaming Mode - Part 2

#### Quick Access Menu

The Quick Access Menu, accessed by the button with the ellipses, is a shortcut to Notifications, Steam Friends, Quick Settings, Performance, Soundtracks, and Help. Two of these warrant a deeper explanation.

##### Quick Settings

This includes useful options from the Steam Deck Settings that you may want to adjust on the fly.

Note:

- Game Rumble refers to controller vibration.
- Steam Haptics refers to additional feedback that you can feel on the Steam Deck such as when moving your thumb across the trackpad.

##### Performance

You can adjust the Performance Overlay Level to view increasingly detailed metrics on how well the Deck is running a game, such as frames per second (FPS) and frame time.

Furthermore, there are options that allow you to make tradeoffs between graphical fidelity and battery life, some of which are:

- Framerate Limit - Sets the game's maximum FPS which affects how smoothly gameplay appears. The lower the framerate, the more battery you will get in exchange for gameplay smoothness. To individually set the display's Refresh Rate and the game's Framerate Limit, disable the Enable Unified Frame Limit Management option under the Deck's Display settings.
- Enable VRR - Toggles Variable Refresh Rate (VRR) for a VRR compatible display (not supported for Steam Deck).
- Enable HDR - Toggles High Dynamic Range (HDR) for an HDR compatible display (not supported for Steam Deck LCD's display).
- Scaling Mode - Depending on the resolution set in the game, this determines how the game's content will be resized relative to the Deck's display.
- Scaling Filter - Applies an upscaling algorithm such as AMD FidelityFX Super Resolution (FSR) 1.0 and Nvidia Image Scaling (NIS).
  > To use Gaming Mode's FSR or NIS, select it in Scaling Filter and then lower the game's resolution (adjusted in-game via a display or graphics option) to less than the display's resolution; the Deck's screen is 1280 x 800 pixels, and most televisions and computer monitors are at least 1920 x 1080 (1080p). You may also need to switch between windowed mode and full screen mode through the in-game display or graphics settings.
  > If you wish to upscale a game's resolution, it is recommended to first try the game's built-in options instead of Gaming Mode's. Note that unlike Gaming Mode's, a game's built-in upscaler should not require you to lower the game's resolution for it to work.

For lower latency in a specific game in exchange for screen tearing, you can enable Allow Tearing and set Framerate Limit to Off in the Performance tab, and enter the in-game graphics or display options and set VSync to off.

#### Game Recording

You can record gameplay and edit clips to save and share with others.

See [Steam - Game Recording](https://store.steampowered.com/gamerecording) for more details.

#### Remotely Play Games

Whether it is done locally or over the internet, using Steam Remote Play you can stream Steam games from a computer to remotely play on your Steam Deck.

The same can be done from the Deck to other devices.

When running a game that supports Remote Play Together on your Deck, you can invite Steam Friends to play in a streamed, remote play session using the Quick Access button.

Alternatively, if your friends have the Steam Link app, they can join via your guest invite URL without having to create Steam accounts.

Visit [Steam Remote Play](https://store.steampowered.com/remoteplay) to learn more and download the Steam Link app.

To read all updates for Steam Link app, visit [Steam Link Android Patch Notes](https://steamcommunity.com/app/353380/discussions/4/1694922345923309554/), such as [Steam Link version 1.1.75 (Mar 23, 2021)](https://steamcommunity.com/app/353380/discussions/4/3095635055538270693/) for adding Steam Remote Play Together guest invitations.

To read all updates for Steam Link hardware, visit [Steam Link Hardware Patch Notes](https://steamcommunity.com/app/353380/discussions/0/4328520278444297841/), such as [Steam Link Build 821 (Sep 16, 2021)](https://steamcommunity.com/app/353380/discussions/0/4931994385937030659/) for adding experimental Bluetooth support for Xbox Series X controllers.

## A Brief Tour - External Peripherals

### External Peripherals

You can use external peripherals such as gamepads, keyboard & mouse, and computer monitors in both Gaming Mode and Desktop Mode by connecting them to the Steam Deck via USB-C or Bluetooth.

#### Playing with External Controllers

Besides the Steam Controller, the Steam Deck supports gamepads from all sorts of brands, including the Xbox Core (Series) Controller, PlayStation DualSense Controller, Nintendo Joy-Con, and numerous other third party controllers.

> When launching a game with at least one external controller connected to the Deck, Steam determines the controller order by the order in which it receives input from each controller.

While playing a game, this order can be changed by using Rearrange Controller Order which is found in Quick Settings and Controller Settings.

> To open Quick Access with an external controller, press Steam + A (Home/Xbox/PS + bottom face button).

There are games that only allow the first controller to do anything in-game and reject input from other ones, as noted in the Steam Deck compatibility report.

To play these with an external controller, you may need to reorder the external one to become the first one. Such may be the case if you interact with the Steam Deck Controller first after launching the game instead of the external controller.

#### Playing on an External Display in Gaming Mode

In Gaming Mode, when playing on the Steam Deck's screen, also called the internal display, games will by default run at a maximum resolution of 1280 x 800. When playing on a computer monitor or television connected to the Steam Deck, also called the external display, games will by default run at a max of 1280 x 720 (720p) on a 16:9 display and 1280 x 800 on a 16:10 display.

To increase the maximum resolution a specific game can run at when playing on an external display:

1. Go to the game in the Library -> Settings (gear icon) -> Properties -> General -> Game Resolution -> change from Default to the desired resolution.
2. Afterwards, you may also need to launch the game -> enter the in-game graphics or display settings -> set the desired resolution.

It is important to note that when the resolution is set higher, the harder it will be for the Steam Deck to run the game smoothly. For less graphically and computationally intensive games such as 2D games and older 3D titles, it is possible to maintain a visually smooth experience at higher resolutions, such as 1600 x 900, 1920 x 1080 (1080p), and even 3840 x 2160 (4K). If you are experiencing gameplay stutters, you may find it better to leave the Game Resolution at Default.

> The Game Resolution option only affects the maximum resolution the game can run at when an external display is connected. Without an external display connected, the default max resolution when playing on the Steam Deck's display is 1280 x 800.

If you wish to run a game at a higher resolution on the Steam Deck's display (i.e. without an external display connected), adjust the Game Resolution and toggle the option for Set resolution for internal and external display.

#### Connecting Multiple Wired Peripherals

Using the [Steam Deck Docking Station](https://www.steamdeck.com/en/dock) or most USB-C compliant docks or hubs, you can connect multiple wired peripherals such as a USB-C charger, a computer monitor, a keyboard, and a gamepad in both Gaming Mode and Desktop Mode.

## A Brief Tour - Desktop Mode

From Gaming Mode, you can switch to Desktop Mode through the Power menu.

### Desktop Mode

The Steam Deck is a PC.

In Desktop Mode, you can use the Deck as you would with any regular PC such as browsing the internet and playing games on Steam.

The Deck runs on SteamOS 3, an operating system that is based on [Arch Linux](https://archlinux.org/)[archlinux.org] and uses [KDE Plasma](https://kde.org/plasma-desktop/)[kde.org] for its desktop environment.

#### Finding more apps

Use the KDE Discover (Software Center) to find applications to use in SteamOS.

You can download various software to write documents, play videos, manage spreadsheets, edit images and videos, create 3D models, and more.

#### Steam Deck's Display

Note that the Deck includes a 800 x 1280 portrait display. Therefore, in the Display Configuration found in System Settings -> Display and Monitor, it is correct that by default the Deck's display is set to 90 degrees counter-clockwise for its Orientation.

Consequently, if you experience screen tearing, it will appear vertically on the Deck's display rather than horizontally, which is the case for landscape displays typically found in computer monitors and televisions. This may be observed on the Deck's display in Gaming Mode by enabling Allow Tearing and setting the Framerate Limit to Off through the Performance tab in Quick Settings and turning off V-Sync in-game.

#### Keyboard and Mouse Shortcuts

There are keyboard and mouse shortcuts in SteamOS for executing a multitude of actions.

##### Keyboard

Keyboard shortcuts are found in System Settings -> Workspace -> Shortcuts. You can reset shortcuts to their default assignment via the Defaults button at the bottom of the window. Note that the Meta key is a synonymous with Super, Windows, and Command key on a keyboard.

Here is a short list of shortcuts to get you started:

| Keyboard Shortcut | Action | Note |
|---|---|---|
| Meta | Open application launcher, Kickoff | Similar to Window’s Start Menu |
| Alt + Tab | Switch forward between windows |  |
| Alt + Tab + Shift | Switch backwards between windows |  |
| Alt + F4 | Close window |  |
| Meta + W | Toggle overview | Show and switch between all windows/desktops, as well as add and remove desktops |
| Meta + D | Show and hide the desktop |  |
| Meta + E | Open file manager, Dolphin | Similar to Window’s File Explorer |
| Meta + V | Open clipboard history, Klipper |  |
| Meta + 1, Meta +2, … | Launch application in task manager | Similar to Window’s taskbar; right-click an app and select Pin to Task Manager to save it to the task manager |
| Ctrl + Esc | Open System Activity | Similar to Window's Task Manager; this is a bit different from the other app System Monitor |
| Ctrl + Alt + Esc | Kill window | After pressing the key combination, select a window to quit that application |
| Print Screen | Open screen shot capture utility, Spectacle | Similar to Window’s Snipping Tool |
| Meta + Print Screen | Screenshot active window |  |
| Shift + Print | Screenshot desktop |  |
| Meta + Shift + Print | Screenshot rectangular region |  |
| Meta + . | Emoji Selector |  |
| Alt + Space, Alt + F2 | Open KRunner |  |
| Ctrl + Alt + T | Open the terminal, Konsole | Similar to Window’s Command Prompt or Powershell |
| Meta + P | Switch display | Useful when you connect another monitor |

##### Mouse

By going to System Settings -> Workspace -> Workspace Behavior -> Screen Edges, you can execute different actions depending on the corner and edge you continuously move the mouse cursor into. Reduce the activation delay to shorten the time you need to keep moving the mouse in order to activate the action.

You can adjust your mouse buttons' actions on the desktop by right-clicking any empty space -> Configure Desktop and Wallpaper... or pressing Alt + D + S -> Mouse Actions

- If you accidentally remove Right-Button set as Standard Menu, you can always reopen this setting by using the keyboard shortcut mentioned above on the desktop.
- If you do not want Sticky Notes to appear on the desktop with Middle-Button click, which may be the case you click the Deck's left trackpad on the desktop, change the action from Paste or remove this shortcut by pressing the minus button next to the shortcut.

#### Return to Game Mode

The quickest way to return to Gaming Mode is to use the "Return to Gaming Mode" shortcut on the desktop.

To learn more about Desktop Mode, visit [Steam Support - Steam Deck Desktop: FAQ](https://help.steampowered.com/en/faqs/view/671A-4453-E8D2-323C).

## Steam Deck Controls

### Controls

The Steam Deck is equipped with controls that are found on a typical gamepad:

- Button pad (A B X Y)
- D-pad
- Menu & View buttons (also called Start & Select)
- Steam button (also called Guide button) & Quick Access button
- L & R bumpers (also called L1 & R1)
- L & R analog triggers (also called L2 & R2)
- Dual analog sticks (with clickable thumbsticks also called L3 & R3)
  Additionally, it features augmented controls:
- Gyro
  By default, gyro activates only when touching the right trackpad or tumbstick, and this condition can be changed if you like.
- Dual Trackpads which have capacitive touch
- Dual analog sticks also have capacitive touch
- Four assignable grip buttons (also called L4 & R4 and L5 & R5 buttons)
- Touchscreen (multi-touch display, supporting up to ten fingers)

If you have the Steam Deck and want to familiarize yourself with the controls while playing a game, consider checking out Valve's free, playable short [Aperture Desk Job](https://store.steampowered.com/app/1902490/Aperture_Desk_Job/).

## Controller Settings

After familiarizing yourself with the Steam Deck controls, how would you go about customizing what they do? This is where Controller Settings steps in.

> The behavior of each control on your Steam Deck or controller can be changed through Controller Settings in the Steam client to do something else.

Through Controller Settings, you can modify each of the buttons, triggers, D-pad, analog sticks, and trackpads to do something else in a game.

From here, I will be guiding you on the various topics about the Controller Settings to get you started on creating a layout for the Steam Deck.

First, what is Steam Input? When Steam Input is mentioned in conversations, they usually refer to one of the following:

- When a person says to "change bindings in Steam Input," they refer to Steam Input and Controller Settings synonymously. I will be doing the same throughout this guide.
- When a person says a game has "native Steam Input," they mean the game has implemented Steam Input API (SIAPI), which will be explained more throughout the guide.

That said, officially, Steam Input refers to the collection of software, hardware, and configuration utilities that Steam uses to interface with games. For the Steam user, it handles anything that is gamepad related, examples include:

- Controller Settings
- Adjusting the sensitivity of a gamepad's analog sticks
- Managing multiple gamepads connected to the device
- Modifying the color a gamepad's LED emits

Updates to Steam Input can be found in the Steam Client update patch notes.

For official documentation, check out [Steamworks - Steam Input](https://partner.steamgames.com/doc/features/steam_controller) to learn more about Controller Settings and Steam Input API. I will also cover SIAPI in Controller Settings - With and Without Steam Input API chapter.

### Accessing Controller Settings

Controller Settings can be accessed in two ways:

- While in-game, press the Steam button -> move to the right (or press Controller Settings) -> Controller Settings.
- While in the Steam Deck UI, navigate to your game in the library -> Controller Settings (represented by the gamepad icon).

I use the first way more often since editing the controls to my liking usually involves going back in forth between making changes in Controller Settings and testing them in-game.

### Notation on Reading the Next Chapters

In the following chapters, I will be constantly referring to the different parts of the Deck's controls, the gamepad and keyboard & mouse commands in Controller Settings, and the corresponding actions in game.

For the sake of clarity, I will use the following notation to distinguish which of the three I am talking about.

- [Steam Deck control] - When enclosed in brackets, this refers to some part of the Steam Deck.
- {Command} - When enclosed in braces, this refers to a command in Controller Settings.
- *Action* - When capitalized and italicized, this an action in the game.

Some examples:

- [A] is set to {A Button} - When Deck's [A button] is pressed, the {A Button} is triggered in-game. In the case of platformer games, the character would *Jump*.
- [Right Analog Stick] has an Outer Ring Command set to {Right Trigger} - For the case of twin-stick shooters, moving the [Right Analog Stick] to its edge in the game will cause {Right Trigger} to be triggered, causing the character to *Fire*.
- [Start] is set to {Esc key} - Pressing the Steam Deck's [Menu] button will correspondingly press {Esc key} in-game. This will bring up the *Pause Menu* or *Back* out of a menu option in most games.

### Updated terminology

Although the same customization and configuration concepts have made their way into the Steam Deck UI from the Steamwork documentation and the previous iteration of Big Picture Mode (BPM), the words that represent them have changed. The following is a list correlating some of the notable terminology between them:

| **Steam Deck - Current Big Picture Mode** | **Old Big Picture Mode** | **Steamworks Documentation** | **Notes** |
|---|---|---|---|
| Controller Settings | Controller Configuration | Steam Input Configurator (SIC) | I will also refer to this as Steam Input |
|  |  | Native and Legacy mode | I will refer to this as with and without SIAPI |
| Layout | Configuration or Config | Configuration or Config |  |
| Command | Activator | Activator |  |
| Sub command | Binding | Binding |  |
| Activation | Activation Type | Activation Type |  |
| Behavior | Style of Input | Input Source Mode |  |
| Joystick (Behavior) | Joystick Move (Style of Input) | Joystick Move (Input Source Mode) |  |
| As Joystick (Behavior) | Mouse Joystick (Style of Input) | Mouse Joystick (Input Source Mode) |  |
| As Mouse (Behavior) | Mouse (Style of Input) | Mouse (Input Source Mode) |  |
| Virtual Menus |  |  | New. Radial, Touch, and Hotbar Menus are different types of Virtual Menu |

## Getting Started - Binding a Command

When entering Controller Settings, you will see the following:

- View layout - An overview of the controller being used along with the bindings assigned to each control.
- Edit layout - Menu for modifying any of the controller's controls.
- Quick Settings - A short menu for enabling and editing grip buttons as well as defining gyro and right trackpad behaviors.

### Assigning a Command

Let us start off with binding a command.

In this game, pressing the [A button] causes the character to *Jump* and [L2] causes the character to *(Reset) Camera / Graffiti action*.

Open the Steam Overlay and scroll to the right. Laid out on this screen are all of the controls on your Steam Deck, or connected controller, and their assigned commands.

For this game, the developer's recommended layout is a gamepad template from Valve, so all of the Deck's controls are assigned with controls found on a gamepad. For example, pressing the [Right Bumper] on the Steam Deck will correspondingly press a gamepad's {Right Bumper}.

There are two ways to navigate the UI to modify a control:

1. Go into Edit layout, select the category, and navigate to the control.
2. Go into View layout, press down, navigate to the control, and press the A button (currently available in Steam Deck Client Beta). The UI will automatically switch over to Edit layout with the selected control highlighted.

In the Buttons category, got to the [A button]. There are two ways to change what this button does:

- Select the [A button].
  Presented here are all of the commands that you can assign, thematically grouped along the top of the screen, and choosing any command here will rebind what the [A button] does. Select the {Left Trigger}.
- Listen for a command by pressing the Start button when the [A button] is highlighted.
  When the Listen dialogue appears, press the gamepad, keyboard, or mouse input that you want to assign to the button (for the latter two, you will need to have a physical keyboard and mouse connected to the Steam Deck). For this example, press the Deck's {Left Trigger}.

Go back to the Edit layout screen, select the [Y button], and bind it to the {Esc key}.

While you are in Edit Layout, you can also name a command by selecting the gear icon next to it and using Rename Command. Also, you can press the [View button] to preview your layout.

Return to the game, and press the [A button] on your Deck, and notice that the resulting in-game action is as if you have pressed the [L2] which is *(Reset) Camera / Graffiti action*. Pressing the [Y button] on your controller will activate the {Esc key} in-game, bringing up the *Pause Menu*.

Let us look at another example.

### Assigning a Game Action

In this game, pressing the [L4 grip button] causes the character to *Swap Weapon* and the [R4 grip button] to *Crouch / Slide*.

In View Layout, notice that the developer has created a custom layout. Now, enter Controller Settings.

Making sure that the Action Set at the top-left in Edit layout or the top in View layout is On-Foot, select the [R4 button].

In addition to the commands you saw earlier, you may notice there is another category called Game Actions, where laid out on this screen are all of the in-game actions that can be assigned to this button.

The reason why the previous game I showed did not have this category while this did does is because this game has Steam Input API (SIAPI) implemented into it (the previous game predates SIAPI). This means that rather than binding gamepad and keyboard & mouse commands to the Deck's controls, you directly bind the actions instead. For example, if you want to *Heal* by pressing the [L5 grip button], rather than having to recall which gamepad control it is assigned to and then selecting it under the Gamepad category, you simply choose *Heal* from the Game Actions category.

When SIAPI is fully implemented, as the developers have done in this game, Controller Settings behaves the same as an in-game controller options rather than just an input wrapper.

Continuing on, under Game Actions, select the *Roll* action. Go back to the Edit layout screen, select the [L4 grip button], and bind it to the *Reload*.

Now when I press [R4] and [L4], the character can *Roll* and *Reload*.

### Quick Settings

Even if you do not plan on diving that deeply into customizing the controls, it is worth taking a look at Quick Settings in Controller Settings.

- To use the Deck's grip buttons, toggle on Enable Back Grip Buttons for the action set that you want to use the buttons with and then you can map whatever commands you like. More information on action sets can be found in Action Sets and Action Layers chapter.
- To use Gyro for cursor or camera control, set its Behavior to either As Mouse or As Joystick (or an equivalent Behavior created by the developer). More information on this can be found in the Gyro - As Mouse and Gyro - As Joystick chapters.
- To use Right Trackpad for cursor or camera control, set the Right Trackpad Behavior to either As Mouse or As Joystick (or an equivalent Behavior created by the developer). More information on this can be found in the Trackpads - As Mouse and Trackpad - As Gyro chapters.

To use other Behaviors for the gyro and trackpads, you can find them in Edit layout.

### Summary

To summarize this chapter:

- Use View Layout to see a quick overview of the controls and the commands' names, when given a description.
- In addition to assigning gamepad and keyboard & mouse bindings to the controls through Edit Layout or Quick Settings, if the developer has fully implemented Steam Input API, you can directly assign the game's actions.
- To use the Deck's grip buttons, you can enable enable it in Quick Settings.
- To use the gyro or trackpad for cursor or camera control, set its Behavior to either As Mouse or As Joystick.

## Other Commands

There are other commands besides gamepad and keyboard & mouse commands.

### Action Sets

This lets you

- Change Action Set
- Hold Action Layer
- Apply Action Layer
- Remove Action Layer
- Cleared from Parent

Details on these are covered in Action Sets and Action Layers chapter.

#### Take Screenshot

When you are in a game, screenshots taken using this command can be found in Your Stuff under the corresponding game's Library page, or you can see your screenshots for any game in Media.

Note that this does not use the operating system's screenshot function, and there is no command for PrtSc (print screen).

#### Show Keyboard

This brings up Steam Deck UI's on-screen keyboard.

One reason why some games do not have Full Controller Support in Steam is because they are either missing an in-game keyboard or have not implemented Steamworks SDK on-screen keyboard that would otherwise be used for typing in a text field, such as naming a character or text chatting in-game.

#### Toggle Magnifier

This toggles the operating system's magnifier to enlarge the screen. This is in contrast to the magnifier in the global shortcut that remains on screen only while you hold down STEAM + Left Shoulder button.

This is useful to bind when you are playing a game where you have to frequently read small text.

#### Force Game Shutdown

Activating this command will forcefully quit the game. While this will cause you to lose any unsaved progress, it can be useful for exiting a game that is frozen and cannot be closed by the usual methods.

#### Change Controller Player Number

This sets the controller to be a specific player number. Note that a device running the Steam client can connect up to 16 controllers.

For a game that has local multiplayer, and multiple controllers have been connected to the Deck, the game may automatically designate a player number to each controller. If you want a specific controller to always be Player 1, another controller to always be Player 2, etc., then this allows you to quickly change the player number of that controller without having to use the Quick Access Menu to readjust it.

### Mouse

#### Move to Position

This command causes the mouse cursor to jump to a location on the screen that you have specified. You also can set it so that when the button is released, the cursor either returns to its position prior to the jump or remains at its new position.

It is important to note that if the cursor position was recorded when playing the game at a specific resolution, such as the Deck's display resolution of 1280 x 800 pixels, Steam Input will relatively scale that cursor position when the same game is played at a different resolution, which may be the case when docking the Steam Deck and playing on a 1920 x 1080 (1080p) monitor. If the game's UI does not scale in the same manner, the cursor position that did something useful on the Deck may no longer be doing anything useful when playing the game at a different resolution. In that case, you will need to set cursor position again for different resolutions.

#### Move Mouse by Amount

This moves the cursor by an amount that is relative to the cursor's position. An example where this is useful is to perform 180 degree turns in first/third person games.

## Load, Save, and Delete Layouts

After configuring a layout for a while, how do you make sure that your changes will be saved? Or how do you load your own or other people's layouts to use as your own? And finally, what if you no longer like your layout and want to delete it? Let us see how to do all of those in this chapter.

### Save

Enter Controller Setting for a game and select Layout Options, represented by the gear icon next to Edit Layout.

This screen is where you can manually save your layouts.

#### Export Layout

While Steam will periodically auto-save the layout you are using, you can also manually save it with a custom name and description, and there are two types of saves: personal save and templates.

##### Personal Save

Layouts saved as personal saves are available specifically for the game that you made it for. They are synchronized to your Steam account, and can be found under Your Layouts category, as described in the next section. When you sign into your Steam account on any Steam Deck and launch a game that you have saved a layout for, your layout will automatically be loaded. Note that when Steam auto-saves a layout, it is saved as a personal save.

If you have made changes to a layout and want to test out other layouts from the community, I recommend saving your layout first through this process.

##### Templates

A template is a layout that you have access to in any game. Similarly, your saved templates are synchronized to your Steam account, and are found in Templates category, as described in the next section.

If you have modified a layout that you plan on reusing across many games, consider saving it as a template. For example, if you usually use the Gamepad With Camera Controls Template and prefer to assign {A B X Y buttons} on specific grip buttons, rather than repeatedly modify that template in multiple games, you can edit the template as desired and export the layout as a new template. The next time you want the same adjustments, you can save some time by loading the template you have created.

#### Share Layout with Community

If you want to share your layout with other Steam users, you can export your layout to the community. In order to upload a layout, you must play the game using your layout for at least 5 minutes without making any adjustments to the layout. Exporting a layout here will also create a personal layout under Your Layout category.

### Load

Return to Controller Setting and select the layout being used.

The Load new Layout screen is where you can find layouts that you and other people have created. The blue line on the left side of a layout indicates which layout you are currently using.

#### Recommended

This category contains layouts created by developers or Valve recommended templates, and it only appears when there is at least one layout.

#### Your Layouts

This category holds all of your saved layouts, and it only appears when you have at least one saved layout.

#### Templates

At the top of the list are Valve provided templates which are applicable to many games. Note that if you plan on using the Keyboard (WASD) and Mouse template, you will very likely need to customize it in order to match the keyboard and mouse commands used by the game.

Located below Valve's templates are all of your saved templates that you plan on reusing.

#### Community Layouts

Layouts that have been shared by the community are found here.

### Delete Layouts

To remove your layouts, whether they are personal saves, templates, or community layouts, go to Your Layouts, highlight their entries, and press Delete Layout.

## Commands and Game Actions - Part 1

You may have noticed that throughout Controller Settings, you can assign game actions, gamepad buttons, and keyboard & mouse keys to not only each button but also trackpad click and touch, triggers, and quite a bit more.

Furthermore, you can assign multiple commands (and sub commands) to each of these, and you can customize how each command activates, such as a regular press or a double tap, as well as how it behaves by accessing their options via the gear icon. All of this can lead to interesting configuration possibilities.

For the sake of brevity, since the options for commands and game actions are the same, I will refer to them synonymously.

### Activation Type

Upon selecting Regular Press, a list of Activations appear. Every command has its own Activation, and the Activation affects the command's primary activation condition.

The activation condition determines how your interaction with the button or control will activate the command. For example, if Regular Press, the default Activation, is changed to Double Press, then you have to tap the button twice within a certain amount of time for the command to activate. If set to Long Press, then you have to hold the button for a length of time after which the command will execute.

There is another activation condition that can be found found in a couple of the Activation's settings.

For now, here is the list of command Activations:

- Regular Press - This is the default choice whenever you create a command, and it is the standard button behavior that you would expect in any game that supports controllers. The command remains active while the button is held down.
- Double Press - Press a button twice within the Double Tap Time, a user assigned value between 0 and 1000 milliseconds (1000 milliseconds = 1 second), to activate this command. The command remains active while the button is held down after the second press.
  - For a scenario to be aware of, let us say a button has both Regular Press and Double Press commands and you intend to activate Regular Press. After pressing the button once, the Double Tap Timer duration must elapse before Regular Press can trigger, since Steam Input is waiting to see if you will press the button a second time to trigger the Double Press condition. Set Double Tap Timer long enough and the delay for Regular Press activation will be noticeable.
- Long Press - Hold a button for the duration of Long Press Time, a user assigned value between 0 and 1000 milliseconds, to activate this command. The command remains active while the button is held down after the command activates.
- Start Press - This command activates for a single moment right when you press the button.
- Release Press - This command activates for a single moment right after you release the button.
- Analog - This command is only available under Soft Pull for triggers and Outer Ring Command for analog sticks or trackpads. Through the command's settings, you can map the control's input range to another control's output range. One peculiarity is the command assigned to Outer Ring Command does not do anything; it only needs to be assigned so its Activation can be set to Analog.
  - For example, let us say for a driving game, the [right analog stick] has Outer Ring Command with Analog activation. In the command settings, the Analog Output Axis can be set to {Right Trigger}. When you push the stick towards the top or bottom, the {Right Trigger's} output will gradually increase, which correspondingly increases the *Vehicle's Acceleration* in-game.
  - As a side note, this is particularly useful for the Steam Link Touch Controller, since this is the only way to access the full range of the triggers on a touchscreen.
  - Note that the full range of the Output Axis control is mapped to the input control. Analog Range Start determines how far you must engage your input before the Output Axis control outputs its initial value. Analog Range End determines when maximum output from the Output Axis control occurs.
- Soft Press - This command activates when it is below the Soft Press Threshold, particularly useful when used with the Click for trackpads, Soft Pull for triggers (when there are multiple commands), and Outer Ring Command for analog sticks or trackpads.
  - If you swipe across the trackpad and accidentally invoke the Click command, consider adjusting the command's Soft Pull Threshold higher.
- Button Chord - This command activates by holding down a button the user designated as the Chord Button and then pressing the button the Chorded Press is assigned to.
  - For example, let us say in a RPG game, *Quick Save* has a keyboard hotkey of [F5]. If you want to press two buttons simultaneously to activate that action, you can assign [F5] command to the [L1 button] and set it to use Button Chord activation. In the command settings, set the Chord Button to [View button]. Go to the [View Button] and Add Extra Command, assign that with an Empty command, and set it to Long Press activation. To invoke *Quick Save*, you would hold down [View button] and then press the [L1 button].

#### Interruptible

In addition to the activation conditions mentioned above, Regular Press and Release Press have another one, a setting called Interruptible. When toggled on, the command can be prevented from firing off by prioritizing another command that is activating. When set to Off, the command acts independently of others' command activations.

- Unless you have a particular use case, leaving this at the default setting is fine.
- As an example, by default, Regular Press has Interruptible set to On. If the button is also paired with a Long Press command, holding down the button long enough will activate the Long Press command and not the Regular Press command. If Interruptible is set to Off, then both Regular Press and Long Press will activate.

## Commands and Game Actions - Part 2

### Sub Commands

To trigger multiple bindings at the same time, you can add sub commands to a command. When a command's activation conditions are cleared, the command and all of its sub commands will simultaneously activate.

In this game, magic is casted by first holding [R2] to open an in-game menu and then pressing [X, Y, or B button]. If I find myself using the {B button} spell frequently, I can bind the combination to [L4 grip button] by assigning a {Right Trigger} command with a {B Button} sub command.

If you are familiar with BPM, you may recognize this as Multi-Button binding.

### Multiple Commands in a Single Button

You can also trigger multiple bindings at the same time by adding extra commands to a button. When each of them have the same Activation and settings, in effect this is no different from a command with multiple sub commands. The more interesting behavior comes about when each command has a different Activation.

Here, I have assigned the [View button] to *Open Inventory screen* with Regular Press, *Open Goals/Notes screen* with Long Press, and *Quick save* with Double Press.

When multiple commands are associated with a button, the Activation causes commands to trigger in the following sequence:

1. Start Press
2. Regular Press, Long Press, Double Press, Chorded Press
  - The first and second button press for activating Double Press will each activate the Start Press and Release Press commands.
3. Release Press

### Command Settings

Besides the individual settings that are specific to each Activation, other customization are available in Command Settings.

#### Hold to Repeat (Turbo)

When toggled on, you can hold a button down to repeatedly activate the button's command, as if you were repeatedly pressing the button (for Regular Press).

Repeat Rate value determines the time between each command activating, ranging from 10 to 1000 milliseconds.

#### Fire Start Delay and Fire End Delay

Fire Start Delay and Fire End Delay controls when and for how long a command is active after clearing the conditions of the Activation:

- Fire Start Delay - Determines how much time must pass before the command is triggered, ranging from 0 to 1000 milliseconds.
  - If a Regular Press command has Fire Start Delay set to 0.5 seconds, after pressing the button, the command will trigger after 0.5 seconds.
  - If a Long Press command, with Long Press Time set to 0.25 seconds, has Fire Start Delay set to 0.5 seconds, after holding the button for 0.25 seconds, the command will trigger after another 0.5 seconds passes.
- Fire End Delay - Determines how long it must take for the command to stop being active, ranging from 0 to 1000 milliseconds.
  - If a Regular Press command has Fire End Delay set to 0.5 seconds, after pressing and releasing the button, the command will trigger and remain active for 0.5 seconds.
  - If a Start Press command has Fire End Delay set to 0.5 seconds, since the Start Press command completes the moment a button is pressed, the command will immediately trigger and remain active for only another 0.5 seconds.

For a button with multiple commands, the timer for a command's Fire Start Delay and Fire End Delay begins after its command's activation conditions are cleared. For example:

- If a button has three Regular Press commands with Fire Start Delay are set to 0 seconds, 0.25 seconds, and 0.50 seconds, the timers for Fire Start Delay will activate
  - For one of the Regular Press, 0 seconds after the button is pressed
  - For one of the Regular Press, 0.25 seconds after the button is pressed
  - For one of the Regular Press, 0.50 seconds after the button is pressed
  - In other words, they are activating in 0.25 seconds intervals.
- If a button has Start Press, Release Press, and Long Press commands with Fire Start Delay set to 0.25 seconds, 0.50 seconds, and 0.75 seconds, respectively, the timers for command's Fire Start Delay will activate
  - For Start Press, 0.25 seconds after the button is pressed
  - For Release Press, 0.5 seconds after the button is released
  - For Long Press, after 0.75 seconds after the button has been held for the duration of Long Press Time

Here, I have assigned a button with four Regular Presses to achieve a combination of jumps and rolls: a 0.1 seconds Fire End Delay, a 0.5 seconds Fire Start Delay, a 0.675 seconds Fire Start Delay, and a 1 second Fire Start Delay.

#### Cycle Commands

You can sequentially fire off the parent command and its sub commands by fulfilling the command's activation condition.

Here is a Regular Press command with two sub commands. Each button press causes the character to switch weapons.

If it was instead a Double Press, then you would quickly tap the button twice for a command to execute before the next one is cycled to.

#### Toggle

When set to On, the command will be continuously active after its activation condition is fulfilled. When fulfilled again, the command stops being active.

However, it is important to note that if you press a button to toggle the binding, such as [Y Button] to toggle {Control Key}, and then press the [­B button] assigned with {Control Key}, this will stop that command's in-game action.

### Multiple Sub Commands vs Multiple Commands

Multiple sub commands is useful when you want to activate multiple commands at the same time with a single button, and the same can be done by assigning multiple commands with the same Activation to a button. If this is all that is needed, then creating multiple sub commands is sufficient.

On the other hand, some games may require a specific button to be held down before pressing other buttons to trigger in-game actions, in which case using multiple commands would be the better way.

As an example, this game does not consistently interpret [R2] command with [ABXY button] sub command as casting a spell, then the solution is to create [R2] command with a Fire End Delay and another [ABXY button] command with a Fire Start Delay. With the correct values for both delays, a spell can be casted with a button press.

### Recap

To bring it all together, a command has three parts:

1. The command.
  - Whenever you select a game action, gamepad button, or keyboard & mouse hotkey, you are setting a command.
2. The activation conditions, which need to be cleared before the behavior of the command can become active.
  - This is determined by the command type and Interruptible setting.
3. The behavior of the command that is sent to the game.
  - The command can be sent as is or be modified by command settings, such as Fire End Delay and Hold to Repeat (Turbo).

## Triggers

Besides being used as simple buttons, analog triggers like those found on the Steam Deck can output a range of values which correspondingly allows you to customize the triggers' behavior through Steam Input.

### Full Pull and Soft Pull

Note that to explain Full Pull and Soft Pull in this section, in the left and right's Trigger Settings I am setting Analog Output Trigger to Analog Off and Trigger Threshold Style to Simple Threshold in a controller supported game without using SIAPI.

In Edit Layouts, each trigger has a Soft Pull and Full Pull to which you can assign commands to, and each pull command will activate depending on how far you pull the Deck's trigger (assuming the command's activation conditions have been fulfilled as well).

When Analog Output Trigger is set to Off, assigning Soft and Full Pull commands does the following:

- As you pull an analog trigger, the Soft Pull will activate at the Trigger Threshold Point.
  - Located in Trigger Settings, the Trigger Threshold Point can be set to a smaller value for Soft Pull to activate sooner in a pull or larger for it to activate later.
    In this example, I have [Right Trigger]'s Soft Pull set to {Right Trigger}, so when I pull the trigger past the Trigger Threshold Point value, the full value of {Right Trigger} is activated.
- As you pull an analog trigger, the Full Pull command will activate near the end of the pull.
- As you pull a digital trigger, both Soft Pull and Full Pull command will activate at the same time.

You will feel haptic feedback when the Soft Pull and Full Pull activate on the Steam Deck.

Here, I have assigned {Right Mouse Click} to Soft Pull and {Left Mouse Click} to Full Pull on [R2], allowing me to softly pull on the trigger to aim the weapon and pull all the way to fire.

### Analog Output Trigger

To explain Analog Output Trigger, I am re-enabling Analog Output Trigger and removing the Soft Pull and Full Pull commands from both triggers in this section.

Analog Output Trigger is responsible for enabling the range of values that the triggers can send to a game.

There are three choices for Analog Output Trigger:

- Analog Off - Turns off the trigger's analog (or binary) output.
  - This specifically disables the trigger's output of analog values but does not prevent Steam Input from sending any assigned pull commands based on their custom trigger behaviors to the game.
- Left or Right Trigger - Choose if you want the analog (or binary) output to be from the left or right analog (or digital) trigger.

In other words, even when Soft Pull and Full Pull commands are not assigned, Analog Output Trigger does the following:

- If set to Analog Off, pulling on the triggers does nothing.
- If set to Left or Right Trigger, the game will respond to the analog (or binary) output of the analog (or digital) triggers.

While it is redundant to assign a Soft or Full Pull command when Analog Output Trigger is enabled in a controller supported game, for quick reference in View Layout, it can be useful to assign a Full Pull command with a name.

### When to enable or disable Analog Output Trigger

Another question to ask is, when should Analog Output Trigger be enabled in a controller supported game without SIAPI?

- Enable Analog Output Trigger when:
  - The game uses the analog output from analog triggers, such as a driving game.
  - The game uses triggers as buttons, and you are fine with how far you have to pull the trigger to invoke the in-game action or can customize this as you like in-game.
- Disable Analog Output Trigger when:
  - You are assigning commands that are not [Triggers] to the pull commands, such as keyboard & mouse buttons and gamepad face buttons, in a controller supported game.
    - It is important to note that if Analog Output Trigger is still enabled while make the changes above, then trigger output will continue to be sent to the game when the triggers are pressed, leading to unintended actions.
  - The game uses triggers as button, but you are not fine with how far you have to pull them to invoke the in-game action and cannot customize this as you like in-game, such as firing a weapon in a shooting game and punching in a fighting game.

By default, all of Valve's gamepad templates have Analog Output Trigger enabled.

### Threshold Trigger Style

When Analog Output Trigger is Off, another interesting modification can be made.

In the Full Pull and Soft Pull section, I showed I can aim using Soft Pull and fire using Full pull on the same trigger, but what if I wanted to also shoot without aiming while using the same trigger? Or in another scenario, what if I want a more responsive right trigger for rapidly firing weapons? This is where Threshold Trigger Style comes in.

With Threshold Trigger Style, the behavior of the trigger can be adjusted.

- Simple Threshold - Soft Pull activates at the Trigger Threshold Point and Full Pull activates when almost pressing the trigger all the way. Useful when:
  - Planning on doing mouse clicks and drags such as in strategy games.
  - Holding action layers.
  - Only need simple behavior.
- Hair Trigger - When pressing and releasing of the trigger is done beyond the Trigger Threshold Point, the Soft Pull command can be repeatedly sent with short travel distances. Useful when:
  - Need to rapidly fire a weapon with trigger pulls.
- Hip Fire Agressive/Normal/Relaxed - Used if you have both Soft Pull and Full Pull commands assigned but want to be able to activate Full Pull only or Soft Pull followed by Full Pull. Useful when:
  - Being able to aim and shoot or just shoot with one trigger.
- Hip Fire Exclusive - Used if you have both Soft Pull and Full Pull commands assigned but only want one pull to activate whenever you pull the trigger. Slowly pull for Soft Pull and quickly pull all the way for Full Pull. Useful when:
  - You want two commands on a trigger without triggering both in a single pull.

By default, all of Valve's gamepad templates use Hair Trigger.

### Other Settings to note

#### Trigger Response Curve

When Analog Output Trigger is enabled, this determines the correlation between your input via depressing the trigger and the analog output value sent to the game.

#### Trigger Range Start and End

When Analog Output Trigger is enabled, Trigger Range Start and Trigger Range End determine the trigger's deadzone.

When a trigger is not physically resetting to its original position after being pressed and released, resulting in undesired output to the game, adjusting the trigger's deadzone can mitigate this problem.

## Controller Settings - Without Steam Input API

It is difficult to continue discussing Controller Settings without first describing how your customization of a game's layout is dependent on whether or not a game fully implements Steam Input API (SIAPI). This chapter also details many of the characteristics of what I think makes a good Steam Input experience from a user's perspective.

Without SIAPI, you are able to map gamepad and keyboard & mouse keys to each of the controls. Essentially, Steam Input acts as an input wrapper.

When you press a button on your Deck, Steam Input interprets that into whatever command you assigned to the button, and then it sends the command to the game. The game then executes the corresponding action in-game. As far as the game knows, it is unaware of the existence of Steam Input and of the fact that the sent commands originate from the Deck's controls.

Although Controller Settings offers extensive customization, depending on how a game handles input, you can experience undesired side effects when mixing gamepad and keyboard & mouse commands.

Common examples of why you may want to use simultaneous (or mixed) input types include:

- When playing a first person game, you may be satisfied with gamepad input but prefer to use gyro to aid with camera control, in which case you would set gyro to use a Behavior called As Mouse (not As Joystick). This sets the gyro to control the mouse.
  - It should be said that players who enjoy this approach to gaming will find it frustrating when they find out that a game that they like does not support this concept. While it is possible to use As Joystick in place of it, having the gyro control a joystick typically runs counter to the preferred gyro interaction, leading to a subpar experience, as explained in the chapters Trackpads - As Joystick.
- A game's gamepad input may be missing actions that are only available for the keyboard & mouse. To suit your play style, you may feel inclined to combine the two.

> For a game not using Steam Input API, a quick way to see if it supports simultaneous mouse movement (As Mouse Behavior) and gamepad input is to apply the Gamepad with Mouse Trackpad (or Gyro) template, and simultaneously use the left analog stick and right trackpad.

When a game has no simultaneous input support:

- The games allows you to use only gamepad or only keyboard & mouse.
- When the game detects a new active input type that is different from the current active one, it may ignore the new input until the current one is no longer active or until it adapts to accepting the new input, which can feel like input drops or lag.

When a game has partial simultaneous input support:

- The on screen button prompts automatically switch icons to the active input type, even changing when mouse movement is detected, which is distracting.
- Although mouse movement does not cause button prompts to switch, right analog stick is required for certain interactions. Examples include interacting with an in-game pop-up menu, such as a weapon and item menu wheel, and rotating and zooming in on a character or map in a menu screen.
- Rather than having a single cursor, the game may have implemented separate gamepad cursor and mouse cursor for navigating menus.

As powerful as Controller Settings in Legacy mode is, if you want to utilize gamepad and keyboard & mouse input on your Deck, the way games may handle this situation can result in a less pleasant gameplay experience where you may have to make compromises.

## Controller Settings - With Steam Input API

When developers fully implement SIAPI, you can directly map the game's actions to the Deck's controls using Controller Settings and select developer-made Behaviors for analog controls. This approach is similar to how most computer games allow you to remap the actions' default keyboard bindings to another hotkey, such as changing the crouch action from {Control Key} to {C Key}, and modify the analog stick's or mouse behavior.

When you press a button on your Deck, Steam Input will receive it and relay the assigned game action to the game, whereupon that action is executed.

When SIAPI is implemented fully, Controller Settings may offer the following:

- All of the in-game actions are available for binding in Controller Settings as game actions, so you should not have to rely on binding gamepad buttons and keyboard & mouse keys to create your preferred layout. Even if the developer does not assign all game actions to buttons, you can choose which ones to prioritize. Steam Input has menu Behaviors such as Radial Menu and Touch Menu for storing multiple game actions, and the Steam Deck has buttons on the back for binding extra actions.
  - For example, A FPS game has a 180 degree turn action available for gamepad but not for keyboard & mouse. It also has keyboard hotkeys for accessing character, equipment, skill tree, quest, map, and encyclopedia but only two of these are bound for gamepad. Instead, every useful action and menu should be available as game actions, including those that bring up menu wheels or pop-ups.
- Inclusion of Behavior(s) which enable trackpads and gyro to behave like a physical mouse. The gyro's mouse behavior can be used simultaneously with the analog sticks' joystick behavior and trackpads' mouse behavior.
- Action sets and layers have been created for all of the states that the game can be in, and the game actions and Behaviors are properly associated with the sets that they should be in.
  - For example, suppose *Confirm* and *Cancel* actions are in the Menu action set and *Jump* and *Roll* actions are in the Gameplay set, both of which are bound to [A Button] and [­B Button] buttons. Changing *Confirm* to be the [­B button] and *Cancel* to be the [A button] does not affect button assignments for *Jump* and *Roll*, since they are in different sets.
  - Able to assign different trackpad, analog sticks, and gyro sensitivities for each layer and set.
- The game automatically switches to the appropriate action set or layer when you encounter different gameplay states and in-game pop-up menus.
- Non-analog actions associated with analog triggers, particularly Analog Output Trigger, are available to bind for buttons on a controller. This also allows players to set custom Trigger Threshold Points for Soft Pull commands.
  - For example, *aiming* and *firing* a weapon are usually associated with [L2] and [R2]. Since these actions have only two states, they should also be available as game actions.
- Analog actions associated with the analog triggers should have digital variants available as game actions for other buttons.
  - For example, even for driving games where slowly pressing on the right trigger causes a gradual increase in acceleration, full acceleration (and maybe other levels of acceleration) should be available as a game action.
- Supports button prompt icons in-game for the controllers that are being used.
  - When major controllers with new button glyphs are released such as the PlayStation DualSense, SIAPI can automatically display on screen the new glyphs when they are connected. Developers can choose to have SIAPI handle all button prompt icons, or use custom icons with a fallback to SIAPI's icons for controllers they did not anticipate on supporting, such as the DualSense's monochrome glyphs.

As a couple of side notes:

- Steam Input supports localization so that each game action's descriptions can be available in different languages.
- The game should still have a fallback from SIAPI to regular gamepad input in case you disable Steam Input.
- For the Steam Link Touch Controller, when a game fully implements SIAPI, the layout of controls on the screen will automatically change when different action sets and layers are active.
  Additionally for the Steam Link Touch Controller, button prompts should not change due to mouse movement and clicks (e.g. aiming and firing a weapon).

In short, a game using SIAPI should offer a superset of the gamepad and keyboard & mouse capabilities, where all in-game actions are available in Controller Settings for remapping and are grouped into the proper action sets and layers; gyro and trackpad's mouse behavior can concurrently be used with the analog sticks' joystick behavior; and in-game button prompts matches the active controllers' glyphs.

Examples of games that fully implement SIAPI:

- [No Man's Sky](https://store.steampowered.com/app/275850/)
- [Days Gone](https://store.steampowered.com/app/1259420/)
- [Prey](https://store.steampowered.com/app/480490/)
- [The Long Dark](https://store.steampowered.com/app/305620/)
- [Portal 2](https://store.steampowered.com/app/620/)
- [Euro Truck Simulator 2](https://store.steampowered.com/app/227300/)
- [Okami HD](https://store.steampowered.com/app/587620/)
- [Atari Vault](https://store.steampowered.com/app/400020/)

To learn more about what makes a good input experience for a gamepad and Steam Deck, refer to

- [Steamworks - Getting Started for Developers](https://partner.steamgames.com/doc/features/steam_controller/getting_started_for_devs) Learn more about how a game's input system can work with Steam Input, whether or not SIAPI is being implemented.
- [Steamworks - Steam Input: Getting your game ready for Steam Deck](https://partner.steamgames.com/doc/steamdeck/recommendations) Information on how to ensure a game's input experience works well on Steam Deck.
- [Steamworks News - Steam Input API Adds PS5 Controller Support](https://store.steampowered.com/news/group/4145017/view/2924487488167580235)

## Action Sets and Action Layers - Introduction

Before talking about action sets and action layers, let us first consider what some of the commands on a control for a hypothetical open world game can be.

| **Controller** | **On Foot** | **Vehicle** | **Fishing Mini-game** | **Menu** |
|---|---|---|---|---|
| A | Jump | Boost |  | Select |
| Y | Enter Vehicle | Exit Vehicle |  |  |
| R1 | Throw Grenade | Shoot Weapon |  | Next Menu Tab |
| Right Analog Stick | Camera Control | Camera Control | Camera Control | Cursor Control |

As seen from the table, each control's action changes depending on the state of the game. For example, [R1] button is used to *Throw Grenade*, *Shoot Weapon*, do nothing, and *Next Menu Tab* in four different game states.

Moreover, many games have additional states within a game state.

| **Controller** | **Menu** | **Menu: Map** | **Menu: Inventory** |
|---|---|---|---|
| A | Select | Select | Select |
| Y |  | Detail | Detail |
| R1 | Next Menu Tab | Next Menu Tab | Next Menu Tab |
| Right Analog Stick | Cursor Control | Map Rotation and Tilt | Cursor Control |

When comparing Menu: Map and Menu: Inventory to those in the Menu game state, many actions are shared. For example, the [A] button is used to *Select* in all three states. Another way to describe this relationship is to say that the Menu is the parent game state and Menu: Map and Menu: Inventory are the Menu's child game states.

Using the same idea, in Steam Input:

- Commands and Behaviors that are used in a game state are placed into an action set (parent game state), such as On Foot, Vehicle, Fishing Mini-Game, and Menu.
- When the commands and Behaviors of two or more game states heavily overlap, then a part of those are assigned to an action set (parent game state) and the remainder are assigned to action layers (child game states) of that set, such as Menu (action set), Menu: Map (action layer), and Menu: Inventory (action layer).

Action sets and layers can be created under the Action Sets category in Edit Layout.

### Action Sets

Anytime you modify commands and Behaviors through Controller Settings without being in an action layer, you are changing them in an action set.

When entering View Layout and Edit Layout, the action set appears as follows.

While a layout can include multiple action sets, only one set can be active at a time while playing.

Action sets behave noticeably different depending on whether or not SIAPI is implemented.

When SIAPI is implemented:

- Action sets automatically change depending on the game state. If you are running on foot and then pause to the menu in the hypothetical open world game, then the set will change from On Foot to Menu.
- You are not able to add more action sets. The available sets are determined by the developer.

When SIAPI is not implemented:

- Action sets do not automatically change depending on the game state, since the game is unaware of Steam Input's existence. In order to change between them, you must assign a Change Action Set command in each set.
  - The exception to this is to use the Global Set Options, found in Action Sets category in Edit Layout. A set can change to another if the mouse cursor is being shown or hidden. However, how well this works will vary for each game.
- Your layout starts with an action set called Default (name can be changed), and you can add more sets.

### Action Layers

An Action Layer is similar to an Action Set, except it exists within an action set. It only contains changes in command and Behavior assignments made from its parent set.

When entering View Layout and Edit Layout, the active action layer appears as follows

Not only can there be multiple layers in a set, unlike action sets, more than one can be enabled simultaneously.

Similar to action sets, action layers behave differently depending on whether or not SIAPI is implemented.

When SIAPI is implemented:

- Action layers are automatically applied and removed depending on the game state. If you are bring up a map in-game, then the Menu set with Map layer will be applied.
- You can add as many layers to each set as you like, in addition to the developer made layers.
- All of the game actions available in the action layer are from its parent set.

When SIAPI is not implemented:

- Action layers do not automatically change depending on the game state, since the game is unaware of the existence of Steam Input. You must assign an Add/Remove/Hold Action Set Layer, under the Action Sets category, to each action layer to change between them.
- You can add as many action layers as you like.

When entering View Layout or Edit Layout from within a game, the active action set or layer is displayed.

#### Applying multiple Action Layers

Let us return to the open world scenario, and here are action layers for On Foot:

| **Controller** | **On Foot** | **On Foot: Weapon Wheel** | **On Foot: Weapon Scope** |
|---|---|---|---|
| A | Jump | Jump | Jump |
| Y | Enter Vehicle | Scroll through Weapon Type | Change Bullet Type |
| R1 | Throw Grenade | Throw Grenade | Hold Breath |
| Right Analog Stick | Camera Control | Weapon Selection | Camera Control (reduced sensitivity) |

In an actual game, it makes sense that only one of the above layers is applied at time, but the following is a demonstration of what happens if they are applied in different orders:

| **Controller** | **Weapon Wheel, then Weapon Scope** | **Weapon Scope, then Weapon Wheel** |
|---|---|---|
| A | Jump | Jump |
| Y | Change Bullet Type | Scroll through Weapon Type |
| R1 | Hold Breath | Hold Breath |
| Right Analog Stick | Camera Control (reduced sensitivity) | Weapon Selection |

#### Why use Action Layers?

Suppose you are playing a game that does not support SIAPI, and you are creating your own action sets and layers. If you want to change [D-Pad Up] from *Open Inventory* to *Open Map*.

- If you have a Walking set with an Aim Scope layer, then you would change it in Walking set.
- If you have a Walking set and a separate Aim Scope set, then you would need to change it in both sets.

In short, when multiple states have a large overlap in actions, it is easier to make changes for the former scenario rather than the latter.

## Action Sets and Action Layers - Commands

As mentioned in the previous chapter, in a game with SIAPI, the developer can create multiple Action Sets and Layers and design the game to automatically switch to whichever set and layer as needed depending on the state of the game.

When you create your own Action Sets and Layers, you have to assign Action Set and Layer commands in order to manually switch between sets and layers, since the game is unaware that they exist.

You can find these commands under the Action Sets category.

Before you can use them, first, you must create at least one additional Action Set or Layer.

### Creating Action Sets and Layers

To create an Action Set or Layer, go to the Action Sets category at the bottom of Edit Layout.

- To create an Action Set, select Add Action Set.
  - Note that an Action Set can be only created in a game without SIAPI. In a game with SIAPI, only the developer can create Action Sets.
- To create an Action Layer, select the settings (gear icon) next to the action set that you want the layer to reside in, and then select Add Layer.
  - Note that an Action Layer can be created in a game with or without SIAPI.

In View Layout or Edit Layout, be sure to switch to the desired set or layer first by using the shoulder buttons, [L1] and [R1], before assigning and modifying controls.

### Action Sets commands

There is one action set command:

- Change Action Set - This changes the active action set to another set that you designate.
  - To change between action sets, you should have this command assigned in each action set. For example, if you have Default and another action set called Set 1, then in Default you would have a button that can change to Action Set 1 and in Action Set 1 you would have a button that can change to Default.

### Action Layers commands

There are a few action layer commands:

- Hold Action Layer - The layer is only active while the command is active.
  - This is similar to Mode Shift (explained in a later chapter), except while Mode Shift is used for changing only Behaviors and can only be activated by holding down a single button you designate, an Action Layer can change any control and can be activated by fulfilling a command's activation conditions, such as holding down a Regular or Double Press for a button and activating the Outer Ring Command for analog sticks and trackpads.
- Apply Action Layer - Activating the command will apply a layer that you designate.
  - This is useful for manually apply a layer. For example, if you want to apply a layer called Layer 1 from the default action set, you should assign this command to a control in the default action set and designate the layer of interest to be Layer 1.
- Remove Action Layer - Activating the command will remove the layer that you designate.
  - This is useful for manually remove a layer. For example, if you want to remove a layer called Layer 1 while Layer 1 is active, then you can assign this command to a control in Layer 1 (or the default action set) and designate the layer of interest to be Layer 1.
- Cleared from Parent - This assigns a command that does nothing in the layer.
  - This is useful when you want a control to do nothing in a layer. For example, if the default action set's [L4 grip button] presses the {X button} and it has not been modified in the Layer 1's controls, then when Layer 1 is active, pressing [L4 grip button] will still trigger the {X button}. If you do not want that grip button to do anything while Layer 1 is active, then assign [L4 grip button] in Layer 1 with Cleared from Parent.

I kept the above examples straightforward, but if you are considering having more than one action layer active at the same time, you may have to spend a bit more time considering which controls across each layer (or action set) you should be assigning the Apply and Remove Action Layer as well as Cleared from Parent, especially if you are also considering applying action layers in different orders.

## Behaviors - Introduction

How the D-Pad, Button Pad, Analog Sticks, Trackpads, and Gyro act in-game depend significantly on the Behavior that has been assigned. For example, you can set [Right Trackpad] to use As Mouse, where sliding your thumb across the [Trackpad] moves the mouse cursor, or you can set it to Radial Menu, where moving your thumb on the [Trackpad] brings up a menu of user-defined options.

Here is the list of the Behaviors that are available for each control:

| **Behaviors** | **D-Pad** | **Button Pad** | **Analog Sticks** | **Trackpads** | **Gyro** |
|---|---|---|---|---|---|
| **Directional Pad** | ✔ | ✔ | ✔ | ✔ | ✔ |
| **Button Pad** | ✔ | ✔ |  | ✔ |  |
| **As Mouse** |  |  |  | ✔ | ✔ |
| **As Joystick** |  |  |  | ✔ | ✔ |
| **Joystick** | ✔ | ✔ | ✔ | ✔ | ✔ |
| **Joystick Mouse** |  |  | ✔ |  |  |
| **Flick Stick** |  |  | ✔ | ✔ |  |
| **Scroll Wheel** |  |  | ✔ | ✔ |  |
| **Radial Menu** | ✔ | ✔ | ✔ | ✔ |  |
| **Touch Menu** |  |  | ✔ | ✔ | ✔ |
| **Hotbar Menu** | ✔ |  | ✔ | ✔ |  |
| **Mouse Region** |  |  | ✔ | ✔ | ✔ |
| **Single Button** |  |  |  | ✔ |  |
| **Directional Swipe** |  |  |  | ✔ | ✔ |
| **Gyro to Mouse[Beta]** |  |  |  |  | ✔ |
| **Gyro to Joystick Camera[Beta]** |  |  |  |  | ✔ |
| **Gyro to Joystick Deflection[Beta]** |  |  |  |  | ✔ |

While many Behavior are available for each of the mentioned controls, in practice you will mostly use only a subset of them, with some more frequently used for particular controls. For example, the [A B X Y] will almost always be set to Button Pad Behavior.

Also, anytime you create a Virtual Menu, which is represented by a Radial Menu, Touch Menu, or Hotbar Menu, you will find it in the list of behaviors for the controls mentioned above.

Furthermore, when SIAPI is fully implemented, developers can also create Behaviors. The ones covered in this guide are those that are built into Steam Input.

### Behavior Showcase

The following shows each Behavior with one of the controls that most uses it.

**Directional Pad**

This behaves like a physical D-Pad, and you can assign game actions and commands to each of the cardinal directions.

**Button Pad**

This behaves like a physical button pad, and you can assign game actions and commands to each of the buttons.

**As Mouse**

This behaves like a physical mouse and controls the mouse.

**As Joystick**

This controls the joystick in-game in a way such that it behaves like a physical mouse.

**Joystick**

This behaves like a physical joystick and can control either joysticks or mouse.

**Joystick Mouse**

This behaves like a physical joystick and controls the mouse.

**Scroll Wheel**

This behaves like a physical scroll wheel, and you can assign gamepad, keyboard & mouse, and special inputs to the wheel.

**Mouse Region**

This behaves as if the game's content on the display is mapped to the control's range of movement. For example, Mouse Region can be set such that tapping the right side of the Trackpad moves the cursor to the right side of the display, and tapping just to the left of the Trackpad's center will move the cursor to just to the left screen's center.

**Radial Menu**

This behaves like a menu where the menu items you create are arranged in a circle, and is a type of Virtual Menu.

**Touch Menu**

This behaves like a menu where the menu items you create are arranged in a grid, and is a type of Virtual Menu.

**Hotbar Menu**

This behaves like a menu where the menu items you create are arranged in a row, and is a type of Virtual Menu.

**Single Button**

This behaves as if it is a button.

**Flick Stick**

This behaves like a physical joystick. Conceptualized by Jibb Smart, Flick Stick is a different paradigm for controlling the camera in first and third person games, and it generally works as follows:

1. The 360 degrees rotation of the [analog stick] has a 1 to 1 correlation to the 360 degrees of the in-game camera's horizontal rotation.
2. The [Gyro] handles the in-game camera's vertical rotation as well as horizontal rotation.

Valve has implemented this concept into Steam Input as two parts: Flick Stick Behavior and Gyro Behavior.

For additional information on Flick Stick, visit the creator's blog at [GyroWiki - Good Gyro Controls Part 2: The Flick Stick](http://gyrowiki.jibbsmart.com/blog:good-gyro-controls-part-2:the-flick-stick)[gyrowiki.jibbsmart.com].

**Directional Swipe**

This allows swiping in the cardinal directions to activate menu items.

**Gyro to Mouse [Beta]**
This behaves like a physical mouse and controls the mouse, and renovates the As Mouse Behavior for [Gyro]. It noticeably adds a Dots Per 360 degrees setting for sharing angle calibration with Flick Stick and a multiple different ways to control mouse cursor and camera movement via controller rotation.

**Gyro to Joystick Camera[Beta]**
This behaves a bit like a physical mouse and controls the joystick. It renovates the As Joystick Behavior for [Gyro]. Like Gyro to Mouse, it includes multiple different ways to control mouse cursor and camera movement via controller rotation.

**Gyro to Joystick Deflection[Beta]**
This behaves like a joystick and controls the joystick. This mimics using a wheel in driving and flight simulators.

### How this guide explains Behaviors

Because of how enormous of a topic this is and the varying viability of applying certain Behaviors to specific controls, I will cover the combinations that I think are easy to understand or are intuitive, and if I have the time, I will revisit other combinations in future updates.

As a note, each Behavior has additional settings that can customize the input experience further. Furthermore, the additional settings that are available for a Behavior can change depending on the control. For example, although both the [D-Pad] and a [Trackpad] can be set to use Directional Pad, the [Trackpad] has additional settings to allow emulation of joystick-style movement via Analog Emulation.

## Behaviors - Virtual Menus

Before discussing the various combinations of Behaviors and controls, let us talk a bit about Virtual Menu. In Steam Input, a Virtual Menu is an interactive menu that is filled with menu items you have assigned to it, and there are three types:

- Radial Menu
- Touch Menu
- Hotbar Menu

The three differ from each other by how they appear on screen and the interaction needed to activate the buttons. Otherwise, they all offer a convenient way to access a multitude of commands with a single control.

A Virtual Menu is particularly useful for games that have multiple UI interactions or have more actions that need to be used than there are buttons on a controller. Common examples include:

- Access various in-game menus such as *Map*, *Inventory*, *Quest objectives*, *Crafting*, *Character Stats*, *Civilization Management*, etc.
- In MMO games, use ability hotkeys which can number in the dozens, such as 4 rows with 13 abilities each, and various in-game menus.

### Creating a Virtual Menu

There are two ways to create a Virtual Menu:

- From the list of Behaviors under a control, select one of the Virtual Menu types and give it a name. The new menu is immediately associated with that control.
- Add a Virtual Menu in Edit Layout, give it a name, and select the menu type that you want. The new menu is not associated with any control.

### Editing a Virtual Menu

There are two ways to edit a Virtual Menu:

- For a menu that has been associated with a control, you can edit that menu by going to that control's settings and using the gear icon next to the menu.
- For all menus, regardless if they have been associated with controls or not, you can find and edit them created by using the pencil icons next to them under the Virtual Menus section in Edit Layout.

Note that for any Virtual Menu that you create, you can assign and reassign it to any control that supports that menu type by selecting it from the list of Behaviors.

### Assigning commands to menu buttons

After you create a Virtual Menu with your preferred menu type, you can populate the menu buttons as desired.

If you want to change menu type, use Menu Type under the Commands section. If you want to rearrange the order of the menu buttons after assigning commands, use Reorder Menu Inputs.

### Customizing Virtual Menu appearance

The Virtual Menu's position and appearance can be changed in Onscreen Display:

- Menu Horizontal/Vertical Position - Determines the horizontal/vertical position of the menu. The values of 0 and 100 correspond to the left and right edges for Horizontal Position, and the top and bottom edges for Vertical Position.
- Menu Size - Determines how large the menu.
- Menu Opacity - Determines how transparent the menu is.

The menu buttons' appearance can also be customized by selecting and coloring their glyphs.

As mentioned before, the commands can be renamed by selecting the gear icon next to the command, and the assigned name will appear in the Virtual Menu on screen.

More details on the specific menu types are explained later in this guide.

## Trackpads - As Mouse

As Mouse Behavior allows you to control the cursor by moving your finger across the trackpad.

If you have never used the Steam Deck, Steam Controller, Steam Link Touch Controller, or mobile game input, it is to be expected that using the trackpads to control the cursor in a game will feel strange the first time you try it. Just as there is a learning curve to using analog sticks or a mouse, it will also take time to familiarize yourself with using the Deck's trackpads in games. The payoff though is that any handheld gaming experience that revolves around using a cursor, where having greater speed and accuracy can be beneficial, may be improved by using As Mouse on the trackpad.

### Using As Mouse with trackpad

If you are using As Mouse on the trackpad for the first time, I recommend starting with a slower pace game that does not place you into situations that require quick reactions before jumping into quicker pace ones. Similar to how you develop habits for what you think is the best way to use analog sticks, over time you will also develop a better understanding to using the trackpads in games.

### Together with Gyro using As Mouse

Having said all of that, anytime you want to control a camera or cursor, it would be amiss to not mention an important complement, the gyro. To gain even more speed and more control over the cursor than what is possible with the trackpad (or analog stick) alone, gyro should be enabled and set to As Mouse.

When paired together, as a general advice you should use the trackpad for large movements and the gyro for smaller movements. For example, to aim at a target in a first person shooter:

1. Quickly swipe across the trackpad to point your weapon in the vicinity of the target. Your aim does not have to be directly on the target.
2. Using the gyro by rotating the Steam Deck, fine-tune your aim until it is over the target.

> If you want fast and precise control over the cursor in a game without SIAPI, consider setting the trackpad and gyro to As Mouse Behavior. As a guideline, the trackpad should be used for large camera or cursor movements and the gyro for smaller movements.

### Settings to note

#### Adjusting Sensitivity

When you start a game and move the camera or cursor, you may find its speed to be either too fast or too slow. In that case, you can change its speed by adjusting the Sensitivity found in General.

Note:

- If the game implements SIAPI, then the camera sensitivity should depend on only As Mouse's Sensitivity.
- If the game does not implement SIAPI, then the camera sensitivity is dependent on both As Mouse's Sensitivity and the in-game option's mouse sensitivity.

For first/third person games, a good start for adjusting Sensitivity is to have a swipe across the trackpad, without lifting your thumb, consistently rotate the camera horizontally to some value between 60 and 180 degrees, and then change it as needed.

#### Rotating the camera horizontally beyond the trackpad's area

If you are new to using the trackpad, you may find yourself feeling limited by the trackpad's size when trying to rotate the camera horizontally in-game. Here are some of the ways to resolve that in the following order:

- If you have not already, adjust the Sensitivity higher.
- If you think you have adjusted the Sensitivity setting high enough, then try setting Gyro to As Mouse as well. Use the trackpad for large movements and the gyro for fine-tuning your aim.
- Trackball Mode in Trackpad is enabled by default. By swiping across the trackpad while lifting your thumb off, the mouse cursor in-game will move while slowing down over time, similar to how a trackball behaves.
  - Trackball Friction determines how quickly the cursor stops moving after swiping at the trackpad while lifting your thumb off, and by default it is set to Medium.
- When using Acceleration, the faster you move your thumb across the trackpad, the higher the Mouse sensitivity becomes.
- When Edge Spin is enabled, placing your thumb along the edge of the trackpad causes continuous cursor movement to be output towards that direction, similar to pushing an analog stick.
  - To enable Edge Spin, Edge Spin Speed must be set higher than 0. To adjust how close your thumb has to be to the edge of the trackpad for Edge Spin to activate, adjust the Edge Spin Radius.

#### Consistent horizontal cursor movement

The Rotation setting under Output determines the angle at which your thumb swipe across the trackpad is translated to a purely horizontal cursor movement across the screen, ranging from -90 degrees (clockwise) and 90 degrees (counter clockwise). You may consider adjusting this to your preferred swiping angle.

If you are still having issues with horizontal cursor movement, here are a couple of other settings to look at in the following order:

- If you are using Trackball Mode, try adjusting Friction Vertical Scale higher, such as 150. As the cursor moves after you swipe at the trackpad, Friction Vertical Scale determines how quickly the vertical movement of the cursor slows down compared to the horizontal movement. Setting this higher will reduce the trackball's vertical movement, which can be helpful when intending to quickly spin the camera horizontally.
- Sensitivity Vertical Scale under General determines how sensitive vertical movement is relative to horizontal movement as you move your thumb across the pad. Adjusting this lower will decrease the vertical movement relative to horizontal movement.

If you are changing the above two settings in a game that does not support SIAPI, do note that these changes applies everywhere in the game, unless you have created a separate action set to adjust them in. While not as much as an issue for Friction Vertical Scale, having reduced Sensitivity Vertical Scale may feel unusual in some scenarios such as navigating menus. For games using SIAPI, if the developer has created a separate in-game action set, this is not an issue.

#### Reducing cursor movement while pressing the triggers

If you find that pressing the triggers is causing undesired cursor movement while your thumb is on the trackpad, you can try using Trigger Press Mouse Dampening in Trigger Dampening. This allows you to set up conditions for reducing the cursor sensitivity when using the trigger; Trigger Press Mouse Dampening (Value) determines the amount by which the sensitivity is reduced.

Enabling this may have unintended effects such as being unable to shoot and track a moving target simultaneously in a shooting game as well as being unable to click, drag, and drop items in an inventory menu with the trackpad. In that case, you should supplement this by setting gyro to As Mouse so that you can still control the cursor normally as the trackpad's sensitivity is reduced.

## Trackpads - As Joystick - Part 1

When moving your finger across the trackpads, As Joystick feels a bit similar to controlling a mouse, even though Steam Input is actually outputting joystick movement to the game. The magnitude of the output depends on how fast you swipe across the trackpads, and when moving above a certain speed, the output will be at, or close to, maximum.

For games that do not support simultaneous gyro/trackpad in mouse mode for camera/cursor control and gamepad controls for movement, this can be useful when you desire a mouse-like experience on the trackpad but do not want to use a keyboard & mouse only layout.

### Comparison of As Mouse and As Joystick

While it is impressive in how it mimics a mouse, As Joystick does feel different from As Mouse in ways that limits it from being a complete substitute, some reasons which include:

- The techniques that game developers employ to make analog sticks feel good to use can make it difficult to replicate a mouse-like experience on a trackpad.
- Camera rotation speed via analog sticks is far slower than what can be done with a mouse.

These discrepancies can result in unexpected responses when using As Joystick which are not experienced when using As Mouse, including reduced sensitivity to diagonal swipes and unintended camera acceleration.

Due to having to output joystick movement, there are limitations to what As Joystick can do.

- At above a certain swiping speed, the Behavior outputs the maximum joystick stick movement. This means quick changes to the camera's rotation is not possible.
  - When using As Mouse with mouse acceleration disabled in the game and in Controller Settings, movement across the trackpad is linearly correlated to camera. Swiping across the trackpad in 0.1 seconds compared to 1 second should have no difference in the amount of camera rotation.
  - Consider how much less the camera rotates when pushing an analog stick to the right for 0.1 seconds and when pushed for 1 second. The non-zero difference between the two applies to As Joystick too.

In short, due to the differences between analog stick input and mouse input, whether they are from physical characteristics or intended by the developer's design, there are limits to how closely As Joystick can recreate a mouse-like experience on a trackpad, and calibrating it to do so involves a non-trivial number of steps that is likely to still fall short of it. The best mouse experience on [Trackpads] and [Gyro] is to use As Mouse, but if you want to use only gamepad input and have a mouse-like experience on the trackpads, as a workaround As Joystick is the next best thing.

Similar to As Mouse, As Joystick should be assigned to the trackpad and gyro if you want quick and accurate control over the gamepad cursor.

### Settings to note

There are three As Joystick settings that heavily influence the mouse-like behavior on the trackpad: Minimum Joystick X Output Value, Minimum Joystick Y Output Value, and Enhance Small Movement Precision. I will refer to the first two together as Minimum Joystick X/Y Output for short.

#### Minimum Joystick X/Y Output Value behavior

If you are following along this guide, set Enhance Small Movement Precision to 100, since explaining Minimum Joystick X/Y Output is difficult unless Enhance Small Movement Precision is ignored. If you are familiar with this setting from the older version of Big Picture Mode (BPM), note that 0 to 100 in old BPM's Controller Configuration is equivalent to 100 to 1 in Steam Deck UI's Controller Settings (values are reversed).

With a range between 0 and 20,000, Minimum Joystick X/Y Output determines the smallest joystick output which corresponds to the slowest swipe across the trackpad (only true when Enhance Small Movement Precision is 100) in the horizontal/vertical direction. As you move your thumb faster, the joystick output increases from Minimum Joystick X/Y Output to a higher value, up to a maximum of 32,767.

These settings should be set to at least the size of the game's joystick deadzone, which typically lies between 3,000 and 12,000 for games that I have played; any lower and the game will ignore a slow swipe. To consistently determine a deadzone's size, refer to Calibration below.

That said, if you set Minimum Joystick X/Y Output to the size of the deadzone and swipe the trackpad, almost always the cursor moves too slow. As mentioned before, most games' default analog stick sensitivity feels fine when using analog sticks, but is too low for a a good mouse-like experience on a trackpad. There are two solutions to this:

1. Adjust the in-game analog stick sensitivity to a high or maximum value. While this results in a much better As Joystick experience, this change typically affects any external controller that is connected to the game.
2. Set Minimum Joystick X/Y Output higher than the deadzone size, and you should correspondingly set Enhance Small Movement Precision to a value that is not 100.

To understand the second suggestion, let us examine the example above where Enhance Small Movement Precision is set to 100 and Minimum Joystick X/Y Output is set to its highest, and the game's deadzone is about 4,900. Notice how the camera jerks while slowly swiping across the trackpad, and this is because the joystick output is constantly alternating between the output of 0 and 20,000. The higher the value above the deadzone's size, the more noticeable this effect becomes (and this can be observed as well if gyro is set to As Joystick).

How does Enhance Small Movement Precision resolve this problem, and more importantly, what should it be set to after you specify Minimum Joystick X/Y Output? This brings us to our next topic.

#### Enhance Small Movement Precision behavior

Enhance Small Movement Precision has a couple of observable effects when set to any value that is not 100.

- When swiping across the trackpad, the joystick output smoothly transitions between 0 output to some higher value. This is in contrast to when Enhance Small Movement Precision is set to 100, where swiping will first cause joystick output to jump from 0 to the Minimum Joystick X/Y Output before gradually increasing to some higher value.
  - When slowly swiping, the output smoothly changes to some value between 0 and the Minimum Joystick X/Y Output. The lower the Enhance Small Movement Precision, the closer the output is to Minimum Joystick X/Y Output during a slow swipe. This can observed by using a Steam Controller to play a game in Big Picture Mode and using Toggle Controller HUD in the overlay.
- At any value, the output of the analog stick randomly swings between 0 and the Minimum Joystick X/Y Output when placing your thumb still on the trackpad.
  Here is a comparison while setting the Minimum Joystick X/Y Output to maximum.

To reemphasize, if Minimum Joystick X/Y Output is set to the size of the deadzone:

- When Enhance Small Movement Precision is set to 100, a slow swipe across the trackpad causes the analog stick output to be the same as the Minimum Joystick X/Y Output.
- When Enhance Small Movement Precision is lower than 100, a very slow swipe across the trackpad can cause the analog stick output to lie within the deadzone area.

## Trackpads - As Joystick - Part 2

### Determining Minimum Joystick X/Y Output Value and Enhance Small Movement Precision

To put it simpler, for any given Minimum Joystick X/Y Output Value, what should Enhance Small Movement Precision be such that you benefit from smooth camera rotation without outputting joystick values within the deadzone?

> After finding the size of the game's deadzone and adjusting Minimum Joystick X/Y Output to what you prefer, try setting Enhance Small Movement Precision to 100 - 99*Sqrt(Game's Deadzone Size/Minimum Joystick X Value).

This is based on my observation that when set to the smallest value, Enhance Small Movement Precision causes the joystick output to wildly swing between 0 and the Minimum Joystick X/Y Output when the thumb is absolutely still on the trackpad. When you determine the game's deadzone size and set the Minimum Joystick X/Y Output, the above equation causes the output to wildly swing to the size of the deadzone area. The result should be that when you slowly swipe the trackpad, joystick output is less likely within the deadzone.

### Calibration

Here are the overall steps to adjusting the As Joystick.

1. Enter the in-game controller options and reduce the effects of the various analog stick options that can lead to un-mouse like behavior on a trackpad. However, if you plan on connecting external controllers, whether it is for local play or Remote Play session, then skip this step.
2. Find the size of the analog stick's deadzone through Controller Settings.
3. Apply the deadzone sizes to As Joystick's Minimum Joystick X/Y Output Value.
4. If trackpad's sensitivity feels too low from the slow and medium swipes, set Minimum Joystick X/Y Output higher and correspondingly adjust Enhance Small Movement Precision.
5. Adjust Sensitivity Vertical Scale and Custom Response Curve in As Joystick as needed to further reduce un-mouse like behavior.

#### Adjust in-game controller options

If you are not going to connect controllers to the Deck, whether for local play or Remote Play session, then go into the in-game controller options and adjust any analog stick options that cause un-mouse like behavior.

- Increase the analog stick sensitivity to the max. This can be reduced later if needed.
- Reduce the deadzone size to as small as possible.
- Set deadzone shape to circular.
- Set curve response to linear.

There may be more in-game options than the one I listed, so you will need to change those as well.

#### Find game's deadzone for analog sticks

Each game has a different deadzone for analog sticks, mostly ranging between 3000 to 12000. For proper calibration, you will need to find this value through Controller Settings. There are two methods:

- If the deadzone shape is the same along the horizontal and vertical axis (e.g. circle, square, cross), then the deadzone size can be found through As Joystick Behavior or Joystick Behavior.
- If the deadzone shape is different along the axes (e.g. oval, rectangle), then the deadzone size can be found through Joystick Behavior (or As Joystick if if you do not care too much).

##### Find deadzone size through As Joystick

If the deadzone shape is the same along the axes, set right trackpad's Behavior to As Joystick:

1. Set Minimum Joystick X/Y Output to 8000.
2. Set Enhance Small Movement Precision to 1.
3. Return to the game so that you have control of the camera.
4. Place your thumb on the trackpad and do not move your thumb.
  - There absolutely must be no movement on the thumb (i.e. do not roll your thumb on the trackpad). If not done correctly, the camera will rotate consistently in one direction.
  - If there is random camera movement, decrease Minimum Joystick X/Y Output by 500 to 1000.
  - If there is no random camera movement, increase Minimum Joystick X/Y Output by 500 to 1000.
5. Repeat the previous step until the camera barely moves.
6. Set Enhance Small Movement Precision to 100.

The value you found for Minimum Joystick X/Y Output is a good approximation of the size of the deadzone.

##### Find deadzone size through Joystick

If the deadzone shape is different along the axes:

1. For the right analog stick, set the Behavior to Joystick with Output Joystick set to Right Joystick
2. Set Output Axis to Horizontal Only.
3. Reduce Horizontal Scale to 25.
4. Return to the game and move the analog stick exactly left or right.
  - If there is camera rotation, decrease Horizontal Scale by 1 to 5.
  - If there is no camera rotation, increase Horizontal Scale by 1 to 5.
5. Repeat the previous step until the camera barely moves.
6. Note down the value of Horizontal Scale.
7. Reset Horizontal Scale to max.
8. If the deadzone is different along the vertical axis, repeat all the steps again starting from Step 2 for the vertical axis.
9. Set Output Axis to Both Horizontal & Vertical.

The values you find are a good approximations of the relative size of the deadzone along the horizontal (and vertical axis).

#### Apply Deadzone Size to As Joystick's Minimum Joystick X/Y Output Value

If you found the deadzone size through As Joystick, then you are already done with this part.

If you found the deadzone size through Joystick, assign the value(s) you found for Horizontal/Vertical Scale to Minimum Joystick X/Y Output

1. For the right trackpad, set the Behavior to As Joystick
2. Set Minimum Joystick X Output Value to Horizontal Scale/100 * 32,767
3. Set Minimum Joystick Y Output Value to Vertical Scale/100 * 32,767
4. Set Enhance Small Movement Precision to 100

#### Test trackpad sensitivity

Move your thumb across the trackpad at varying speeds (recall that high speed swipes do not work like it does in As Mouse so avoid those).

- If you feel the sensitivity is too high, which will likely only happen if you adjusted the in-game analog stick sensitivity:
  1. Lower analog stick's sensitivity in-game until you're satisfied.
  2. Set Enhance Small Movement Precision to 1.
- If you feel the sensitivity is just fine:
  1. Set Enhance Small Movement Precision to 1.
- If you feel the sensitivity is too low:
  1. Increase Minimum Joystick X/Y Output, such as by 1000 higher. Test again and readjust until you are satisfied.
  2. Set Enhance Small Movement Precision to about 100 - 99*Sqrt(Deadzone Size/Minimum Joystick X Value).
    - For example, if Deadzone Size is 8192 and you prefer Minimum Joystick X Value to be 12,000, then 100 - 99*Sqrt(8192/12,000) is about 18.
    - For example, if Deadzone Size is 6553 and you prefer Minimum Joystick X Value to be 15,000, then 100 - 99*Sqrt(6553/13,000) is about 34.

## Trackpads - Scroll Wheel

This Behavior acts like a scrollwheel, where a swipe across the trackpad causes commands to repeatedly activate.

This is useful when you want to repeatedly trigger certain actions in a relatively controlled manner. Common examples include zooming in and out of a map and scrolling up and down through text.

### Swipe Direction and Commands

There are two ways to create commands.

- Clockwise/Counter Clockwise Commands consist of one binding each.
  - Clockwise command is repeatedly activated when going in the clockwise direction.
  - Counter Clockwise command is repeatedly activated when going in the counter clockwise direction.
- Scroll Wheel List can store up to 10 commands, and the commands are sequentially activated based on their order in the list and the direction of the swipe.
  - In the Clockwise direction, bindings are activated in an ascending order.
  - In the Counter Clockwise direction, bindings are activated in an descending order.

Note that if you have bindings in both Clockwise/Counter Clockwise Commands and Scroll Wheel List # Command, and you attempt a swipe, then only the ones in the Scroll Wheel List will activate.

There are three swipe directions on the trackpad for repeatedly activating bindings:

- Circular swipe can activate anywhere on the trackpad as long as your thumb moves around the center of the trackpad.
  - Clockwise direction is a clockwise swipe.
  - Counter Clockwise direction is a counterclockwise swipe.
- Horizontal swipe can activate from anywhere on the trackpad.
  - Clockwise direction is a swipe to the right.
  - Counter Clockwise direction is a swipe to the left.
- Vertical swipe can activate from anywhere on the trackpad.
  - Clockwise direction is a swipe down.
  - Counter Clockwise direction is a swipe up.

## Trackpads - Mouse Region

Mouse Region sets the entire surface of the trackpad such that any thumb movement on it has a 1 to 1 correlation to a cursor within a region on the screen that you have designated. Placing your thumb on a specific position on the trackpad and moving it will place the cursor in the corresponding location within that region and be moved in the same manner.

This can be useful for more responsive turns in twin stick shooters, where the region is set to the entire screen, and when you want to interact with a specific area on the screen which can be the case for an inventory in point-and-click adventure games and a map in a strategy game, in which case you set the region to a specific area on the screen.

### Settings to note

#### Changing the Region's Shape, Size, and Position

With the default settings, the Behavior's region on the screen is the same shape as the trackpad, which is a square for the Steam Deck (and a circle for the Steam Controller), and it is centered around the middle of the screen. It is large enough such that the left and right edges of the trackpad correspond the the left and right edges of the screen.

To customize the shape, size, and position of the region, they can be adjusted in Onscreen Display as follows:

- Region Size - Determines the general size of the region.
- Horizontal/Vertical Scale - Change these two to affect the aspect ratio of the region.
- Region Horizontal/Vertical Position - Sets the position around which the region is centered on. The values of 0 and 100 correspond to the left and right edges for Horizontal Position, and the top and bottom edges for Vertical Position.

#### Changing position when using and not using Mouse Region

Given the variety of scenarios where Mouse Region is useful, you will likely want to impose certain conditions on the cursor when using and not using Mouse Region. For these cases, there are two settings in General that are worth looking at:

- Snap Cursor on Activation - Causes the cursor to snap to the center of the region when a Mouse Region with this setting becomes active after a change in the layout via a mode-shift, action layer, or action set. For example, if the As Mouse on the right trackpad changes to Mouse Region via the mentioned methods.
- Return Cursor on Deactivation - Causes the cursor to snap to the center of the region when you stop touching the trackpad or when a Mouse Region with this setting becomes inactive after a change in the layout via a mode-shift, action layer, or action set. For example, if the Mouse Region on the right trackpad changes to As Mouse via the mentioned methods.

For a bit more context on how to use those two settings, here are a couple of examples:

- When playing an isometric game with an interactable action bar, you may want to use As Mouse for everything in the game, except for the action bar where you use Mouse Region. In this case, you can set the right trackpad to use As Mouse, and when a button is held down to Hold an Action Layer, the right trackpad changes to Mouse Region where its region overlaps the action bar. Upon releasing the grip button, the right trackpad returns to being As Mouse.
  - When the trackpad becomes set to Mouse Region, it is preferable for the cursor to automatically jump to the action bar, and when the trackpad returns to being a Mouse, the cursor returns to its previous position prior to the change to the trackpad.
  - In this case, set both Snap Cursor on Activation to off and Return Cursor on Deactivation to on.
    In this example, I set Vertical Scale to 0 so that the cursor moves only horizontally.
- If the player is playing a top-down, twin-stick shooter and is constantly using Mouse Region, then the player may prefer that the cursor would not jump to the center of the region at any time.
  - In this case, set both Snap Cursor on Activation and Return Cursor on Deactivation to off.

## Trackpads - Radial Menu (Virtual Menu)

As a type of Virtual Menu, Radial Menu is a customizable menu where upon touching the touchpad, a radial arrangement of menu buttons is presented on the screen, and selecting a menu item activates its corresponding command.

### Using Radial Menu on trackpad

The arrangement of the items in the Radial menu are mapped in the same manner to the surface of the trackpad. To select a menu button on screen, move your thumb to the corresponding position on the trackpad.

### Number of menu items and their arrangement in Radial Menu

Radial Menu can be filled with up to 20 menu items, and the number of menu items that appears on screen is determined by the number of menu items you assign commands to.

A setting to note is the Radial Menu Button Type under the General section which determines how you activate a menu button when highlighting it:

- Click - Activates upon the user clicking down the trackpad.
- Release - Activates after the user clicks down on the trackpad and then releases.
- Touch Release - Without having to click, activates after the user lifts their thumb off of the trackpad or when the user uses mode-shift or switches action layers.
- Continuous - Activates immediately and the command remains active until the user stops highlighting the item.

Besides the Radial Menu Buttons, there are two more commands that can be assigned:

- Click - Click the trackpad and to trigger the command (as long as the command's activation conditions are also cleared). This is independent of the Radial Menu Buttons.
- Touch - Touch the trackpad to trigger the command (as long as the command's activation conditions are also cleared). This is independent of the Radial Menu Buttons.

Both settings can have commands associated to them and can be used in-game at the same time with the Radial Menu Buttons.

## Trackpads - Touch Menu (Virtual Menu)

As a type of Virtual Menu, Touch Menu is a customizable menu where upon touching the touchpad, a grid-like arrangement of menu buttons is presented on the screen, and selecting one of them activates its corresponding command.

### Using Touch Menu on trackpad

The arrangement of the items in the Touch menu are mapped in the same manner to the surface of the trackpad. For example, if Menu Button 1 is the menu's top-left button, then touching the top-left corner of the trackpad will highlight Menu Button 1.

### Number of menu buttons and their arrangement in Touch Menu

Touch Menu can be filled with up to 16 menu items. By default, the number of menu buttons on screen is equal to the number of buttons that you create in the settings.

Unlike Radial Menu, you can also manually specify the number of buttons to appear by using the Touch Menu Button Count. For example, if you were set it to 2 buttons, no matter how many more buttons you assign commands with, only 2 buttons will show on screen when the Touch Menu is invoked.

Note that the position of a menu item in the Touch Menu is determined by its Touch Menu Button number. This also means that if you skip certain menu buttons while assigning bindings, which can happen if you specify the Touch Menu Button Count to not be Same As Command Count, the corresponding button in the Touch Menu will appear on screen as blank.

The other setting of interest is the Touch Menu Activation Style. When a menu item is highlighted,

- Click
- Release
- Touch Release
- Continuous

Similar to the Radial Menu Buttons, there are also Touch Menu Buttons:

- Click
- Touch

Both settings can have commands associated to them and be used in-game at the same time with the Touch Menu Buttons.

## Trackpads - Single Button

The entire trackpad behaves as though it is a button.

This can be useful when you want to bind a simple interaction.

### Types of activation

There are two ways for the button to activate:

- Click - Click the trackpad and to trigger the command (as long as the command's activation conditions are also cleared).
- Touch - Touch the trackpad to trigger the command (as long as the command's activation conditions are also cleared).

Both settings can have commands associated to them and can be used in-game at the same time.

## Trackpads - Directional Swipe

Directional Swipe allows you to set up a customizable menu, consisting of 4 menu items, where swiping up, down, left, or right at any position on the trackpad can activate a command (as long as the command's activation conditions are cleared).

This is useful whenever you want to quickly access in-game actions, such as different menu shortcuts.

### Using Directional Swipes

The condition for a menu item activating is based on the distance travelled starting from the contact point on the trackpad, which can be adjusted via the Sensitivity setting. The higher the value, the less distance needed for activation.

By default, once a command has been activated, continuing the same swipe in the same direction will not activate it again. To invoke it again, you either have to swipe in a different direction or lift your thumb off of the trackpad and then swipe at the trackpad again. This can be changed by enabling the Scroll Wheel Mode.

When turned on, moving your thumb in the same direction will repeatedly activate the same command. Furthermore, swiping your thumb at the trackpad while lifting it up will also cause the binding to repeatedly fire, reminiscent of how a cursor can keep moving when Trackball Mode is enabled for Mouse Behavior.

Lastly, you can also assign a Click command.

## Gyro - As Mouse

As Mouse enables you to control the mouse cursor by rotating the Steam Deck.

This is useful in scenarios where quick navigation and manipulation of UI elements as well as fast and accurate camera control is desired, amongst others.

### Using As Mouse with trackpad

If you have never used a gyro-supported device for gaming, using the gyro to control the camera or cursor may feel strange the first time you try it, but once you understand it, it becomes a handy feature in many types of games, whether you are using it with the trackpads or analog sticks.

While you can rotate the Deck, or a controller, in any way to activate the gyro, ultimately each one can be thought of as a combination of simple rotations that go about three axes.

- Pitch - This moves the cursor or rotates the camera up and down.
- Roll - This moves the cursor or rotates the camera left and right.
- Yaw - This can also move the cursor or rotate the camera left and right.

While Steam Input always considers rotations about the pitch axis to be vertical rotation in game, in the Gyro Turning Axis setting found under the Gyro category in As Mouse settings, you can designate how you want horizontal camera rotation handled. It can be Yaw, Roll, or Combined Yaw & Roll. As the latter option's name suggests, you can rotate about the yaw or roll axis and the camera in-game will rotate horizontally.

For a more technical discussion about gyro turning axis, visit Jibb Smart's blog [GyroWiki - Player Space Gyro (and Alternatives) Explained](http://gyrowiki.jibbsmart.com/blog:player-space-gyro-and-alternatives-explained)[gyrowiki.jibbsmart.com].

### Settings to note

#### Adjusting Sensitivity

When you start a game and move the camera or cursor, you may find its speed to be either too fast or too slow. In that case, you can change its speed by adjusting the Sensitivity found in General.

Note:

- If the game implements SIAPI, then the camera sensitivity should depend on only As Mouse's Sensitivity.
- If the game does not implement SIAPI, then the camera sensitivity is dependent on both As Mouse's Sensitivity and the in-game option's mouse sensitivity.

Compared to the Sensitivity's entire range, usually gyro's Sensitivity is not set too differently from the trackpad that is also set to As Mouse. It should be high enough such that you can rotate the Deck to move the camera or cursor by the amount that you want without making it difficult to view the game's content on the display.

#### Gyro activation conditions

You can set the conditions under which gyro turns on by adjusting the Gyro Enable Button and Button Behavior.

- Gyro Enable Button - Determines the button and type of interaction needed to cause the Button Behavior to activate, such as Right Pad Touch, Left Trigger Soft Pull, and Always On.
- Button Behavior - Dictates whether interacting with the button will cause the gyro to turn on, turn off, or toggle.

By default, the Gyro Enable Button is Right Stick or Right Pad Touch and the Button Behavior is On. Because the Steam Deck is equipped with capacitive touch analog sticks and trackpads, this combination allows you to use the Deck's gyro when your thumb is on the right analog stick or trackpad, and readjust the orientation of the device by lifting your thumb off of it. If a game only allows you to shoot while holding down [L2] for aiming, you can try setting Gyro Enable Button to the Left Trigger, instead.

#### Smoothing

Compared to using As Mouse with trackpad, Smoothing is perhaps a more relevant setting if you don't find gyro aiming to be as smooth. This is worth considering adjusting a bit higher than the default.

## Gyro - As Joystick

This Behavior allows you to control the gamepad cursor by rotating the Steam Deck.

For games that do not support simultaneous gyro/trackpad in mouse mode for camera/cursor control and gamepad controls for movement, this can be useful for players who still desire a mouse-like experience on the gyro but do not want to use a keyboard & mouse only layout. This is usually paired with the trackpad set to As Joystick or analog stick set to Joystick.

### Using Mouse Joystick with trackpad

As described in Trackpad - As Joystick Part 1, there is only so much that can be done to make a game's analog stick behave like a mouse, which means that using gyro set to As Joystick will not feel quite as natural compared to As Mouse or a camera (mouse) Behavior created by the developer. Be sure to set a good Minimum Joystick X/Y Output Value and Enhance Small Movement Precision values, or else small gyro movements might not smoothly translate to gamepad cursor movement.

If you are not planning on playing the game with an external controller, then it would be very helpful to adjust the in-game controller options to minimize any joystick behavior that would contradict a good mouse-like experience on the gyro, as described in Trackpad - As Joystick Part 2.

### Settings to note

#### Adjusting cursor speed

Refer to the Calibration section found in Trackpad - As Joystick chapters for learning more about assigning Minimum Joystick X/Y Output and Enhance Small Movement Precision values.

When used together with a trackpad that is set to As Joystick, the Gyro Camera Scale setting will adjust the relative input of the gyro to be less or greater.

#### Gyro activation conditions

Just as it is for the As Mouse Behavior, you can control the conditions under which gyro turns on and off by adjusting the Gyro Enable Button and Button Behavior.

By default, the Gyro Enable Button is Right Pad Touch and the Button Behavior is On.

## Joysticks - Directional Pad

Any gamepad, keyboard & mouse, and special inputs can be assigned to each of the cardinal directions.

A common usage for this is to set {WASD} for movement in first/third person games when you are creating a keyboard & mouse layout, or assign them with {arrow keys} for panning an isometric camera in games that do not have gamepad support.

### Settings to note

#### Defining the layout

The first setting to note is Layout which determines how the four bindings will activate when you push the analog stick:

- 8 way (overlap): A pie-shaped layout where the eight pie pieces correspond to the cardinal and diagonal directions; pressing a diagonal direction activates two of the cardinal directions.
- 4 way (no overlap): A pie-shaped layout, except with diagonal directions disabled. Instead, pressing a diagonal direction will trigger the nearest cardinal direction. This is useful if you decide to assign bindings where you only need one of them to activate at any time, such as shortcuts to menus.
- Analog Emulation: This attempts to modify the output of Directional Pad to simulate analog output.
  - This can be useful if you want to create a keyboard & mouse only layout but still smoothly transition between no character or isometric camera movement to maximum movement.
  - It works as follow:
    1. When analog stick is at neutral position, no command is triggered.
    2. When analog stick is deflected above the Deadzone value, the corresponding command pulses at a specified time interval and duration, which would ideally correspond to a consistent, smooth movement in-game at a speed that is less than the maximum speed.
    3. When analog stick is fully deflected, the binding remains active; thus, the speed is at maximum.
  - Analog Emulation Pulse Time and Analog Emulation Active %: Together, they determine the time interval and duration of each pulse. For example, if Analog Emulation Pulse Time is set to 100 milliseconds, or 0.1 seconds, and Analog Emulation Active % is set to 20, then the pulses occur in 0.1 second intervals with each one lasting for .02 seconds (0.1 x 0.2 = 0..02), or 20 milliseconds. How good the in-game results are depend on the values you set and how the game handles rapid movement input.
- Crossgate: A cross-shaped layout that emphasizes the cardinal directions over the diagonal directions.

Additionally, Deadzone specifies the circular region where any analog stick movement within it will not be output to the game.

#### Outer Ring Command

The Outer Ring Command is invoked when you deflect the analog stick beyond the Command Radius (and having satisfied the command's activation conditions), where maximum joystick output is 32,767. A common example for this is when a game uses {WASD} for regular movement and holding {Shift} for sprinting. To allow your character to move at a regular speed when tilting the stick moderately and sprint when pushed further:

- Bind {WASD} to the Directional Pad's directions
- Assign {Shift} to the Outer Ring Command

Alternatively, Command Invert can be toggled such that the Outer Ring Command is invoked when the analog stick is within the Outer Ring Binding Radius. This is useful when a game uses {WASD} for regular movement and holding {Alt} for walking.
To allow your character to walk when tilting the stick moderately and move normally when pushed further:

- Bind {WASD} to the Directional Pad's directions
- Assign {Alt} to the Outer Ring Command
- Toggle Command Invert to On

#### Haptics Intensity Override

Each command has a Haptics Intensity settings, and by default it is set to Low. If you assigned {WASD} to the [Left Joystick] and it feels strange to feel or hear haptics when moving the [joystick], you can consider going into the Directional Pad settings and changing Haptic Intensity Override to Off.

## Joysticks - Joystick

Joystick is the Behavior to use when you want the usual analog stick experience found in games with gamepad support.

What makes Joystick interesting is that besides being able to set the [analog stick]'s Output to the {Left Joystick} or {Right Joystick}, which is suitable for gamepad supported games, you can also set it to {Mouse}. Simlar to how a gamepad cursor behaves, when set to {Mouse} pushing the analog stick lightly will move the mouse cursor slowly and pushing it further will increasingly speed up the cursor.

### Settings to Note

To reemphasize, for games that fully implement SIAPI, Controller Settings takes on the role of the game's controller options. For games without it, any changes to Joystick settings will interact with the game's controller options.

#### Output to Joystick or Mouse

The type of gameplay experience you are looking for determines your choice between setting Output to Left Joystick, Right Joystick, or Mouse.

If you want the analog sticks to behave like they usually would in a game with gamepad support, then have [left analog stick] and [right analog stick] set to {Left Joystick} and {Right Joystick}, respectively, which is the default preference in Valve's gamepad templates.

For games that do not have gamepad support and you want to control the mouse cursor using a joystick, set the Output to {Relative Mouse}.

If you want to use gyro in a game that does not natively support it, try one of the following:

- If the game supports concurrent use of gamepad controls and mouse movement, then set [gyro] to As Mouse, the Output of [right analog stick] to Mouse, Output of [left analog stick] to Left Joystick, and adjust Joystick's Sensitivity.
- If the game does not, then either:
  - Set [gyro] to As Joystick and the Output of [right analog stick] to Right Joystick. Compared to the first option, this gyro experience may feel unusual until you become familiar with As Joystick's quirks, as described in the Trackpad - As Joystick chapter.
  - Set [gyro] to As Mouse and the Output of [right analog stick] to Mouse, and create a keyboard & mouse only layout to avoid simultaneous input issues.

#### Adjusting joystick sensitivity

There is a variety of settings to modify the joystick/mouse values that are sent to the game.

- Output Axis: You can restrict joystick/mouse output to move horizontally or vertically in-game.
- Stick Response Curve: This modifies the relation between the amount of tilt of the stick, or input, and the joystick/mouse value sent to the game, or output. For example, Linear has a 1:1 relation between input and output. Besides the presets, you can also set a Custom Curve.
  - If the game does not implement SIAPI and you do not like the game's built-in response curve, you can attempt to counteract it using this setting.
- Horizontal/Vertical Scale: This controls the maximum joystick output in the horizontal/vertical axis, where a value of 0 is no output and a value of 100 is maximum output.
  - It is possible to set the scale low enough such that pushing the stick all the way along an axis does nothing due to being in the game's deadzone.
  - While it seems implied that the sensitivity scale along each axis is independent, from my testing, they appear to be a bit related, where reducing the scale for one of them to 0 will slightly reduce the sensitivity of the other.
- Sensitivity: This controls the maximum mouse output of the analog stick, and it appears only when Output is set to Mouse.

#### Adjusting Deadzones

In the Joystick Settings, there are three Deadzone Types:

- None - Steam Input will not apply a deadzone.
- Default - Steam Input will apply a deadzone based on your analog stick calibration, performed either in this option or at Settings -> Controller -> Calibration & Advanced Settings -> Sensors -> Calibrate Joystick.
- Custom - Steam Input will apply a deadzone based on the changes you've made in the layout.

Which should you choose?

- For games that fully implement SIAPI, use Default, which should be the default preference.
- For games without SIAPI:
  - If you set Output to Relative Mouse, be sure to set it to Default.
  - If you set Output to Left/Right Joystick, use None, which is apt for games with built-in deadzones and deadzone settings. If you are not satisfied with the game's deadzone and cannot adjust it in-game, use Custom to readjust it via Output Anti-Deadzone Output Anti-Deadzone Buffer.

All of Valve's gamepad templates use None and the Keyboard & Mouse template uses Default.

##### Deadzone Type Custom

Deadzone settings: These define the physical interaction with the analog stick needed for outputting the minimum and maximum joystick/mouse values.

- Dead Zone Shape
- Deadzone Inner: Defines the minimum deflection of the stick needed before Steam Input will output the smallest joystick/mouse value to the game.
- Deadzone Outer: Defines the minimum deflection of the analog stick needed to output the largest joystick/mouse value.

If you are interesting in changing the correlation between analog stick input and the joystick output to the game, be aware that you can either adjust the in-game analog stick settings, if available, or adjust Stick Response Curve under General.

For a game that does not use SIAPI and does not include deadzone settings in-game, you can use Steam Input to modify the game's deadzone:

- Output Anti-Deadzone: If a game's deadzone is too large, you can use this to shrink it. More accurately, it defines the minimum joystick output to the game, given the smallest deflection you can do to the analog stick. This has a default value of 0.
  - For example, let us say the game's deadzone is a circle where pushing the analog stick 20% (or 6553) of the way does nothing, and you might prefer 12.5% (or 4096) instead. That means, the first 7.5% (or 2458) of pushing the stick does not do anything useful for you. In that case, you can set Output Anti-Deadzone to 2458. The next time you slightly push the stick, the smallest value sent to the game will be as if you already pushed the stick 7.5% the way there.
- Output Anti-Deadzone Buffer: If you set the Output Anti-Deadzone value to be higher than the game's deadzone for the joysticks, then the slightest push of the analog sticks will cause the in-game cursor or camera to move. This setting defines a new deadzone to be used with Output Anti-Deadzone.
  - For example, let us say the game's deadzone is 20% (or 6553), and you find the minimum camera movement just above the deadzone to be too slow. If you prefer 30% (or 9830) to be your preferred minimum speed, then set Output Anti-Deadzone to 9830. However, your new minimum output is greater than the game's deadzone, so the slightest push of the stick causes the camera to move. If you still want a deadzone size of 10% (or 3277), you can set Output Anti-Deadzone Buffer to 3277 to define a new deadzone. When you push the stick 10% of the way and it does nothing, the slightest push above that will cause a joystick output of 9830, which corresponds to your preferred minimum camera speed.

### Outer Ring Command

As discussed in the previous chapter, when you deflect the analog stick to the edge of its range, the Outer Ring Command will trigger (as long as the command's activation conditions are also satisfied).

## Joysticks - Joystick Mouse

This allows you to control the mouse using the analog stick. This is extremely similar to using Joystick Move with output set to relative mouse, the exception being it does not have the additional setting Gyro Lock at Edges.

## Joysticks - Flick Stick

Of the Input Sources available, Flick Stick Behavior is best suited for the [analog stick], so that the analog stick's 360 degrees rotation has a 1 to 1 correlation to the in-game camera's 360 degrees horizontal rotation. Because this Behavior is only capable of horizontal rotation, it must be paired with [Gyro] that is set to use As Mouse (or some camera/aim Behavior by the game developer) for controlling vertical rotation (pitch).

### Using Flickstick with analog stick

As described in Behaviors - Introduction chapter, Flick Stick is a different paradigm for controlling the in-game camera, pioneered by Jibb Smart, and Valve has implemented it into Steam Input as two components: analog stick assigned with Flick Stick Behavior and gyro assigned with As Mouse Behavior (or a camera/aim Behavior by the game developer).

Just like how using [trackpad] and [gyro] set to Mouse Behavior enables both speed and precision, Flick Stick is a different approach with similar goals and it is to be expected that playing first/third person games with this method for the first time will feel unusual.

As a general guideline,

1. Push the [analog stick] in the general direction of your target.
2. Rotate the [analog stick] and use gyro to fine-tune your horizontal aim. Also, use the [gyro] to aim vertically.
3. Repeat the above step until your aim is over the target.
4. To change to the next target, release the [analog stick] and repeat from the first step.

If the game does not have Flick Stick natively implemented into the game, whether it is via SIAPI or integrated directly by the developer, then Flick Stick Behavior in Controller Settings uses mouse movement as its basis for rotation. In this case, you must calibrate Flick Stick such that the 360 degrees rotation of the [analog stick] has a 1 to 1 correlation to the 360 degrees of the in-game camera's horizontal rotation which is done by adjusting Flick Stick to Mouse Pixels (Pixels per 360°). Calibrating this correctly is described in the next section. Additionally, you must set Gyro to As Mouse (or Gyro to Mouse [Beta]).

### Flick Stick Behavior calibration in a game without SIAPI

If you plan to use Flick Stick for a game that does not natively support it, then you will have to calibrate the Behavior.

Before listing the calibration steps, note that Flick Stick is also dependent on the in-game mouse sensitivity; therefore, Flick Stick to Mouse Pixels will need to be recalibrated if the in-game mouse sensitivity is adjusted. This is relevant if you are planning on playing the same game using a mouse, which may be the case when using the Steam Deck while docked, so adjust the in-game mouse sensitivity to your preference before proceeding.

When creating a layout for a game without SIAPI, here are the steps for calibrating Flick Stick Behavior when you are in-game and in control of your character (or camera):

1. Set gyro to None.
2. Orient the in-game camera so that you are looking straight forward.
3. Go into Steam Overlay -> Controller Settings -> set the [right analog stick] to Flick Stick.
4. Return to the game.
5. Push the stick directly forward. This corresponds to a 0 degree flick so that the camera should continue to look forward.
6. Take note of where the camera is aiming as reference, as you will rotate the analog stick 360 degrees clockwise or counter-clockwise.
7. Rotate the analog stick 360 degrees, and then note where the camera is looking now.
  - If the camera has rotated less than 360 degrees, return to step 3 and adjust Flick Stick to Mouse Pixels higher.
  - If the camera has rotated more than 360 degrees, return to step 3 and adjust Flick Stick to Mouse Pixels lower.
  - If the camera has rotated (about) 360 degrees, you have finished calibrating Flick Stick Behavior.
8. Set gyro to As Mouse and adjust As Mouse's Sensitivity as needed.

> Note that Flick Stick to Mouse Pixels (Pixels per 360°) in this Behavior is the same setting as Gyro Angles to Mouse Pixels (Pixels per 360°) in the Gyro to Mouse [Beta] Behavior; therefore, adjusting either setting will adjust the other.

### Settings to note

Other settings worth looking at:

- Snap Angle - determines the size of the deadzone in the forward direction of the analog stick where flick will not occur. For example, setting this to 90 degrees will mean pushing the analog stick within 45 degrees clockwise and counter-clockwise from the forward direction will not cause flick to occur.
- Flick-Turn Tightness - determines how quickly the camera flicks to a certain direction.
- Inner and Outer Deadzone - dictates how far you have to push the analog stick before the camera begins to flick, and the flick-turn speed will scale depending on the distance between the Inner and Outer Deadzone. Maximum speed is reached when you push beyond the Outer Deadzone.

## D-Pad - Directional Pad

Any game actions, gamepad, and keyboard & mouse commands can be assigned to each of the cardinal directions.

Classic examples of what this is used for include movement in 2D side scrollers, menu navigation or shorcuts, and less frequently used actions.

### Settings to note

For Directional Pad Layout, there are three different styles to apply to the D-Pad:

- 8 way (overlap): A pie-shaped layout where the eight pie pieces correspond to the cardinal and diagonal directions; pressing a diagonal direction activates two of the cardinal directions.
- 4 way (no overlap): A pie-shaped layout, except with diagonal directions disabled. Instead, pressing a diagonal direction will trigger the nearest cardinal direction. This is useful if you decide to assign bindings where you only need one of them to activate at any time, such as shortcuts to menus.
- Crossgate: A cross-shaped layout that emphasizes the cardinal directions over the diagonal directions.

## D-Pad - Hotbar Menu (Virtual Menu)

Hotbar Menu is a customizable menu where you use the D-Pad to navigate and activate the menu buttons that are presented in a row.

This is a Virtual Menu and serves the same purpose as the previously mentioned Radial Menu and Touch Menu.

### Using Hotbar Menu on trackpad on D-Pad

To interact with the Hotbar Menu, use the D-Pad as follows:

- Press down to open and close the menu.
- When the menu is open, press left and right to navigate the menu.
- When the menu is open, press up to activate the highlighted menu button.

### Modifying the Hotbar Menu

Hotbar Menu can be filled up to 16 menu buttons, and similar to Radial Menu, the number of menu buttons that appear on screen is equal to the number of Hotbar Buttons you assign commands to.

There are three settings to note that influence how you navigate and activate commands in the menu:

- Wrap When Scrolling - When enabled, pressing left at the first menu button will cause the last menu item to be highlighted and vice versa.
- Dismiss After Activation - When enabled, the menu closes after activating a menu button. Consider disabling this when you when to activate menu button(s) multiple times before closing the menu.
- Re-Center Each Time - When enabled, the menu button that is highlighted will be the same as the button that you last highlighted since the last time you opened the menu.

Besides the Hotbar Menu Buttons, there are two more commands that can be assigned:

- Click
- Touch - This does not do anything when a Virtual Menu is assigned to DPad.

The Click setting can have a command associated with it and can be used in-game at the same time with the Hotbar Menu Buttons.

## Buttons Pad - Button Pad

As the name suggests, this allows you to assign any command to the Deck's button pad.

## Mode Shift

Although it is found in the Behaviors list, Mode Shift is not a Behavior. Rather, it is a way for you to assign more than one Behavior to a control and then switch (or shift) between them by holding and releasing a button you designate.

One use case for Mode Shift is when a game mostly supports simultaneous gamepad and mouse input. The game can accept concurrent gamepad input for actions and mouse movement from the trackpad for aiming, but for highlighting items in the game's item/weapon wheel that is opened by [R1], it only accepts right analog stick input, not the mouse.

Using Mode Shift, you can set As Mouse as the default Behavior and Joystick as the Mode Shift Behavior to the [right trackpad]. By setting the Mode Shift Button to [R1], which is also the in-game item/weapon wheel button, you can seamlessly use the right trackpad for aiming and interacting with the wheel.

### Using Mode Shift

To add more than one Behavior to a control, go to the desired control in Edit layout:

1. In the list of Behaviors for the control, at the bottom select Create a Mode Shift.
2. For the new Behavior (Mode Shift), assign the Behavior you want.
3. Open the Mode Shift Behavior's settings (gear icon).
4. Under Behavior, select the Mode Shift Button to choose the button that you want to hold down for invoking this Behavior.

When the Modeshift button is not being pressed, the default Behavior will be active. When the Modeshift button is being pressed, the Mode Shift Behavior will be active.

### When should I use Button Chord, Mode Shift, Action Layer, and Action Set?

A simple way to decide when to use Button Chord, Mode Shift, Action Layer, and Action Set is to consider the scope of your adjustments as well as how easy it will be make changes as you iterate on your layout.

- Do you want to adjust just one button's action when a button is being held?
  - Try using Button Chord.
- Do you want to adjust just one control's Behavior when a button you designate is being held?
  - Try using Mode Shift.
- Do you want to adjust a control's Behavior when a command's activation condition is cleared?
  - Mode Shift activates by holding down a button that you designate. If you want to have a similar effect but have the Behavior change when a command's activation condition is cleared, then use an action layer with Hold Action Set Layer. An example would be to set the Outer Binding Command of an analog stick or trackpad to Hold Action Set Layer.
- Do you want to adjust two or more buttons' actions when a button is being held?
  - If you are adjusting more than a couple, maybe consider using action layer with Hold Action Set Layer instead of multiple Button Chords.
- Do you want to adjust two or more controls' Behaviors when a button is being held?
  - If you are adjusting more than a couple, maybe consider using action layer with Hold Action Set Layer instead of multiple Mode Shift Behaviors.
- You have been editing an action set, and you want a part of the set's commands and Behaviors to change with a button hold or press.
  - If you are changing only some of them, consider using action layer with Apply/Remove Action Layer or Hold Action Layer.
  - If you are changing almost all of them in a game without SIAPI implemented, consider using an action set with Change Action Set.

Alternatively, when creating a layout for a game without SIAPI implemented, rather than considering these as a thematic and/or logical way of grouping commands and behaviors or as a way to organize your edits in the layout, you can also consider what can and can not be done for each of these. For example, you can apply action layers one at a time and then use Change Action Set to quickly remove all active layers. While such a solution might not be needed in a game that implements SIAPI, such interactions can yield interesting results that can help close the gap a bit.

## Misc.

If you have read up to this point, you probably have realized this is more of a guide on Steam Input than just about Steam Deck controls, and that is true. Even if you do not own a Steam Deck, this information should be relevant whenever you are using a gamepad with Steam and wish to customize your game input experience.

I hope this guide has been somewhat helpful, and despite it being much longer than what I had anticipated when I set out to create this guide, there are still a number of topics not covered which I'm hoping to get to eventually.

If you enjoyed reading this guide, consider checking out my other one, [Steam Link Touch Controller Guide - A Visual Introduction](https://steamcommunity.com/sharedfiles/filedetails/?id=1888830141). That one goes into detail on how to create layouts on a touchscreen device, as in placing controls on the screen, and the customizations in Controller Settings that are unique to touchscreens. This guide that you are reading now is also meant to act as a companion to my other guide, so if you roughly understand the topics that I have covered here, then you are already well on your way to creating your own touchscreen layouts for playing Steam games on your smartphone or tablet.

References and Resources:

- [Steamworks - Steam Input](https://partner.steamgames.com/doc/features/steam_controller)
- [Steamworks - Steam Deck](https://partner.steamgames.com/doc/steamdeck)
- [Game Developer (Gamastura) - The Absolute Basics of Good Gyro Controls](https://www.gamedeveloper.com/design/the-absolute-basics-of-good-gyro-controls)[www.gamedeveloper.com]
- [GyroWiki by Jibb Smart](http://gyrowiki.jibbsmart.com/blog)[gyrowiki.jibbsmart.com]

Figures and assets:

- Steam Deck render from [Steam Deck - Press](https://www.steamdeck.com/en/press)
- Outline diagram is modified from [Steam Deck - Tech Specs](https://www.steamdeck.com/en/tech) and combined with glyph assets from the Steam installation folder.
- CAD files from [Steam Deck Deposit News - Steam Deck CAD files now available](https://store.steampowered.com/news/app/1675180/view/3106923225208810470).
