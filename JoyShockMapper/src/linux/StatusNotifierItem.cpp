#include "linux/StatusNotifierItem.h"

#include <cstdlib>
#include <string>
#include <utility>

TrayIcon *TrayIcon::getNew(TrayIconData applicationName, std::function<void()> &&beforeShow)
{
	return new StatusNotifierItem(applicationName, std::forward<std::function<void()>>(beforeShow));
}

StatusNotifierItem::StatusNotifierItem(TrayIconData, std::function<void()> &&beforeShow)
  : context_{ g_main_context_new() }
  , loop_{ g_main_loop_new(context_, FALSE) }
  // Capture beforeShow BY MOVE: the lambda runs on thread_, which outlives this
  // constructor; capturing the rvalue-ref parameter by reference would dangle.
  , thread_{ [this, beforeShow = std::move(beforeShow)] {
	  g_main_context_push_thread_default(context_);

	  std::string iconName = "jsm-status-dark";
	  if (const char *appdir = ::getenv("APPDIR"); appdir != nullptr)
	  {
		  iconName = std::string(appdir) + "/usr/share/icons/hicolor/24x24/status/jsm-status-dark.svg";
	  }

	  menu_ = g_menu_new();
	  actions_ = g_simple_action_group_new();
	  indicator_ = app_indicator_new(APPLICATION_RDN APPLICATION_NAME, iconName.c_str(), APP_INDICATOR_CATEGORY_APPLICATION_STATUS);

	  // beforeShow() builds the menu via AddMenuItem on this thread, so all
	  // GMenu/GAction construction stays single-threaded.
	  beforeShow();

	  // The indicator renders only once it has BOTH a menu and actions.
	  app_indicator_set_menu(indicator_, menu_);
	  app_indicator_set_actions(indicator_, actions_);
	  app_indicator_set_status(indicator_, APP_INDICATOR_STATUS_ACTIVE);

	  g_main_loop_run(loop_);

	  g_main_context_pop_thread_default(context_);
  } }
{
}

StatusNotifierItem::~StatusNotifierItem()
{
	if (loop_ != nullptr)
	{
		// Quit the loop on its own thread, then join.
		g_main_context_invoke(
		  context_,
		  [](void *data) -> gboolean {
			  g_main_loop_quit(static_cast<StatusNotifierItem *>(data)->loop_);
			  return G_SOURCE_REMOVE;
		  },
		  this);
	}

	if (thread_.joinable())
	{
		thread_.join();
	}

	for (auto &entry : subMenus_)
	{
		g_clear_object(&entry.second);
	}
	g_clear_object(&indicator_);
	g_clear_object(&menu_);
	g_clear_object(&actions_);
	if (loop_ != nullptr)
	{
		g_main_loop_unref(loop_);
		loop_ = nullptr;
	}
	if (context_ != nullptr)
	{
		g_main_context_unref(context_);
		context_ = nullptr;
	}
}

std::string StatusNotifierItem::addAction(GSimpleAction *action, ClickCallbackType &&onClick)
{
	callbacks_.emplace_back(std::move(onClick));
	// std::list keeps element addresses stable, so &back() is valid for the
	// lifetime of the action.
	g_signal_connect(action, "activate", G_CALLBACK(&StatusNotifierItem::OnActivate), &callbacks_.back());
	g_action_map_add_action(G_ACTION_MAP(actions_), G_ACTION(action)); // takes its own ref
	std::string detailed = std::string("indicator.") + g_action_get_name(G_ACTION(action));
	g_object_unref(action);
	return detailed;
}

void StatusNotifierItem::AddMenuItem(const std::string &label, ClickCallbackType &&onClick)
{
	// Disable show-hide console since this is not supported on Linux
	if (label == "Show Console")
		return;

	const std::string name = "item" + std::to_string(actionCounter_++);
	GSimpleAction *action = g_simple_action_new(name.c_str(), nullptr);
	const std::string detailed = addAction(action, std::move(onClick));

	GMenuItem *item = g_menu_item_new(label.c_str(), detailed.c_str());
	g_menu_append_item(menu_, item);
	g_object_unref(item);
}

void StatusNotifierItem::AddMenuItem(const std::string &label, ClickCallbackTypeChecked &&onClick, StateCallbackType &&getState)
{
	// Disable show-hide console since this is not supported on Linux
	if (label == "Show Console")
		return;

	const std::string name = "item" + std::to_string(actionCounter_++);
	// Boolean-stateful action with no parameter type toggles its visual state on
	// activation; we mirror the click into the app-side state via onClick.
	GSimpleAction *action = g_simple_action_new_stateful(name.c_str(), nullptr, g_variant_new_boolean(getState()));
	const std::string detailed = addAction(action, [onClick = std::move(onClick), getState = std::move(getState)] {
		onClick(!getState());
	});

	GMenuItem *item = g_menu_item_new(label.c_str(), detailed.c_str());
	g_menu_append_item(menu_, item);
	g_object_unref(item);
}

void StatusNotifierItem::AddMenuItem(const std::string &label, const std::string &subLabel, ClickCallbackType &&onClick)
{
	// Disable show-hide console since this is not supported on Linux
	if (label == "Show Console")
		return;

	GMenu *submenu = getOrCreateSubMenu(label);

	const std::string name = "item" + std::to_string(actionCounter_++);
	GSimpleAction *action = g_simple_action_new(name.c_str(), nullptr);
	const std::string detailed = addAction(action, std::move(onClick));

	GMenuItem *item = g_menu_item_new(subLabel.c_str(), detailed.c_str());
	g_menu_append_item(submenu, item);
	g_object_unref(item);
}

GMenu *StatusNotifierItem::getOrCreateSubMenu(const std::string &label)
{
	if (auto it = subMenus_.find(label); it != subMenus_.end())
	{
		return it->second;
	}

	GMenu *submenu = g_menu_new();
	g_menu_append_submenu(menu_, label.c_str(), G_MENU_MODEL(submenu)); // takes its own ref
	subMenus_.emplace(label, submenu);                                  // keep our ref; released in dtor
	return submenu;
}

void StatusNotifierItem::ClearMenuMap()
{
}

void StatusNotifierItem::OnActivate(GSimpleAction *, GVariant *, void *data) noexcept
{
	auto *cb = static_cast<ClickCallbackType *>(data);
	(*cb)();
}

bool StatusNotifierItem::Show()
{
	g_main_context_invoke(
	  context_,
	  [](void *data) -> gboolean {
		  auto *self = static_cast<StatusNotifierItem *>(data);
		  if (self->indicator_ != nullptr)
			  app_indicator_set_status(self->indicator_, APP_INDICATOR_STATUS_ACTIVE);
		  return G_SOURCE_REMOVE;
	  },
	  this);
	return true;
}

bool StatusNotifierItem::Hide()
{
	g_main_context_invoke(
	  context_,
	  [](void *data) -> gboolean {
		  auto *self = static_cast<StatusNotifierItem *>(data);
		  if (self->indicator_ != nullptr)
			  app_indicator_set_status(self->indicator_, APP_INDICATOR_STATUS_PASSIVE);
		  return G_SOURCE_REMOVE;
	  },
	  this);
	return true;
}

bool StatusNotifierItem::SendNotification(const std::string &)
{
	return true;
}

StatusNotifierItem::operator bool()
{
	return true;
}
