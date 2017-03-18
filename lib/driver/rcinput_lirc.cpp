/*
 * LIRC support based on LIRC for VDR, which was written by
 * Carsten Koch.
 * 
*/

#include <netinet/in.h>
#include <sys/socket.h>
#include <lib/driver/rcinput_lirc.h>
#include <lib/base/init.h>
#include <lib/base/init_num.h>
#include <lib/base/condVar.h>
#include <lib/driver/input_fake.h>


// Converts a hexadecimal string to integer

int xtoi(const char* xs, unsigned int* result)
{
 size_t szlen = strlen(xs);
 int i, xv, fact;

 if (szlen > 0)
 {
  // Converting more than 32bit hexadecimal value?
  if (szlen>8) return 2; // exit

  // Begin conversion here
  *result = 0;
  fact = 1;

  // Run until no more character to convert
  for(i=szlen-1; i>=0 ;i--)
  {
   if (isxdigit(*(xs+i)))
   {
    if (*(xs+i)>=97)
    {
     xv = ( *(xs+i) - 97) + 10;
    }
    else if ( *(xs+i) >= 65)
    {
     xv = (*(xs+i) - 65) + 10;
    }
    else
    {
     xv = *(xs+i) - 48;
    }
    *result += (xv * fact);
    fact *= 16;
   }
   else
   {
    // Conversion was abnormally terminated
    // by non hexadecimal digit, hence
    // returning only the converted with
    // an error value 4 (illegal hex character)
    return 4;
   }
  }
 }

 // Nothing to convert
 return 1;
}


static tKey keyTable[] = { // "Up" and "Down" must be the first two keys!
	{ KEY_RESERVED,         "KEY_RESERVED"         },
	{ KEY_ESC,              "KEY_ESC"              },
	{ KEY_1,                "KEY_1"                },
	{ KEY_2,                "KEY_2"                },
	{ KEY_3,                "KEY_3"                },
	{ KEY_4,                "KEY_4"                },
	{ KEY_5,                "KEY_5"                },
	{ KEY_6,                "KEY_6"                },
	{ KEY_7,                "KEY_7"                },
	{ KEY_8,                "KEY_8"                },
	{ KEY_9,                "KEY_9"                },
	{ KEY_0,                "KEY_0"                },
	{ KEY_MINUS,            "KEY_MINUS"            },
	{ KEY_EQUAL,            "KEY_EQUAL"            },
	{ KEY_BACKSPACE,        "KEY_BACKSPACE"        },
	{ KEY_TAB,              "KEY_TAB"              },
	{ KEY_Q,                "KEY_Q"                },
	{ KEY_W,                "KEY_W"                },
	{ KEY_E,                "KEY_E"                },
	{ KEY_R,                "KEY_R"                },
	{ KEY_T,                "KEY_T"                },
	{ KEY_Y,                "KEY_Y"                },
	{ KEY_U,                "KEY_U"                },
	{ KEY_I,                "KEY_I"                },
	{ KEY_O,                "KEY_O"                },
	{ KEY_P,                "KEY_P"                },
	{ KEY_LEFTBRACE,        "KEY_LEFTBRACE"        },
	{ KEY_RIGHTBRACE,       "KEY_RIGHTBRACE"       },
	{ KEY_ENTER,            "KEY_ENTER"            },
	{ KEY_LEFTCTRL,         "KEY_LEFTCTRL"         },
	{ KEY_A,                "KEY_A"                },
	{ KEY_S,                "KEY_S"                },
	{ KEY_D,                "KEY_D"                },
	{ KEY_F,                "KEY_F"                },
	{ KEY_G,                "KEY_G"                },
	{ KEY_H,                "KEY_H"                },
	{ KEY_J,                "KEY_J"                },
	{ KEY_K,                "KEY_K"                },
	{ KEY_L,                "KEY_L"                },
	{ KEY_SEMICOLON,        "KEY_SEMICOLON"        },
	{ KEY_APOSTROPHE,       "KEY_APOSTROPHE"       },
	{ KEY_GRAVE,            "KEY_GRAVE"            },
	{ KEY_LEFTSHIFT,        "KEY_LEFTSHIFT"        },
	{ KEY_BACKSLASH,        "KEY_BACKSLASH"        },
	{ KEY_Z,                "KEY_Z"                },
	{ KEY_X,                "KEY_X"                },
	{ KEY_C,                "KEY_C"                },
	{ KEY_V,                "KEY_V"                },
	{ KEY_B,                "KEY_B"                },
	{ KEY_N,                "KEY_N"                },
	{ KEY_M,                "KEY_M"                },
	{ KEY_COMMA,            "KEY_COMMA"            },
	{ KEY_DOT,              "KEY_DOT"              },
	{ KEY_SLASH,            "KEY_SLASH"            },
	{ KEY_RIGHTSHIFT,       "KEY_RIGHTSHIFT"       },
	{ KEY_KPASTERISK,       "KEY_KPASTERISK"       },
	{ KEY_LEFTALT,          "KEY_LEFTALT"          },
	{ KEY_SPACE,            "KEY_SPACE"            },
	{ KEY_CAPSLOCK,         "KEY_CAPSLOCK"         },
	{ KEY_F1,               "KEY_F1"               },
	{ KEY_F2,               "KEY_F2"               },
	{ KEY_F3,               "KEY_F3"               },
	{ KEY_F4,               "KEY_F4"               },
	{ KEY_F5,               "KEY_F5"               },
	{ KEY_F6,               "KEY_F6"               },
	{ KEY_F7,               "KEY_F7"               },
	{ KEY_F8,               "KEY_F8"               },
	{ KEY_F9,               "KEY_F9"               },
	{ KEY_F10,              "KEY_F10"              },
	{ KEY_NUMLOCK,          "KEY_NUMLOCK"          },
	{ KEY_SCROLLLOCK,       "KEY_SCROLLLOCK"       },
	{ KEY_KP7,              "KEY_KP7"              },
	{ KEY_KP8,              "KEY_KP8"              },
	{ KEY_KP9,              "KEY_KP9"              },
	{ KEY_KPMINUS,          "KEY_KPMINUS"          },
	{ KEY_KP4,              "KEY_KP4"              },
	{ KEY_KP5,              "KEY_KP5"              },
	{ KEY_KP6,              "KEY_KP6"              },
	{ KEY_KP1,              "KEY_KP1"              },
	{ KEY_KP2,              "KEY_KP2"              },
	{ KEY_KP3,              "KEY_KP3"              },
	{ KEY_KP0,              "KEY_KP0"              },
	{ KEY_KPDOT,            "KEY_KPDOT"            },
	{ KEY_ZENKAKUHANKAKU,   "KEY_ZENKAKUHANKAKU"   },
	{ KEY_102ND,            "KEY_102ND"            },
	{ KEY_F11,              "KEY_F11"              },
	{ KEY_F12,              "KEY_F12"              },
	{ KEY_RO,               "KEY_RO"               },
	{ KEY_KATAKANA,         "KEY_KATAKANA"         },
	{ KEY_HIRAGANA,         "KEY_HIRAGANA"         },
	{ KEY_HENKAN,           "KEY_HENKAN"           },
	{ KEY_KATAKANAHIRAGANA, "KEY_KATAKANAHIRAGANA" },
	{ KEY_MUHENKAN,         "KEY_MUHENKAN"         },
	{ KEY_KPJPCOMMA,        "KEY_KPJPCOMMA"        },
	{ KEY_KPENTER,          "KEY_KPENTER"          },
	{ KEY_RIGHTCTRL,        "KEY_RIGHTCTRL"        },
	{ KEY_KPSLASH,          "KEY_KPSLASH"          },
	{ KEY_SYSRQ,            "KEY_SYSRQ"            },
	{ KEY_RIGHTALT,         "KEY_RIGHTALT"         },
	{ KEY_LINEFEED,         "KEY_LINEFEED"         },
	{ KEY_HOME,             "KEY_HOME"             },
	{ KEY_UP,               "KEY_UP"               },
	{ KEY_PAGEUP,           "KEY_PAGEUP"           },
	{ KEY_LEFT,             "KEY_LEFT"             },
	{ KEY_RIGHT,            "KEY_RIGHT"            },
	{ KEY_END,              "KEY_END"              },
	{ KEY_DOWN,             "KEY_DOWN"             },
	{ KEY_PAGEDOWN,         "KEY_PAGEDOWN"         },
	{ KEY_INSERT,           "KEY_INSERT"           },
	{ KEY_DELETE,           "KEY_DELETE"           },
	{ KEY_MACRO,            "KEY_MACRO"            },
	{ KEY_MUTE,             "KEY_MUTE"             },
	{ KEY_VOLUMEDOWN,       "KEY_VOLUMEDOWN"       },
	{ KEY_VOLUMEUP,         "KEY_VOLUMEUP"         },
	{ KEY_POWER,            "KEY_POWER"            },
	{ KEY_KPEQUAL,          "KEY_KPEQUAL"          },
	{ KEY_KPPLUSMINUS,      "KEY_KPPLUSMINUS"      },
	{ KEY_PAUSE,            "KEY_PAUSE"            },
	{ KEY_SCALE,            "KEY_SCALE"            },
	{ KEY_KPCOMMA,          "KEY_KPCOMMA"          },
	{ KEY_HANGEUL,          "KEY_HANGEUL"          },
	{ KEY_HANGUEL,          "KEY_HANGUEL"          },
	{ KEY_HANJA,            "KEY_HANJA"            },
	{ KEY_YEN,              "KEY_YEN"              },
	{ KEY_LEFTMETA,         "KEY_LEFTMETA"         },
	{ KEY_RIGHTMETA,        "KEY_RIGHTMETA"        },
	{ KEY_COMPOSE,          "KEY_COMPOSE"          },
	{ KEY_STOP,             "KEY_STOP"             },
	{ KEY_AGAIN,            "KEY_AGAIN"            },
	{ KEY_PROPS,            "KEY_PROPS"            },
	{ KEY_UNDO,             "KEY_UNDO"             },
	{ KEY_FRONT,            "KEY_FRONT"            },
	{ KEY_COPY,             "KEY_COPY"             },
	{ KEY_OPEN,             "KEY_OPEN"             },
	{ KEY_PASTE,            "KEY_PASTE"            },
	{ KEY_FIND,             "KEY_FIND"             },
	{ KEY_CUT,              "KEY_CUT"              },
	{ KEY_HELP,             "KEY_HELP"             },
	{ KEY_MENU,             "KEY_MENU"             },
	{ KEY_CALC,             "KEY_CALC"             },
	{ KEY_SETUP,            "KEY_SETUP"            },
	{ KEY_SLEEP,            "KEY_SLEEP"            },
	{ KEY_WAKEUP,           "KEY_WAKEUP"           },
	{ KEY_FILE,             "KEY_FILE"             },
	{ KEY_SENDFILE,         "KEY_SENDFILE"         },
	{ KEY_DELETEFILE,       "KEY_DELETEFILE"       },
	{ KEY_XFER,             "KEY_XFER"             },
	{ KEY_PROG1,            "KEY_PROG1"            },
	{ KEY_PROG2,            "KEY_PROG2"            },
	{ KEY_WWW,              "KEY_WWW"              },
	{ KEY_MSDOS,            "KEY_MSDOS"            },
	{ KEY_COFFEE,           "KEY_COFFEE"           },
	{ KEY_SCREENLOCK,       "KEY_SCREENLOCK"       },
	{ KEY_DIRECTION,        "KEY_DIRECTION"        },
	{ KEY_CYCLEWINDOWS,     "KEY_CYCLEWINDOWS"     },
	{ KEY_MAIL,             "KEY_MAIL"             },
	{ KEY_BOOKMARKS,        "KEY_BOOKMARKS"        },
	{ KEY_COMPUTER,         "KEY_COMPUTER"         },
	{ KEY_BACK,             "KEY_BACK"             },
	{ KEY_FORWARD,          "KEY_FORWARD"          },
	{ KEY_CLOSECD,          "KEY_CLOSECD"          },
	{ KEY_EJECTCD,          "KEY_EJECTCD"          },
	{ KEY_EJECTCLOSECD,     "KEY_EJECTCLOSECD"     },
	{ KEY_NEXTSONG,         "KEY_NEXTSONG"         },
	{ KEY_PLAYPAUSE,        "KEY_PLAYPAUSE"        },
	{ KEY_PREVIOUSSONG,     "KEY_PREVIOUSSONG"     },
	{ KEY_STOPCD,           "KEY_STOPCD"           },
	{ KEY_RECORD,           "KEY_RECORD"           },
	{ KEY_REWIND,           "KEY_REWIND"           },
	{ KEY_PHONE,            "KEY_PHONE"            },
	{ KEY_ISO,              "KEY_ISO"              },
	{ KEY_CONFIG,           "KEY_CONFIG"           },
	{ KEY_HOMEPAGE,         "KEY_HOMEPAGE"         },
	{ KEY_REFRESH,          "KEY_REFRESH"          },
	{ KEY_EXIT,             "KEY_EXIT"             },
	{ KEY_MOVE,             "KEY_MOVE"             },
	{ KEY_EDIT,             "KEY_EDIT"             },
	{ KEY_SCROLLUP,         "KEY_SCROLLUP"         },
	{ KEY_SCROLLDOWN,       "KEY_SCROLLDOWN"       },
	{ KEY_KPLEFTPAREN,      "KEY_KPLEFTPAREN"      },
	{ KEY_KPRIGHTPAREN,     "KEY_KPRIGHTPAREN"     },
	{ KEY_NEW,              "KEY_NEW"              },
	{ KEY_REDO,             "KEY_REDO"             },
	{ KEY_F13,              "KEY_F13"              },
	{ KEY_F14,              "KEY_F14"              },
	{ KEY_F15,              "KEY_F15"              },
	{ KEY_F16,              "KEY_F16"              },
	{ KEY_F17,              "KEY_F17"              },
	{ KEY_F18,              "KEY_F18"              },
	{ KEY_F19,              "KEY_F19"              },
	{ KEY_F20,              "KEY_F20"              },
	{ KEY_F21,              "KEY_F21"              },
	{ KEY_F22,              "KEY_F22"              },
	{ KEY_F23,              "KEY_F23"              },
	{ KEY_F24,              "KEY_F24"              },
	{ KEY_PLAYCD,           "KEY_PLAYCD"           },
	{ KEY_PAUSECD,          "KEY_PAUSECD"          },
	{ KEY_PROG3,            "KEY_PROG3"            },
	{ KEY_PROG4,            "KEY_PROG4"            },
	{ KEY_DASHBOARD,        "KEY_DASHBOARD"        },
	{ KEY_SUSPEND,          "KEY_SUSPEND"          },
	{ KEY_CLOSE,            "KEY_CLOSE"            },
	{ KEY_PLAY,             "KEY_PLAY"             },
	{ KEY_FASTFORWARD,      "KEY_FASTFORWARD"      },
	{ KEY_BASSBOOST,        "KEY_BASSBOOST"        },
	{ KEY_PRINT,            "KEY_PRINT"            },
	{ KEY_HP,               "KEY_HP"               },
	{ KEY_CAMERA,           "KEY_CAMERA"           },
	{ KEY_SOUND,            "KEY_SOUND"            },
	{ KEY_QUESTION,         "KEY_QUESTION"         },
	{ KEY_EMAIL,            "KEY_EMAIL"            },
	{ KEY_CHAT,             "KEY_CHAT"             },
	{ KEY_SEARCH,           "KEY_SEARCH"           },
	{ KEY_CONNECT,          "KEY_CONNECT"          },
	{ KEY_FINANCE,          "KEY_FINANCE"          },
	{ KEY_SPORT,            "KEY_SPORT"            },
	{ KEY_SHOP,             "KEY_SHOP"             },
	{ KEY_ALTERASE,         "KEY_ALTERASE"         },
	{ KEY_CANCEL,           "KEY_CANCEL"           },
	{ KEY_BRIGHTNESSDOWN,   "KEY_BRIGHTNESSDOWN"   },
	{ KEY_BRIGHTNESSUP,     "KEY_BRIGHTNESSUP"     },
	{ KEY_MEDIA,            "KEY_MEDIA"            },
	{ KEY_SWITCHVIDEOMODE,  "KEY_SWITCHVIDEOMODE"  },
	{ KEY_KBDILLUMTOGGLE,   "KEY_KBDILLUMTOGGLE"   },
	{ KEY_KBDILLUMDOWN,     "KEY_KBDILLUMDOWN"     },
	{ KEY_KBDILLUMUP,       "KEY_KBDILLUMUP"       },
	{ KEY_SEND,             "KEY_SEND"             },
  { KEY_REPLY,            "KEY_REPLY"            },
	{ KEY_FORWARDMAIL,      "KEY_FORWARDMAIL"      },
	{ KEY_SAVE,             "KEY_SAVE"             },
	{ KEY_DOCUMENTS,        "KEY_DOCUMENTS"        },
	{ KEY_BATTERY,          "KEY_BATTERY"          },
	{ KEY_BLUETOOTH,        "KEY_BLUETOOTH"        },
	{ KEY_WLAN,             "KEY_WLAN"             },
	{ KEY_UWB,              "KEY_UWB"              },
	{ KEY_UNKNOWN,          "KEY_UNKNOWN"          },
	{ KEY_VIDEO_NEXT,       "KEY_VIDEO_NEXT"       },
	{ KEY_VIDEO_PREV,       "KEY_VIDEO_PREV"       },
	{ KEY_BRIGHTNESS_CYCLE, "KEY_BRIGHTNESS_CYCLE" },
	{ KEY_BRIGHTNESS_ZERO,  "KEY_BRIGHTNESS_ZERO"  },
	{ KEY_DISPLAY_OFF,      "KEY_DISPLAY_OFF"      },
	{ KEY_WIMAX,            "KEY_WIMAX"            },
//	{ KEY_RFKILL,           "KEY_RFKILL"           },

	{ KEY_OK,               "KEY_OK"               },
	{ KEY_SELECT,           "KEY_SELECT"           },
	{ KEY_GOTO,             "KEY_GOTO"             },
	{ KEY_CLEAR,            "KEY_CLEAR"            },
	{ KEY_POWER2,           "KEY_POWER2"           },
	{ KEY_OPTION,           "KEY_OPTION"           },
	{ KEY_INFO,             "KEY_INFO"             },
	{ KEY_TIME,             "KEY_TIME"             },
	{ KEY_VENDOR,           "KEY_VENDOR"           },
	{ KEY_ARCHIVE,          "KEY_ARCHIVE"          },
	{ KEY_PROGRAM,          "KEY_PROGRAM"          },
	{ KEY_CHANNEL,          "KEY_CHANNEL"          },
	{ KEY_FAVORITES,        "KEY_FAVORITES"        },
	{ KEY_EPG,              "KEY_EPG"              },
	{ KEY_PVR,              "KEY_PVR"              },
	{ KEY_MHP,              "KEY_MHP"              },
	{ KEY_LANGUAGE,         "KEY_LANGUAGE"         },
	{ KEY_TITLE,            "KEY_TITLE"            },
	{ KEY_SUBTITLE,         "KEY_SUBTITLE"         },
	{ KEY_ANGLE,            "KEY_ANGLE"            },
	{ KEY_ZOOM,             "KEY_ZOOM"             },
	{ KEY_MODE,             "KEY_MODE"             },
	{ KEY_KEYBOARD,         "KEY_KEYBOARD"         },
	{ KEY_SCREEN,           "KEY_SCREEN"           },
	{ KEY_PC,               "KEY_PC"               },
	{ KEY_TV,               "KEY_TV"               },
	{ KEY_TV2,              "KEY_TV2"              },
	{ KEY_VCR,              "KEY_VCR"              },
	{ KEY_VCR2,             "KEY_VCR2"             },
	{ KEY_SAT,              "KEY_SAT"              },
	{ KEY_SAT2,             "KEY_SAT2"             },
	{ KEY_CD,               "KEY_CD"               },
	{ KEY_TAPE,             "KEY_TAPE"             },
	{ KEY_RADIO,            "KEY_RADIO"            },
	{ KEY_TUNER,            "KEY_TUNER"            },
	{ KEY_PLAYER,           "KEY_PLAYER"           },
	{ KEY_TEXT,             "KEY_TEXT"             },
	{ KEY_DVD,              "KEY_DVD"              },
	{ KEY_AUX,              "KEY_AUX"              },
	{ KEY_MP3,              "KEY_MP3"              },
	{ KEY_AUDIO,            "KEY_AUDIO"            },
	{ KEY_VIDEO,            "KEY_VIDEO"            },
	{ KEY_DIRECTORY,        "KEY_DIRECTORY"        },
	{ KEY_LIST,             "KEY_LIST"             },
	{ KEY_MEMO,             "KEY_MEMO"             },
	{ KEY_CALENDAR,         "KEY_CALENDAR"         },
	{ KEY_RED,              "KEY_RED"              },
	{ KEY_GREEN,            "KEY_GREEN"            },
	{ KEY_YELLOW,           "KEY_YELLOW"           },
	{ KEY_BLUE,             "KEY_BLUE"             },
	{ KEY_CHANNELUP,        "KEY_CHANNELUP"        },
	{ KEY_CHANNELDOWN,      "KEY_CHANNELDOWN"      },
	{ KEY_FIRST,            "KEY_FIRST"            },
	{ KEY_LAST,             "KEY_LAST"             },
	{ KEY_AB,               "KEY_AB"               },
	{ KEY_PLAY,             "KEY_PLAY"             },
	{ KEY_RESTART,          "KEY_RESTART"          },
	{ KEY_SLOW,             "KEY_SLOW"             },
	{ KEY_SHUFFLE,          "KEY_SHUFFLE"          },
	{ KEY_FASTFORWARD,      "KEY_FASTFORWARD"      },
	{ KEY_PREVIOUS,         "KEY_PREVIOUS"         },
	{ KEY_NEXT,             "KEY_NEXT"             },
	{ KEY_DIGITS,           "KEY_DIGITS"           },
	{ KEY_TEEN,             "KEY_TEEN"             },
	{ KEY_TWEN,             "KEY_TWEN"             },
	{ KEY_BREAK,            "KEY_BREAK"            },

	{ 0,                    NULL                   },
};

/*
 * eLircInputDevice
 */

eLircInputDevice::eLircInputDevice(eRCDriver *driver) : eRCDevice("Lirc", driver), m_escape(false), m_unicode(0)
{}

eLircInputDevice::~eLircInputDevice()
{}

void eLircInputDevice::handleCode(long arg)
{
	const lircEvent* event = (const lircEvent*)arg;
	int code, flags;
	
	if (event->repeat == true) {
		flags = eRCKey::flagRepeat;
	} else if (event->release == true) {
		flags = eRCKey::flagBreak;
	} else {
		flags = eRCKey::flagMake;
	}

	code = translateKey(event->name);

	//eDebug("LIRC name=%s code=%d flags=%d", event->name, code, flags);
	input->keyPressed(eRCKey(this, code, flags));
}

const char *eLircInputDevice::getDescription() const
{
	return "Lirc";
}

int eLircInputDevice::translateKey(const char* name)
{
	if (name==NULL)
	{
		eDebug("LIRC: translateKey ERROR");
		return KEY_RESERVED;
	}

	for (int i=0;keyTable[i].name!=NULL;i++)
	{
		if (!strcmp(name, keyTable[i].name))
		{
			//printf("FOUND KEY CODE FOR %s: %04X\n", name, keyTable[i].code);
			return keyTable[i].code;
		}
	}

	eDebug("LIRC: unhandled key name: %s", name);
	return KEY_RESERVED;
}

/*
 * eLircInputDriver
 */

#define IGNOREFIRSTREPEAT true
#define REPEATCOUNT 1 //increase to ignore all repeats-signals with count not dividable by repeatcount
#define REPEATDELAY 100 // ms
#define REPEATFREQ 100 // ms
#define REPEATTIMEOUT 500 // ms
#define RECONNECTDELAY 3000 // ms


static bool fileReady(int FileDes, int TimeoutMs)
{
	fd_set set;
	struct timeval timeout;
	FD_ZERO(&set);
	FD_SET(FileDes, &set);
	if (TimeoutMs >= 0) {
		if (TimeoutMs < 100)
			TimeoutMs = 100;
		timeout.tv_sec  = TimeoutMs / 1000;
		timeout.tv_usec = (TimeoutMs % 1000) * 1000;
	}
	return select(FD_SETSIZE, &set, NULL, NULL, (TimeoutMs >= 0) ? &timeout : NULL) > 0 && FD_ISSET(FileDes, &set);
}

static ssize_t safe_read(int filedes, void *buffer, size_t size)
{
	for (;;) {
//("AAread1\n");
		ssize_t p = read(filedes, buffer, size);
//printf("AAread2\n");
		if (p < 0 && errno == EINTR) {
			continue;
		}
		return p;
	}
}

void eLircInputDriver::pumpEvent(const lircEvent &event)
{
	keyPressed(event);
}

eLircInputDriver *eLircInputDriver::instance;

bool eLircInputDriver::Connect(void)
{
	if ((f = socket(AF_UNIX, SOCK_STREAM, 0)) >= 0) {
		if (connect(f, (struct sockaddr *)&addr, sizeof(addr)) >= 0)
 			return true;
		eDebug("Lirc: Connect to %s error !!!", addr.sun_path);
		close(f);
		f = -1;
	}
	else
		eDebug("Lirc: Connect to %s error !!!", addr.sun_path);

	return false;
}

eLircInputDriver::eLircInputDriver() : eRCDriver(eRCInput::getInstance()), m_pump(eApp, 1)
{
	ASSERT(instance == 0);
	instance = this;

	CONNECT(m_pump.recv_msg, eLircInputDriver::pumpEvent);

	addr.sun_family = AF_UNIX;
	strcpy(addr.sun_path, "/var/run/lirc/lircd");
	if (Connect()) {
		run();
		return;
	}
	f = -1;
}

eLircInputDriver::~eLircInputDriver()
{
	instance = 0;

	int fh = f;
	f = -1;

	thread_stop = true;
	sendSignal(SIGINT);
	kill();

	if (fh >= 0)
		close(fh);
}

void eLircInputDriver::thread()
{
	cTimeMs FirstTime;
	cTimeMs LastTime;
	char buf[LIRC_BUFFER_SIZE];
	char LastKeyName[54] = "";
	bool repeat = false;
	int timeout = -1;
	lircEvent event;

	hasStarted();
	thread_stop = false;

	while (!thread_stop && f>=0) {
		bool ready = fileReady(f, timeout);
		int ret = ready ? safe_read(f, buf, sizeof(buf)) : -1;

		if (ready && ret <= 0 ) {
			eDebug("ERROR: lircd connection broken, trying to reconnect every %.1f seconds", float(RECONNECTDELAY) / 1000);
			close(f);
			f = -1;
			while (!thread_stop && f < 0) {
				cCondWait::SleepMs(RECONNECTDELAY);
				if (Connect()) {
					eDebug("reconnected to lircd");
					break;
				}
			}
		}

		if (ready && ret > 21) {
			unsigned int count;
			char countstring[2] = "";
			char substr[3] = "";
			char rawcode[17] = "";
			char KeyName[54] = "";
			char RemoteName[54] = "";
			if (sscanf(buf, "%17s %2s %53s %53s", rawcode, countstring, KeyName, RemoteName) != 4) { // 128buffer size = 17 + 2 + 2x53 + 3 spaces!!
				eDebug("ERROR: unparseable lirc command: %s", buf);
				continue;
			}
			else {
				xtoi(countstring, &count);
				sscanf(RemoteName, "%3s %*s", substr);
			}
			if (strcmp(substr, "E2_") != 0) {
				eDebug("Ignored event from remote : %s", RemoteName);
				continue;
			}
			if (count == 0) {
				if (strcmp(KeyName, LastKeyName) == 0 && FirstTime.Elapsed() < REPEATDELAY)
					continue; // skip keys coming in too fast
				if (repeat) {
					event.name = LastKeyName;
					event.repeat = false;
					event.release = true;
					m_pump.send(event);
				}
				strcpy(LastKeyName, KeyName);
				repeat = false;
				FirstTime.Set();
				timeout = -1;
			}
			else {
				if (LastTime.Elapsed() < REPEATFREQ)
					continue; // repeat function kicks in after a short delay (after last key instead of first key)
				if (FirstTime.Elapsed() < REPEATDELAY)
					continue; // skip keys coming in too fast (for count != 0 as well)
				repeat = true;
			}
			//eDebug("Count : %2d", count);
			if (((count != 1) || (IGNOREFIRSTREPEAT == false)) && ((count + REPEATCOUNT) % REPEATCOUNT) == 0) {
				LastTime.Set();
				event.name = KeyName;
				event.repeat = repeat;
				event.release = false;
				m_pump.send(event);
			}
		}
		else if (repeat) { // the last one was a repeat, so let's generate a release
			if (LastTime.Elapsed() >= REPEATTIMEOUT) {
				event.name = LastKeyName;
				event.repeat = false;
				event.release = true;
				m_pump.send(event);
				repeat = false;
				*LastKeyName = 0;
				timeout = -1;
			}
		}
	}
}

void eLircInputDriver::keyPressed(const lircEvent &event)
{
	if (!enabled || input->islocked())
		return;

	std::list<eRCDevice*>::iterator i(listeners.begin());
	while (i != listeners.end()) {
		(*i)->handleCode((long)&event);
		++i;
	}
}

class eRCLircInit
{
private:
	eLircInputDriver driver;
	eLircInputDevice device;

public:
	eRCLircInit(): driver(), device(&driver)
	{
	}
};

eAutoInitP0<eRCLircInit> init_rcLirc(eAutoInitNumbers::rc+1, "Lirc RC Driver");
