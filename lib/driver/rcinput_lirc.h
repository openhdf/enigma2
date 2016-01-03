#ifndef __lib_driver_rclirc_h
#define __lib_driver_rclirc_h

#include <sys/un.h>
#include <lib/driver/rc.h>
#include <lib/base/thread.h>
#include <lib/base/message.h>

struct tKey {
	uint16_t    code;
	const char  *name;
};

struct lircEvent {
	const char  *name;
	bool        repeat;
	bool        release;
};

class eLircInputDevice : public eRCDevice
{
private:
	bool m_escape;
	unsigned int m_unicode;
	int translateKey(const char* name);

public:
	eLircInputDevice(eRCDriver *driver);
	~eLircInputDevice();

	virtual void handleCode(long arg);
	virtual const char *getDescription() const;
};

class eLircInputDriver : public eRCDriver, public eThread
{
private:
	enum { LIRC_KEY_BUF = 108, LIRC_BUFFER_SIZE = 128 };
	static eLircInputDriver *instance;
	eFixedMessagePump<lircEvent> m_pump;
	void pumpEvent(const lircEvent &keyEvent);
	int f;
	struct sockaddr_un addr;
	virtual void thread();
	bool thread_stop;
	bool Connect(void);

public:
	eLircInputDriver();
	~eLircInputDriver();

	static eLircInputDriver *getInstance() { return instance; }
	void keyPressed(const lircEvent &keyEvent);
};

#endif
