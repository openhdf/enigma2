#include <lib/base/cfile.h>
#include <lib/base/eerror.h>
#include <lib/base/elock.h>
#include <cstdarg>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <time.h>

#include <string>
#include <ansidebug.h>

#ifdef MEMLEAK_CHECK
AllocList *allocList;
pthread_mutex_t memLock =
	PTHREAD_RECURSIVE_MUTEX_INITIALIZER_NP;

void DumpUnfreed()
{
	AllocList::iterator i;
	unsigned int totalSize = 0;

	if(!allocList)
		return;

	CFile f("/tmp/enigma2_mem.out", "w");
	if (!f)
		return;
	size_t len = 1024;
	char *buffer = (char*)malloc(1024);
	for(i = allocList->begin(); i != allocList->end(); i++)
	{
		unsigned int tmp;
		fprintf(f, "%s\tLINE %d\tADDRESS %p\t%d unfreed\ttype %d (btcount %d)\n",
			i->second.file, i->second.line, (void*)i->second.address, i->second.size, i->second.type, i->second.btcount);
		totalSize += i->second.size;

		char **bt_string = backtrace_symbols( i->second.backtrace, i->second.btcount );
		for ( tmp=0; tmp < i->second.btcount; tmp++ )
		{
			if ( bt_string[tmp] )
			{
				char *beg = strchr(bt_string[tmp], '(');
				if ( beg )
				{
					std::string tmp1(beg+1);
					int pos1=tmp1.find('+'), pos2=tmp1.find(')');
					if ( pos1 != std::string::npos && pos2 != std::string::npos )
					{
						std::string tmp2(tmp1.substr(pos1,(pos2-pos1)));
						tmp1.erase(pos1);
						if (tmp1.length())
						{
							int state;
							abi::__cxa_demangle(tmp1.c_str(), buffer, &len, &state);
							if (!state)
								fprintf(f, "%d %s%s\n", tmp, buffer,tmp2.c_str());
							else
								fprintf(f, "%d %s\n", tmp, bt_string[tmp]);
						}
					}
				}
				else
					fprintf(f, "%d %s\n", tmp, bt_string[tmp]);
			}
		}
		free(bt_string);
		if (i->second.btcount)
			fprintf(f, "\n");
	}
	free(buffer);

	fprintf(f, "-----------------------------------------------------------\n");
	fprintf(f, "Total Unfreed: %d bytes\n", totalSize);
	fflush(f);
};
#endif

Signal2<void, int, const std::string&> logOutput;
int logOutputConsole = 1;
int logOutputColors = 1;

static pthread_mutex_t DebugLock =
	PTHREAD_ADAPTIVE_MUTEX_INITIALIZER_NP;


static const char *alertToken[] = {
// !!! all strings must be written in lower case !!!
	"error",
	"fail",
	"not available",
	"no module",
	"no such file",
	"cannot",
	"invalid",
	"bad parameter",
	"not found",
	NULL		//end of list
};

static const char *warningToken[] = {
// !!! all strings must be written in lower case !!!
	"warning",
	"unknown",
	NULL		//end of list
};

bool findToken(char *src, const char **list)
{
	bool res = false;
	if(!src || !list)
		return res;

	char *tmp = new char[strlen(src)+1];
	if(!tmp)
		return res;
	int idx=0;
	do{
		tmp[idx] = tolower(src[idx]);
	}while(src[idx++]);

	for(idx=0; list[idx]; idx++)
	{
		if(strstr(tmp, list[idx]))
		{
			res = true;
			break;
		}
	}
	delete [] tmp;
	return res;
}

void removeAnsiEsc(char *src)
{
	char *dest = src;
	bool cut = false;
	for(; *src; src++)
	{
		if (*src == (char)0x1b) cut = true;
		if (!cut) *dest++ = *src;
		if (*src == 'm' || *src == 'K') cut = false;
	}
	*dest = '\0';
}

void removeAnsiEsc(char *src, char *dest)
{
	bool cut = false;
	for(; *src; src++)
	{
		if (*src == (char)0x1b) cut = true;
		if (!cut) *dest++ = *src;
		if (*src == 'm' || *src == 'K') cut = false;
	}
	*dest = '\0';
}

char *printtime(char buffer[], int size)
{
	struct tm loctime ;
	struct timeval tim;
	gettimeofday(&tim, NULL);
	localtime_r(&tim.tv_sec, &loctime);
	snprintf(buffer, size, "%02d:%02d:%02d.%03ld", loctime.tm_hour, loctime.tm_min, loctime.tm_sec, tim.tv_usec / 1000L);
	return buffer;
}

extern void bsodFatal(const char *component);

void eFatal(const char *file, int line, const char *function, const char* fmt, ...)
{
	char buf[1024];
	va_list ap;
	va_start(ap, fmt);
	vsnprintf(buf, 1024, fmt, ap);
	va_end(ap);
	{
		singleLock s(DebugLock);
		logOutput(lvlFatal, "FATAL: " + std::string(buf) + "\n");
		fprintf(stderr, "FATAL: %s\n",buf );
	}
	bsodFatal("enigma2");
}

#ifdef DEBUG
void eDebug(const char* fmt, ...)
{
	char buf[1024];
	va_list ap;
	va_start(ap, fmt);
	vsnprintf(buf, 1024, fmt, ap);
	va_end(ap);
	singleLock s(DebugLock);
	logOutput(lvlDebug, std::string(buf) + "\n");
	if (logOutputConsole)
		fprintf(stderr, "%s\n", buf);
}

void eDebugNoNewLine(const char* fmt, ...)
{
	char buf[1024];
	va_list ap;
	va_start(ap, fmt);
	vsnprintf(buf, 1024, fmt, ap);
	va_end(ap);
	singleLock s(DebugLock);
	logOutput(lvlDebug, buf);
	if (logOutputConsole)
		fprintf(stderr, "%s", buf);
}

void eWarning(const char* fmt, ...)
{
	char buf[1024];
	va_list ap;
	va_start(ap, fmt);
	vsnprintf(buf, 1024, fmt, ap);
	va_end(ap);
	singleLock s(DebugLock);
	logOutput(lvlWarning, std::string(buf) + "\n");
	if (logOutputConsole)
		fprintf(stderr, "%s\n", buf);
}
#endif // DEBUG

void ePythonOutput(const char *string)
{
#ifdef DEBUG
	singleLock s(DebugLock);
	logOutput(lvlWarning, string);
	if (logOutputConsole)
		fwrite(string, 1, strlen(string), stderr);
#endif
}

void eWriteCrashdump()
{
		/* implement me */
}
