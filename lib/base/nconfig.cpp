#include <lib/base/nconfig.h>
#include <lib/base/eenv.h>
#include <fstream>

eConfigManager *eConfigManager::instance = NULL;

eConfigManager::eConfigManager()
{
	instance = this;
}

eConfigManager::~eConfigManager()
{
	instance = NULL;
}

eConfigManager *eConfigManager::getInstance()
{
	return instance;
}

std::string eConfigManager::getConfigValue(const char *key)
{
	return instance ? instance->getConfig(key) : "";
}

int eConfigManager::getConfigIntValue(const char *key, int defaultvalue)
{
	std::string value = getConfigValue(key);
	return (value != "") ? atoi(value.c_str()) : defaultvalue;
}

bool eConfigManager::getConfigBoolValue(const char *key, bool defaultvalue)
{
	std::string value = getConfigValue(key);
	if (value == "True" || value == "true") return true;
	if (value == "False" || value == "false") return false;
	return defaultvalue;
}

const std::string eConfigManager::getConfigString(const std::string &key, const std::string &defaultValue)
{
        std::string value = eConfigManager::getConfigValue(key.c_str());

        //we get at least the default value if python is still alive
        if (!value.empty())
                return value;

        value = defaultValue;

        // get value from enigma2 settings file
        std::ifstream in(eEnv::resolve("${sysconfdir}/enigma2/settings").c_str());
        if (in.good()) {
                do {
                        std::string line;
                        std::getline(in, line);
                        size_t size = key.size();
                        if (!line.compare(0, size, key) && line[size] == '=') {
                                value = line.substr(size + 1);
                                break;
                        }
                } while (in.good());
                in.close();
        }

        return value;
}
