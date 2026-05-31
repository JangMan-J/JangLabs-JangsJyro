#include "AutoConnect.h"
#include "JslWrapper.h"
#include "InputHelpers.h"
#include "Gamepad.h"


namespace JSM
{

AutoConnect::AutoConnect(shared_ptr<JslWrapper> joyshock, bool start)
  // Pass `false` to the base so PollingThread does NOT spawn the poll thread
  // before our `jsl` member is constructed (base ctor runs before derived
  // member init). Starting below, after `jsl` is set, fixes a use-before-init
  // race that segfaulted AutoConnectPoll on a null `jsl` at startup on Linux.
  : PollingThread("AutoConnect thread", std::bind(&AutoConnect::AutoConnectPoll, this, std::placeholders::_1), nullptr, 1000, false)
  , jsl(joyshock)
{
	if (start)
		Start();
}

bool AutoConnect::AutoConnectPoll(void* param)
{
	int realSize = jsl->GetDeviceCount() - Gamepad::getCount();
	if(lastSize != realSize)
	{
		COUT_INFO << "[AUTOCONNECT] Going from " << lastSize << " devices to " << realSize << ".\n";
		lastSize = realSize;
		WriteToConsole("RECONNECT_CONTROLLERS");
	}
	return true;
}

} // namespace JSM
