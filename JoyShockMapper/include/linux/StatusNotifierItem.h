#pragma once

#include "PlatformDefinitions.h"
#include "TrayIcon.h"

#include <functional>
#include <list>
#include <string>
#include <thread>
#include <unordered_map>

#include <gio/gio.h>
#include <ayatana-appindicator.h>

// GTK-free StatusNotifierItem backed by libayatana-appindicator-glib: the menu
// is a GMenu model whose items bind to a GSimpleActionGroup (the "indicator."
// action namespace), serviced by a GLib main loop on a dedicated thread.
class StatusNotifierItem : public TrayIcon
{
public:
	using StringType = std::string;

	StatusNotifierItem(TrayIconData applicationName, std::function<void()> &&beforeShow);
	~StatusNotifierItem();

	bool Show() override;
	bool Hide() override;

	bool SendNotification(const StringType &message) override;

	void AddMenuItem(const std::string &label, ClickCallbackType &&onClick) override;
	void AddMenuItem(const std::string &label, ClickCallbackTypeChecked &&onClick, StateCallbackType &&getState) override;
	void AddMenuItem(const std::string &label, const std::string &subLabel, ClickCallbackType &&onClick) override;

	void ClearMenuMap() override;

	operator bool() override;

private:
	static void OnActivate(GSimpleAction *action, GVariant *parameter, void *data) noexcept;

	// Registers `action` + its callback and returns the "indicator.<name>"
	// detailed-action string to attach to a GMenuItem. Consumes `action`'s ref.
	std::string addAction(GSimpleAction *action, ClickCallbackType &&onClick);
	GMenu *getOrCreateSubMenu(const std::string &label);

	AppIndicator *indicator_{ nullptr };
	GMenu *menu_{ nullptr };
	GSimpleActionGroup *actions_{ nullptr };
	GMainContext *context_{ nullptr };
	GMainLoop *loop_{ nullptr };

	std::unordered_map<std::string, GMenu *> subMenus_;
	std::list<ClickCallbackType> callbacks_;
	unsigned actionCounter_{ 0 };

	std::thread thread_;
};
