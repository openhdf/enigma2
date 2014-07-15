#ifndef __base_condVar_h
#define __base_condVar_h

#include <pthread.h>

class cMutex {
  friend class cCondVar;
private:
  pthread_mutex_t mutex;
  int locked;
public:
  cMutex(void);
  ~cMutex();
  void Lock(void);
  void Unlock(void);
};

class cCondVar {
private:
  pthread_cond_t cond;
public:
  cCondVar(void);
  ~cCondVar();
  void Wait(cMutex &Mutex);
  bool TimedWait(cMutex &Mutex, int TimeoutMs);
  void Broadcast(void);
};

class cCondWait {
private:
  pthread_mutex_t mutex;
  pthread_cond_t cond;
  bool signaled;
public:
  cCondWait(void);
  ~cCondWait();
  static void SleepMs(int TimeoutMs);
  bool Wait(int TimeoutMs = 0);
  void Signal(void);
};

class cMutexLock {
private:
  cMutex *mutex;
  bool locked;
public:
  cMutexLock(cMutex *Mutex = NULL);
  ~cMutexLock();
  bool Lock(cMutex *Mutex);
};

class cTimeMs {
private:
  uint64_t begin;
public:
  cTimeMs(int Ms = 0);
      ///< Creates a timer with ms resolution and an initial timeout of Ms.
  static uint64_t Now(void);
  void Set(int Ms = 0);
  bool TimedOut(void);
  uint64_t Elapsed(void);
};

#endif
