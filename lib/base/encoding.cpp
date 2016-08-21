#include <cstdio>
#include <cstdlib>
#include <lib/base/cfile.h>
#include <lib/base/encoding.h>
#include <lib/base/eerror.h>
#include <lib/base/eenv.h>

eDVBTextEncodingHandler encodingHandler;  // the one and only instance
int defaultEncodingTable = 1;   // the one and only instance

inline char toupper(char c)
{
	return (c >= 'a' && c <= 'z') ? c - ('a' - 'A') : c;
}

int mapEncoding(char *s_table)
{
	int encoding = 0;

	// table name will be in uppercase!
	if (sscanf(s_table, "ISO8859-%d", &encoding) == 1)
		return encoding;
	if (sscanf(s_table, "ISO%d", &encoding) == 1 and encoding == 6937)
		return 0;
	if (strcmp(s_table, "GB2312") == 0 || strcmp(s_table, "GBK") == 0
		|| strcmp(s_table, "GB18030") == 0 || strcmp(s_table, "CP936") == 0)
		return GB18030_ENCODING;
	if (strcmp(s_table, "BIG5") == 0 || strcmp(s_table, "CP950") == 0)
		return BIG5_ENCODING;
	if (strcmp(s_table, "UTF8") == 0 || strcmp(s_table, "UTF-8") == 0)
		return UTF8_ENCODING;
	if (strcmp(s_table, "UNICODE") == 0)
		return UNICODE_ENCODING;
	if (strcmp(s_table, "UTF16BE") == 0)
		return UTF16BE_ENCODING;
	if (strcmp(s_table, "UTF16LE") == 0)
		return UTF16LE_ENCODING;
	else
		eDebug("[eDVBTextEncodingHandler] unsupported table in encoding.conf: %s. ", s_table);
	return -1;
}

eDVBTextEncodingHandler::eDVBTextEncodingHandler()
{
	std::string file = eEnv::resolve("${sysconfdir}/enigma2/encoding.conf");
	if (::access(file.c_str(), R_OK) < 0)
	{
		/* no personalized encoding.conf, fallback to the system default */
		file = eEnv::resolve("${datadir}/enigma2/encoding.conf");
	}
	CFile f(file.c_str(), "rt");

	if (f)
	{
		size_t bufsize = 256;
		char *line = (char*) malloc(bufsize);
		char countrycode[bufsize];
		char *s_table = (char*) malloc(bufsize);
		while (getline(&line, &bufsize, f) != -1)
		{
			int i, j = 0;	   // remove leading whitespace and control chars, and comments
			for(i = 0; line[i]; i++){
				if (line[i] == '#')
					break; // skip rest of line
				if (j == 0 && line[i] > 0 && line[i] <= ' ')
					continue;       //skip non-printable char and whitespace in head
				line[j++] = toupper(line[i]); // so countrycodes are always uppercase
			}
			if (j == 0)
				continue;       // skip 'empty' lines
			line[j] = 0;

			int tsid, onid, encoding = 0;
			if (sscanf(line, "0X%x 0X%x %s", &tsid, &onid, s_table) == 3
				  || sscanf(line, "%d %d %s", &tsid, &onid, s_table) == 3 ) {
				encoding = mapEncoding(s_table);
				if (encoding >= 0)
					m_TransponderDefaultMapping[(tsid<<16)|onid] = encoding;
			}
			else if (sscanf(line, "0X%x 0X%x", &tsid, &onid) == 2
					|| sscanf(line, "%d %d", &tsid, &onid) == 2 ) {
				m_TransponderUseTwoCharMapping.insert((tsid<<16)|onid);
			}
			else if (sscanf(line, "%s %s", countrycode, s_table) == 2 ) {
				encoding = mapEncoding(s_table);
				if (encoding >= 0)
					m_TransponderDefaultMapping[(tsid<<16)|onid] = encoding;

				if (countrycode[0] == '*')
					defaultEncodingTable = encoding;
				else
					m_CountryCodeDefaultMapping[countrycode] = encoding;
			}
			else
				encoding = -1;

			if (encoding == -1)
				eDebug("[eDVBTextEncodingHandler] encoding.conf: couldn't parse %s", line);
		}
		free(line);
		free(s_table);
	}
	else
		eDebug("[eDVBTextEncodingHandler] couldn't open %s: %m", file.c_str());
}

void eDVBTextEncodingHandler::getTransponderDefaultMapping(int tsidonid, int &table)
{
	std::map<int, int>::iterator it =
		m_TransponderDefaultMapping.find(tsidonid);
	if ( it != m_TransponderDefaultMapping.end() )
		table = it->second;
}

bool eDVBTextEncodingHandler::getTransponderUseTwoCharMapping(int tsidonid)
{
	return m_TransponderUseTwoCharMapping.find(tsidonid) != m_TransponderUseTwoCharMapping.end();
}

int eDVBTextEncodingHandler::getCountryCodeDefaultMapping( const std::string &country_code )
{
	std::map<std::string, int>::iterator it =
		m_CountryCodeDefaultMapping.find(country_code);
	if ( it != m_CountryCodeDefaultMapping.end() )
		return it->second;
	return defaultEncodingTable;
}
