#include <lib/dvb/dvb.h>
#include <lib/dvb/sec.h>
#include <lib/dvb/rotor_calc.h>
#include <lib/dvb/dvbtime.h>

#include <set>

#include <lib/base/eerror.h>

#define SEC_DEBUG

#ifdef SEC_DEBUG
#define eSecDebug(arg...) eDebug(arg)
#else
#define eSecDebug(arg...)
#endif

extern const uint32_t crc32_table[256];

DEFINE_REF(eDVBSatelliteEquipmentControl);

eDVBSatelliteEquipmentControl *eDVBSatelliteEquipmentControl::instance;

int eDVBSatelliteEquipmentControl::m_params[MAX_PARAMS];
/*
   defaults are set in python lib/python/Components/NimManager.py
   in InitSecParams function via setParam call
*/

void eDVBSatelliteEquipmentControl::setParam(int param, int value)
{
	if (param >= 0 && param < MAX_PARAMS)
		m_params[param]=value;
}

eDVBSatelliteEquipmentControl::eDVBSatelliteEquipmentControl(eSmartPtrList<eDVBRegisteredFrontend> &avail_frontends, eSmartPtrList<eDVBRegisteredFrontend> &avail_simulate_frontends)
	:m_lnbidx((sizeof(m_lnbs) / sizeof(eDVBSatelliteLNBParameters))-1), m_curSat(m_lnbs[0].m_satellites.end()), m_avail_frontends(avail_frontends), m_avail_simulate_frontends(avail_simulate_frontends), m_rotorMoving(0),
	m_not_linked_slot_mask(0), m_canMeasureInputPower(false)
{
	if (!instance)
		instance = this;
	clear();
}

#define eSecDebugNoSimulate(x...) \
	do { \
		if (!simulate) \
		{ \
			eSecDebug(x); \
		} \
	} while(0)

/**
 * @brief find best possible lnb for the current tune request
 *
 * @param sat reference to current sattelite parameters
 * @param fe reference to current frontend
 * @param slot_id representation of the slotnumber as an bitmask ( 1 << slotnumber)
 * @param highest_score_lnb index of lnb with highest score
 * @return score of lnb stored in highest_score_lnb
 */
int eDVBSatelliteEquipmentControl::canTune(const eDVBFrontendParametersSatellite &sat, iDVBFrontend *fe, int slot_id, int *highest_score_lnb)
{
	bool simulate = ((eDVBFrontend*)fe)->is_simulate();
	bool direct_connected = m_not_linked_slot_mask & slot_id;
	int score=0, satcount=0;
	long linked_prev_ptr=-1, linked_next_ptr=-1, linked_csw=-1, linked_ucsw=-1, linked_toneburst=-1,
		fe_satpos_depends_ptr=-1, fe_rotor_pos=-1;
	bool linked_in_use = false;

	eSecDebugNoSimulate("direct_connected %d", !!direct_connected);

	fe->getData(eDVBFrontend::LINKED_PREV_PTR, linked_prev_ptr);
	fe->getData(eDVBFrontend::LINKED_NEXT_PTR, linked_next_ptr);
	fe->getData(eDVBFrontend::SATPOS_DEPENDS_PTR, fe_satpos_depends_ptr);

	// first we search the linkage base frontend and check if any tuner in prev direction is used
	while (linked_prev_ptr != -1)
	{
		eDVBRegisteredFrontend *linked_fe = (eDVBRegisteredFrontend*) linked_prev_ptr;
		if (linked_fe->m_inuse)
			linked_in_use = true;
		fe = linked_fe->m_frontend;
		linked_fe->m_frontend->getData(eDVBFrontend::LINKED_PREV_PTR, (long&)linked_prev_ptr);
	}

	fe->getData(eDVBFrontend::ROTOR_POS, fe_rotor_pos);

	// now check also the linked tuners  is in use
	while (!linked_in_use && linked_next_ptr != -1)
	{
		eDVBRegisteredFrontend *linked_fe = (eDVBRegisteredFrontend*) linked_next_ptr;
		if (linked_fe->m_inuse)
			linked_in_use = true;
		linked_fe->m_frontend->getData(eDVBFrontend::LINKED_NEXT_PTR, (long&)linked_next_ptr);
	}

	// when a linked in use tuner is found we get the tuner data...
	if (linked_in_use)
	{
		fe->getData(eDVBFrontend::CSW, linked_csw);
		fe->getData(eDVBFrontend::UCSW, linked_ucsw);
		fe->getData(eDVBFrontend::TONEBURST, linked_toneburst);
	}

	const dvb_frontend_info fe_info = ((eDVBFrontend*)fe)->getFrontendInfo(SYS_DVBS);
	if (highest_score_lnb)
		*highest_score_lnb = -1;

	eSecDebugNoSimulate("canTune %d", slot_id);


	for (int idx=0; idx <= m_lnbidx; ++idx )
	{
		bool rotor=false;
		eDVBSatelliteLNBParameters &lnb_param = m_lnbs[idx];
		bool is_unicable = lnb_param.SatCR_idx != -1;
		bool is_unicable_position_switch = lnb_param.SatCR_positions > 1;

		if ( lnb_param.m_slot_mask & slot_id ) // lnb for correct tuner?
		{
			int ret = 0;
			eDVBSatelliteDiseqcParameters &di_param = lnb_param.m_diseqc_parameters;

			eSecDebugNoSimulate("lnb %d found", idx);

			satcount += lnb_param.m_satellites.size();

			std::pair<std::multimap<int, eDVBSatelliteSwitchParameters>::iterator, std::multimap<int, eDVBSatelliteSwitchParameters>::iterator> ii;
			ii = lnb_param.m_satellites.equal_range(sat.orbital_position);

			std::multimap<int, eDVBSatelliteSwitchParameters>::iterator sit;
//				lnb_param.m_satellites.find(sat.orbital_position);

			eSecDebugNoSimulate("%d option(s) at position %d", lnb_param.m_satellites.count(sat.orbital_position), sat.orbital_position);

			if (lnb_param.m_satellites.count(sat.orbital_position))
			{
				for(sit = ii.first; sit != ii.second; ++sit)
				{
					bool diseqc=false;
					long band=0,
						satpos_depends_ptr=fe_satpos_depends_ptr,
						csw = di_param.m_committed_cmd,
						ucsw = di_param.m_uncommitted_cmd,
						toneburst = di_param.m_toneburst_param,
						rotor_pos = fe_rotor_pos;

					eSecDebugNoSimulate("sat %d found", sat.orbital_position);

					/* Dishpro bandstacking HACK */
					if (lnb_param.m_lof_threshold == 1000)
					{
						if (!(sat.polarisation & eDVBFrontendParametersSatellite::Polarisation_Vertical))
						{
							band |= 1;
						}
						band |= 2; /* voltage always 18V for Dishpro */
					}
					else
					{
						if ( sat.frequency > lnb_param.m_lof_threshold )
							band |= 1;
						if (!(sat.polarisation & eDVBFrontendParametersSatellite::Polarisation_Vertical))
							band |= 2;
					}

					if (di_param.m_diseqc_mode >= eDVBSatelliteDiseqcParameters::V1_0)
					{
						diseqc=true;
						if ( di_param.m_committed_cmd < eDVBSatelliteDiseqcParameters::SENDNO )
							csw = 0xF0 | (csw << 2);

						if (di_param.m_committed_cmd <= eDVBSatelliteDiseqcParameters::SENDNO)
							csw |= band;

						if ( di_param.m_diseqc_mode == eDVBSatelliteDiseqcParameters::V1_2 )  // ROTOR
							rotor = true;

						ret = 10000;
					}
					else
					{
						csw = band;
						ret = 15000;
					}

					if (sat.no_rotor_command_on_tune && !rotor) {
						eSecDebugNoSimulate("no rotor but no_rotor_command_on_tune is set.. ignore lnb %d", idx);
						continue;
					}

					eSecDebugNoSimulate("ret1 %d", ret);

					if (linked_in_use && !is_unicable)
					{
						// compare tuner data
						if ( (csw != linked_csw) ||
							( diseqc && (ucsw != linked_ucsw || toneburst != linked_toneburst) ) ||
							( rotor && rotor_pos != sat.orbital_position ) )
						{
							ret = 0;
						}
						else
							ret += 15;
						eSecDebugNoSimulate("ret2 %d", ret);
					}
					else if ((rotor && satpos_depends_ptr != -1) && !(is_unicable && is_unicable_position_switch))
					{
						eSecDebugNoSimulate("satpos depends");
						eDVBRegisteredFrontend *satpos_depends_to_fe = (eDVBRegisteredFrontend*) satpos_depends_ptr;
						if (direct_connected) // current fe is direct connected.. (can turn the rotor)
						{
							if (satpos_depends_to_fe->m_inuse) // if the dependent frontend is in use?
							{
								if (rotor_pos != sat.orbital_position) // new orbital position not equal to current orbital pos?
									ret = 0;
								else
									ret += 10;
							}
							eSecDebugNoSimulate("ret3 %d", ret);
						}
						else // current fe is dependent of another tuner ... (so this fe can't turn the rotor!)
						{
							// get current orb pos of the tuner with rotor connection
							satpos_depends_to_fe->m_frontend->getData(eDVBFrontend::ROTOR_POS, rotor_pos);
							if (rotor_pos == -1 /* we dont know the rotor position yet */
								|| rotor_pos != sat.orbital_position ) // not the same orbital position?
							{
								ret = 0;
							}
						}
						eSecDebugNoSimulate("ret4 %d", ret);
					}

					if (ret && rotor && rotor_pos != -1)
						ret -= abs(rotor_pos-sat.orbital_position);

					eSecDebugNoSimulate("ret5 %d", ret);

					if (ret && !is_unicable)
					{
						int lof = sat.frequency > lnb_param.m_lof_threshold ?
							lnb_param.m_lof_hi : lnb_param.m_lof_lo;
						int tuner_freq = abs(sat.frequency - lof);
						if (tuner_freq < fe_info.frequency_min || tuner_freq > fe_info.frequency_max)
						{
							eSecDebugNoSimulate("can't tune! tuner frequency %d not in range: frequency_min %d frequency_max %d", tuner_freq, fe_info.frequency_min, fe_info.frequency_max);
							ret = 0;
						}
					}

					if (ret && lnb_param.m_prio != -1)
						ret = lnb_param.m_prio;

					eSecDebugNoSimulate("ret %d, score old %d", ret, score);
					if (ret > score)
					{
						score = ret;
						if (highest_score_lnb)
							*highest_score_lnb = idx;
					}
					eSecDebugNoSimulate("score new %d", score);
				}

			}
		}
	}
	if (score && satcount)
	{
		if (score > (satcount-1))
			score -= (satcount-1);
		else
			score = 1; // min score
	}
	if (score && direct_connected)
		score += 5; // increase score for tuners with direct sat connection
	eSecDebugNoSimulate("final score %d", score);
	return score;
}

bool need_turn_fast(int turn_speed)
{
	if (turn_speed == eDVBSatelliteRotorParameters::FAST)
		return true;
	else if (turn_speed != eDVBSatelliteRotorParameters::SLOW)
	{
		int begin = turn_speed >> 16; // high word is start time
		int end = turn_speed&0xFFFF; // low word is end time
		time_t now_time = ::time(0);
		tm nowTime;
		localtime_r(&now_time, &nowTime);
		int now = (nowTime.tm_hour + 1) * 60 + nowTime.tm_min + 1;
		bool neg = end <= begin;
		if (neg) {
			int tmp = begin;
			begin = end;
			end = tmp;
		}
		if ((now >= begin && now < end) ^ neg)
			return true;
	}
	return false;
}

#define VOLTAGE(x) (lnb_param.m_increased_voltage ? iDVBFrontend::voltage##x##_5 : iDVBFrontend::voltage##x)

#define eDebugNoSimulate(x...) \
	do { \
		if (!simulate) \
			eDebug(x); \
	} while(0)

//round value to multiple of m
int roundMulti(int value, int m)
{
	volatile int tmp = (m + 2 * value) / (2 * m);
	return (m * tmp);
}

int heterodyne(iDVBFrontend &frontend, int rf, int lof)
{
	long inv;
	int ifreq = rf - lof;
	if (ifreq < 0)
	{
		ifreq = -ifreq;
		frontend.getData(eDVBFrontend::SPECTINV_CNT, inv);
		frontend.setData(eDVBFrontend::SPECTINV_CNT, ++inv);
	}
	return ifreq;
}

RESULT eDVBSatelliteEquipmentControl::prepareRFmagicCSS(iDVBFrontend &frontend, eDVBSatelliteLNBParameters &lnb_param, long band, int ifreq, int &tunerfreq, unsigned int &tuningword, int guard_offset)
{
	bool simulate = ((eDVBFrontend*)&frontend)-> is_simulate();
	int vco = roundMulti(lnb_param.SatCRvco + guard_offset + ifreq, 1000);
	tunerfreq = heterodyne(frontend, ifreq, vco);
	unsigned int positions = lnb_param.SatCR_positions ? lnb_param.SatCR_positions : 1;
	unsigned int posnum = (lnb_param.SatCR_positionnumber > 0)										// position == 0 -> use first position
				&& (lnb_param.SatCR_positionnumber <= MAX_EN50607_POSITIONS) ?  lnb_param.SatCR_positionnumber - 1 : 0;

	tuningword = (((roundMulti(vco - lnb_param.SatCRvco - 2*guard_offset - 100000, 1000)/1000)&0x07FF)<<8)
			| (band & 0x3)						//Bit0:HighLow  Bit1:VertHor
			| ((posnum & 0x3F) << 2)				//position number (0..63)
			| ((lnb_param.SatCR_idx & 0x1F) << 19);			//addresse of SatCR (0..31)

	eDebugNoSimulate("polarisation: %c band: %c position: %d satcr: %d tunerfreq: %dMHz vco: %dMHz tuningword 0x%06x" \
		, (band & 2)?'H':'V', (band & 1)?'H':'L', posnum, lnb_param.SatCR_idx, tunerfreq/1000, vco /1000, tuningword);
	return vco;
}

RESULT eDVBSatelliteEquipmentControl::prepareSTelectronicSatCR(iDVBFrontend &frontend, eDVBSatelliteLNBParameters &lnb_param, long band, int ifreq, int &tunerfreq, unsigned int &tuningword, int guard_offset)
{
	bool simulate = ((eDVBFrontend*)&frontend)->is_simulate();
	int vco = roundMulti(lnb_param.SatCRvco + ifreq + guard_offset, 4000);
	tunerfreq = heterodyne(frontend, ifreq, vco);
	unsigned int positions = lnb_param.SatCR_positions ? lnb_param.SatCR_positions : 1;
	unsigned int posnum = (lnb_param.SatCR_positionnumber > 0)							// position == 0 -> use position A
				&& (lnb_param.SatCR_positionnumber <= MAX_FIXED_LNB_POSITIONS) 				// rotor with unicablelnb -> use only position A
				&& (positions > 1)									// has only one position -> use only position A
				&& ((lnb_param.SatCR_positionnumber - 1) % positions) ?  1 : 0;				// odd numbers use position A; even numbers use position B

	tuningword = ((vco - 1400000)/4000)
			|(posnum << 12)
			|((band & 3) <<10)
			|((lnb_param.SatCR_idx & 7) << 13);

	eDebugNoSimulate("polarisation: %c band: %c position: %d satcr: %d tunerfreq: %dMHz vco: %dMHz tuningword 0x%04x" \
		, (band & 2)?'H':'V', (band & 1)?'H':'L', posnum, lnb_param.SatCR_idx, tunerfreq/1000, vco /1000, tuningword);
	return  vco;
}


/**
 * @brief prepare for tune
 * 
 * @param frontend reference to current frontend
 * @param sat reference to current sattelite parameters
 * @param frequency reference to tuner frequency. Initial value is ignored, committing new frequency on tuner
 * @param slot_id representation of the slotnumber as an bitmask ( 1 << slotnumber)
 * @param tunetimeout 5000 ms currenly hardcoded in eDVBFrontend::tune()
 * @return RESULT
 */
RESULT eDVBSatelliteEquipmentControl::prepare(iDVBFrontend &frontend, const eDVBFrontendParametersSatellite &sat, int &frequency, int slot_id, unsigned int tunetimeout)
{
	bool simulate = ((eDVBFrontend*)&frontend)->is_simulate();
	int lnb_idx = -1;

	if (canTune(sat, &frontend, slot_id, &lnb_idx))
	{
		eDVBSatelliteLNBParameters &lnb_param = m_lnbs[lnb_idx];
		eDVBSatelliteDiseqcParameters &di_param = lnb_param.m_diseqc_parameters;
		eDVBSatelliteRotorParameters &rotor_param = lnb_param.m_rotor_parameters;

		std::multimap<int, eDVBSatelliteSwitchParameters>::iterator sit =
			lnb_param.m_satellites.find(sat.orbital_position);
		if ( sit != lnb_param.m_satellites.end())
		{
			eSecCommandList sec_sequence;
			eDVBSatelliteSwitchParameters &sw_param = sit->second;
			bool doSetFrontend = true;
			bool doSetVoltageToneFrontend = true;
			bool forceChanged = false;
			bool needDiSEqCReset = false;
			long band=0,
				voltage = iDVBFrontend::voltageOff,
				tone = iDVBFrontend::toneOff,
				csw = di_param.m_committed_cmd,
				ucsw = di_param.m_uncommitted_cmd,
				toneburst = di_param.m_toneburst_param,
				lastcsw = -1,
				lastucsw = -1,
				lastToneburst = -1,
				lastRotorCmd = -1,
				curRotorPos = -1,
				satposDependPtr = -1;
			iDVBFrontend *sec_fe=&frontend;
			eDVBRegisteredFrontend *linked_fe = 0;
			eDVBSatelliteDiseqcParameters::t_diseqc_mode diseqc_mode = di_param.m_diseqc_mode;
			eDVBSatelliteSwitchParameters::t_voltage_mode voltage_mode = sw_param.m_voltage_mode;
			bool diseqc13V = voltage_mode == eDVBSatelliteSwitchParameters::HV_13;
			bool is_unicable = lnb_param.SatCR_idx != -1;
			frontend.setData(eDVBFrontend::SPECTINV_CNT, 0);

			bool useGotoXX = false;
			int RotorCmd=-1;
			int send_mask = 0;

			frontend.setData(eDVBFrontend::SATCR, lnb_param.SatCR_idx);

			if (diseqc13V)
				voltage_mode = eDVBSatelliteSwitchParameters::HV;

			frontend.getData(eDVBFrontend::SATPOS_DEPENDS_PTR, satposDependPtr);

			if (!(m_not_linked_slot_mask & slot_id))  // frontend with direct connection?
			{
				long linked_prev_ptr;
				frontend.getData(eDVBFrontend::LINKED_PREV_PTR, linked_prev_ptr);
				while (linked_prev_ptr != -1)
				{
					linked_fe = (eDVBRegisteredFrontend*) linked_prev_ptr;
					sec_fe = linked_fe->m_frontend;
					sec_fe->getData(eDVBFrontend::LINKED_PREV_PTR, (long&)linked_prev_ptr);
				}
				if (satposDependPtr != -1)  // we dont need uncommitted switch and rotor cmds on second output of a rotor lnb
					diseqc_mode = eDVBSatelliteDiseqcParameters::V1_0;
				else {
					// in eDVBFrontend::tuneLoop we call closeFrontend and ->inc_use() in this this condition (to put the kernel frontend thread into idle state)
					// so we must resend all diseqc stuff (voltage is disabled when the frontend is closed)
					int state;
					sec_fe->getState(state);
					if (!linked_fe->m_inuse && state != eDVBFrontend::stateIdle)
						forceChanged = true;
				}
			}

			sec_fe->getData(eDVBFrontend::CSW, lastcsw);
			sec_fe->getData(eDVBFrontend::UCSW, lastucsw);
			sec_fe->getData(eDVBFrontend::TONEBURST, lastToneburst);
			sec_fe->getData(eDVBFrontend::ROTOR_CMD, lastRotorCmd);
			sec_fe->getData(eDVBFrontend::ROTOR_POS, curRotorPos);

			if (lastcsw == lastucsw && lastToneburst == lastucsw && lastucsw == -1)
				needDiSEqCReset = true;

			/* Dishpro bandstacking HACK */
			if (lnb_param.m_lof_threshold == 1000)
			{
				if (!(sat.polarisation & eDVBFrontendParametersSatellite::Polarisation_Vertical))
				{
					band |= 1;
				}
				band |= 2; /* voltage always 18V for Dishpro */
			}
			else
			{
				if ( sat.frequency > lnb_param.m_lof_threshold )
					band |= 1;
				if (!(sat.polarisation & eDVBFrontendParametersSatellite::Polarisation_Vertical))
					band |= 2;
			}

			int lof = (band&1)?lnb_param.m_lof_hi:lnb_param.m_lof_lo;

			int ifreq = heterodyne(frontend, sat.frequency, lof);

			if(!is_unicable)
			{
				// calc Frequency
				frequency = roundMulti(ifreq, 125); //round to multiple of 125

				frontend.setData(eDVBFrontend::FREQ_OFFSET, lof);

				/* Dishpro bandstacking HACK */
				if (lnb_param.m_lof_threshold == 1000)
					voltage = VOLTAGE(18);
				else if ( voltage_mode == eDVBSatelliteSwitchParameters::_14V
					|| ( sat.polarisation & eDVBFrontendParametersSatellite::Polarisation_Vertical
						&& voltage_mode == eDVBSatelliteSwitchParameters::HV )  )
					voltage = VOLTAGE(13);
				else if ( voltage_mode == eDVBSatelliteSwitchParameters::_18V
					|| ( !(sat.polarisation & eDVBFrontendParametersSatellite::Polarisation_Vertical)
						&& voltage_mode == eDVBSatelliteSwitchParameters::HV )  )
					voltage = VOLTAGE(18);
				if ( (sw_param.m_22khz_signal == eDVBSatelliteSwitchParameters::ON)
					|| ( sw_param.m_22khz_signal == eDVBSatelliteSwitchParameters::HILO && (band&1) ) )
					tone = iDVBFrontend::toneOn;
				else if ( (sw_param.m_22khz_signal == eDVBSatelliteSwitchParameters::OFF)
					|| ( sw_param.m_22khz_signal == eDVBSatelliteSwitchParameters::HILO && !(band&1) ) )
					tone = iDVBFrontend::toneOff;
			}
			else
			{
				long curr_frq;
				long curr_sym;
				long curr_lof;
				long curr_band;

				frontend.getData(eDVBFrontend::CUR_FREQ, curr_frq);
				frontend.getData(eDVBFrontend::CUR_SYM, curr_sym);
				frontend.getData(eDVBFrontend::CUR_LOF, curr_lof);
				frontend.getData(eDVBFrontend::CUR_BAND, curr_band);

				int gfrq = curr_frq  > 0 ? abs(curr_frq - curr_lof) + (curr_sym*13)/20000 : 0;
				int gfrq_a = curr_frq  > 0 ? abs(curr_frq - curr_lof) - (curr_sym*13)/20000 : 0;

				frontend.setData(eDVBFrontend::CUR_FREQ, sat.frequency);
				frontend.setData(eDVBFrontend::CUR_SYM, sat.symbol_rate);
				frontend.setData(eDVBFrontend::CUR_LOF, lof);
				frontend.setData(eDVBFrontend::CUR_BAND, band);
				switch(lnb_param.SatCR_format)
				{
					case 1:
						eDebugNoSimulate("JESS (EN50607)");
						if(lnb_param.SatCR_switch_reliable)
						{
							long inv;
							frontend.getData(eDVBFrontend::SPECTINV_CNT, inv);
							prepareRFmagicCSS(frontend, lnb_param, curr_band, gfrq + 4000, frequency, lnb_param.GuardTuningWord, 0);
							prepareRFmagicCSS(frontend, lnb_param, curr_band, gfrq_a - 4000, frequency, lnb_param.GuardTuningWord_a, 0);
							frontend.setData(eDVBFrontend::SPECTINV_CNT, inv);
						}
						frontend.setData(eDVBFrontend::FREQ_OFFSET, lof + prepareRFmagicCSS(frontend, lnb_param, band, ifreq, frequency, lnb_param.TuningWord, 0));
						break;
					case 0:
					default:
						eDebugNoSimulate("Unicable (EN50494)");
						if(lnb_param.SatCR_switch_reliable)
						{
							long inv;
							frontend.getData(eDVBFrontend::SPECTINV_CNT, inv);
							prepareSTelectronicSatCR(frontend, lnb_param, curr_band, gfrq + 1000, frequency, lnb_param.GuardTuningWord, 0);
							prepareSTelectronicSatCR(frontend, lnb_param, curr_band, gfrq_a - 1000, frequency, lnb_param.GuardTuningWord_a, 0);
							frontend.setData(eDVBFrontend::SPECTINV_CNT, inv);
						}
						frontend.setData(eDVBFrontend::FREQ_OFFSET, lof + prepareSTelectronicSatCR(frontend, lnb_param, band, ifreq, frequency, lnb_param.TuningWord, 0));
				}
//				eDebugNoSimulate("[prepare] frequency %d",frequency);
				voltage = VOLTAGE(13);
			}

			if (diseqc_mode >= eDVBSatelliteDiseqcParameters::V1_0)
			{
				if ( di_param.m_committed_cmd < eDVBSatelliteDiseqcParameters::SENDNO )
					csw = 0xF0 | (csw << 2);

				if (di_param.m_committed_cmd <= eDVBSatelliteDiseqcParameters::SENDNO)
					csw |= band;

				bool send_csw =
					(di_param.m_committed_cmd != eDVBSatelliteDiseqcParameters::SENDNO);
				bool changed_csw = send_csw && (forceChanged || csw != lastcsw);

				bool send_ucsw =
					(di_param.m_uncommitted_cmd && diseqc_mode > eDVBSatelliteDiseqcParameters::V1_0);
				bool changed_ucsw = send_ucsw && (forceChanged || ucsw != lastucsw);

				bool send_burst =
					(di_param.m_toneburst_param != eDVBSatelliteDiseqcParameters::NO);
				bool changed_burst = send_burst && (forceChanged || toneburst != lastToneburst);

				/* send_mask
					1 must send csw
					2 must send ucsw
					4 send toneburst first
					8 send toneburst at end */
				if (changed_burst) // toneburst first and toneburst changed
				{
					if (di_param.m_command_order&1)
					{
						send_mask |= 4;
						if ( send_csw )
							send_mask |= 1;
						if ( send_ucsw )
							send_mask |= 2;
					}
					else
						send_mask |= 8;
				}
				if (changed_ucsw)
				{
					send_mask |= 2;
					if ((di_param.m_command_order&4) && send_csw)
						send_mask |= 1;
					if (di_param.m_command_order==4 && send_burst)
						send_mask |= 8;
				}
				if (changed_csw)
				{
					if ( di_param.m_use_fast
						&& di_param.m_committed_cmd < eDVBSatelliteDiseqcParameters::SENDNO
						&& (lastcsw & 0xF0)
						&& ((csw / 4) == (lastcsw / 4)) )
						eDebugNoSimulate("dont send committed cmd (fast diseqc)");
					else
					{
						send_mask |= 1;
						if (!(di_param.m_command_order&4) && send_ucsw)
							send_mask |= 2;
						if (!(di_param.m_command_order&1) && send_burst)
							send_mask |= 8;
					}
				}

#if 0
				eDebugNoNewLine("sendmask: ");
				for (int i=3; i >= 0; --i)
					if ( send_mask & (1<<i) )
						eDebugNoNewLine("1");
					else
						eDebugNoNewLine("0");
				eDebug("");
#endif
				if ( diseqc_mode == eDVBSatelliteDiseqcParameters::V1_2
					&& !sat.no_rotor_command_on_tune )
				{
					if (sw_param.m_rotorPosNum) // we have stored rotor pos?
						RotorCmd=sw_param.m_rotorPosNum;
					else  // we must calc gotoxx cmd
					{
						eDebugNoSimulate("Entry for %d,%d? not in Rotor Table found... i try gotoXX?", sat.orbital_position / 10, sat.orbital_position % 10 );
						useGotoXX = true;

						double	SatLon = abs(sat.orbital_position)/10.00,
								SiteLat = rotor_param.m_gotoxx_parameters.m_latitude,
								SiteLon = rotor_param.m_gotoxx_parameters.m_longitude;

						if ( rotor_param.m_gotoxx_parameters.m_la_direction == eDVBSatelliteRotorParameters::SOUTH )
							SiteLat = -SiteLat;

						if ( rotor_param.m_gotoxx_parameters.m_lo_direction == eDVBSatelliteRotorParameters::WEST )
							SiteLon = 360 - SiteLon;

						eDebugNoSimulate("siteLatitude = %lf, siteLongitude = %lf, %lf degrees", SiteLat, SiteLon, SatLon );
						double satHourAngle =
							calcSatHourangle( SatLon, SiteLat, SiteLon );
						eDebugNoSimulate("PolarmountHourAngle=%lf", satHourAngle );

						static int gotoXTable[10] =
							{ 0x00, 0x02, 0x03, 0x05, 0x06, 0x08, 0x0A, 0x0B, 0x0D, 0x0E };

						if (SiteLat >= 0) // Northern Hemisphere
						{
							int tmp=(int)round( fabs( 180 - satHourAngle ) * 10.0 );
							RotorCmd = (tmp/10)*0x10 + gotoXTable[ tmp % 10 ];

							if (satHourAngle < 180) // the east
								RotorCmd |= 0xE000;
							else					// west
								RotorCmd |= 0xD000;
						}
						else // Southern Hemisphere
						{
							if (satHourAngle < 180) // the east
							{
								int tmp=(int)round( fabs( satHourAngle ) * 10.0 );
								RotorCmd = (tmp/10)*0x10 + gotoXTable[ tmp % 10 ];
								RotorCmd |= 0xD000;
							}
							else // west
							{
								int tmp=(int)round( fabs( 360 - satHourAngle ) * 10.0 );
								RotorCmd = (tmp/10)*0x10 + gotoXTable[ tmp % 10 ];
								RotorCmd |= 0xE000;
							}
						}
						eDebugNoSimulate("RotorCmd = %04x", RotorCmd);
					}
				}

				if ( send_mask )
				{
					int diseqc_repeats = diseqc_mode > eDVBSatelliteDiseqcParameters::V1_0 ? di_param.m_repeats : 0;
					int vlt = iDVBFrontend::voltageOff;
					eSecCommand::pair compare;
					compare.steps = +3;
					compare.tone = iDVBFrontend::toneOff;
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_TONE_GOTO, compare) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_TONE, iDVBFrontend::toneOff) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_CONT_TONE_DISABLE_BEFORE_DISEQC]) );

					if (diseqc13V)
						vlt = iDVBFrontend::voltage13;
					else if ( RotorCmd != -1 && RotorCmd != lastRotorCmd )
					{
						if (rotor_param.m_inputpower_parameters.m_use && !is_unicable)
							vlt = VOLTAGE(18);  // in input power mode set 18V for measure input power
						else
							vlt = VOLTAGE(13);  // in normal mode start turning with 13V
					}
					else
						vlt = voltage;

					// check if voltage is already correct..
					compare.voltage = vlt;
					compare.steps = +7;
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_VOLTAGE_GOTO, compare) );

					// check if voltage is disabled
					compare.voltage = iDVBFrontend::voltageOff;
					compare.steps = +4;
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_VOLTAGE_GOTO, compare) );

					// voltage is changed... use DELAY_AFTER_VOLTAGE_CHANGE_BEFORE_SWITCH_CMDS
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, vlt) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_VOLTAGE_CHANGE_BEFORE_SWITCH_CMDS]) );
					sec_sequence.push_back( eSecCommand(eSecCommand::GOTO, +3) );

					// voltage was disabled.. use DELAY_AFTER_ENABLE_VOLTAGE_BEFORE_SWITCH_CMDS
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, vlt) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_ENABLE_VOLTAGE_BEFORE_SWITCH_CMDS]) );

					sec_sequence.push_back( eSecCommand(eSecCommand::INVALIDATE_CURRENT_SWITCHPARMS) );
					if (needDiSEqCReset)
					{
						eDVBDiseqcCommand diseqc;
						memset(diseqc.data, 0, MAX_DISEQC_LENGTH);
						diseqc.len = 3;
						diseqc.data[0] = 0xE0;
						diseqc.data[1] = 0;
						diseqc.data[2] = 0;
						// diseqc reset
						sec_sequence.push_back( eSecCommand(eSecCommand::SEND_DISEQC, diseqc) );
						sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_DISEQC_RESET_CMD]) );
						diseqc.data[2] = 3;
						// diseqc peripherial powersupply on
						sec_sequence.push_back( eSecCommand(eSecCommand::SEND_DISEQC, diseqc) );
						sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_DISEQC_PERIPHERIAL_POWERON_CMD]) );
					}

					for (int seq_repeat = 0; seq_repeat < (di_param.m_seq_repeat?2:1); ++seq_repeat)
					{
						if ( send_mask & 4 )
						{
							sec_sequence.push_back( eSecCommand(eSecCommand::SEND_TONEBURST, di_param.m_toneburst_param) );
							sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_TONEBURST]) );
						}

						int loops=0;

						if ( send_mask & 1 )
							++loops;
						if ( send_mask & 2 )
							++loops;

						loops <<= diseqc_repeats;

						for ( int i = 0; i < loops;)  // fill commands...
						{
							eDVBDiseqcCommand diseqc;
							memset(diseqc.data, 0, MAX_DISEQC_LENGTH);
							diseqc.len = 4;
							diseqc.data[0] = i ? 0xE1 : 0xE0;
							diseqc.data[1] = 0x10;
							if ( (send_mask & 2) && (di_param.m_command_order & 4) )
							{
								diseqc.data[2] = 0x39;
								diseqc.data[3] = ucsw;
							}
							else if ( send_mask & 1 )
							{
								diseqc.data[2] = 0x38;
								diseqc.data[3] = csw;
							}
							else  // no committed command confed.. so send uncommitted..
							{
								diseqc.data[2] = 0x39;
								diseqc.data[3] = ucsw;
							}
							sec_sequence.push_back( eSecCommand(eSecCommand::SEND_DISEQC, diseqc) );

							i++;
							if ( i < loops )
							{
								int cmd=0;
								if (diseqc.data[2] == 0x38 && (send_mask & 2))
									cmd=0x39;
								else if (diseqc.data[2] == 0x39 && (send_mask & 1))
									cmd=0x38;
								int tmp = m_params[DELAY_BETWEEN_DISEQC_REPEATS];
								if (cmd)
								{
									int delay = diseqc_repeats ? (tmp - 54) / 2 : tmp;  // standard says 100msek between two repeated commands
									sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, delay) );
									diseqc.data[2]=cmd;
									diseqc.data[3]=(cmd==0x38) ? csw : ucsw;
									sec_sequence.push_back( eSecCommand(eSecCommand::SEND_DISEQC, diseqc) );
									++i;
									if ( i < loops )
										sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, delay ) );
									else
										sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_LAST_DISEQC_CMD]) );
								}
								else  // delay 120msek when no command is in repeat gap
									sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, tmp) );
							}
							else
								sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_LAST_DISEQC_CMD]) );
						}

						if ( send_mask & 8 )  // toneburst at end of sequence
						{
							sec_sequence.push_back( eSecCommand(eSecCommand::SEND_TONEBURST, di_param.m_toneburst_param) );
							sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_TONEBURST]) );
						}

						if (di_param.m_seq_repeat && seq_repeat == 0)
							sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_BEFORE_SEQUENCE_REPEAT]) );
					}
				}
			}
			else
			{
				sec_sequence.push_back( eSecCommand(eSecCommand::INVALIDATE_CURRENT_SWITCHPARMS) );
				csw = band;
			}

			sec_fe->setData(eDVBFrontend::NEW_CSW, csw);
			sec_fe->setData(eDVBFrontend::NEW_UCSW, ucsw);
			sec_fe->setData(eDVBFrontend::NEW_TONEBURST, di_param.m_toneburst_param);

			if(is_unicable)
			{
				// check if voltage is disabled
				eSecCommand::pair compare;
				compare.steps = +3;
				compare.voltage = iDVBFrontend::voltageOff;
				sec_sequence.push_back( eSecCommand(eSecCommand::IF_NOT_VOLTAGE_GOTO, compare) );
				sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, VOLTAGE(13)) );
				sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_ENABLE_VOLTAGE_BEFORE_SWITCH_CMDS] ) );

				sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, VOLTAGE(18)) );
				sec_sequence.push_back( eSecCommand(eSecCommand::SET_TONE, iDVBFrontend::toneOff) );
				sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_VOLTAGE_CHANGE_BEFORE_SWITCH_CMDS]) );  // wait 20 ms after voltage change

				eDVBDiseqcCommand diseqc;
				memset(diseqc.data, 0, MAX_DISEQC_LENGTH);
				eDVBDiseqcCommand diseqc_a;
				memset(diseqc_a.data, 0, MAX_DISEQC_LENGTH);
				long oldSatcr, oldPin, oldDiction;

				frontend.getData(eDVBFrontend::SATCR, oldSatcr);
				frontend.getData(eDVBFrontend::PIN, oldPin);
				frontend.getData(eDVBFrontend::DICTION, oldDiction);

				if((oldSatcr == -1) || (oldSatcr != lnb_param.SatCR_idx))
				{
					frontend.setData(eDVBFrontend::LFSR, ((lnb_param.SatCR_idx +1) << 17) | ((lnb_param.SatCR_idx + 1) << 5));  //reinit LSFR
				}
				else
				{
					long lfsr;
					frontend.getData(eDVBFrontend::LFSR, lfsr);
					lfsr = (lfsr << 8) ^ crc32_table[((lfsr >> 24) ^ (lnb_param.SatCR_idx +1)) & 0xFF];
					frontend.setData(eDVBFrontend::LFSR, lfsr);
					tunetimeout += (lfsr & 0x3FF);		// add random value 0..1023 ms
				}
				eDebugNoSimulate("tune timeout %dms", tunetimeout);

				if((oldSatcr != -1) && (oldSatcr != lnb_param.SatCR_idx))
				{
					switch (oldDiction)
					{
						case 1:
							if(oldPin < 1)
							{
								diseqc.len = 4;
								diseqc.data[0] = 0x70;
							}
							else
							{
								diseqc.len = 5;
								diseqc.data[0] = 0x71;
								diseqc.data[4] = oldPin;
							}
							diseqc.data[1] = oldSatcr << 3;
							diseqc.data[2] = 0x00;
							diseqc.data[3] = 0x00;
							break;
						case 0:
						default:
							if(oldPin < 1)
							{
								diseqc.len = 5;
								diseqc.data[2] = 0x5A;
							}
							else
							{
								diseqc.len = 6;
								diseqc.data[2] = 0x5C;
								diseqc.data[5] = oldPin;
							}
							diseqc.data[0] = 0xE0;
							diseqc.data[1] = 0x10;
							diseqc.data[3] = oldSatcr << 5;
							diseqc.data[4] = 0x00;
							break;
					}
					sec_sequence.push_back( eSecCommand(eSecCommand::SEND_DISEQC, diseqc) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_LAST_DISEQC_CMD]) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, VOLTAGE(13)) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_BETWEEN_DISEQC_REPEATS]) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, VOLTAGE(18)) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_VOLTAGE_CHANGE_BEFORE_SWITCH_CMDS]) );
					frontend.setData(eDVBFrontend::SATCR, -1);
				}


				frontend.setData(eDVBFrontend::DICTION, lnb_param.SatCR_format);
//TODO				frontend.setData(eDVBFrontend::PIN, lnb_param.SatCR_pin);

//>>> HACK adenin20150421
				long pin = 0;
//<<<
//>>> TODO optimize this
				if(lnb_param.SatCR_switch_reliable)
				{
					switch(lnb_param.SatCR_format)
					{
						case 1: //JESS
							if(pin < 1)
							{
								diseqc.len = diseqc_a.len = 4;
								diseqc.data[0] = diseqc_a.data[0] = 0x70;
							}
							else
							{
								diseqc.len = diseqc_a.len = 5;
								diseqc.data[0] = diseqc_a.data[0] = 0x71;
								diseqc.data[4] = diseqc_a.data[4] = pin;
							}
							diseqc.data[1] = lnb_param.GuardTuningWord >> 16;
							diseqc.data[2] = lnb_param.GuardTuningWord >> 8;
							diseqc.data[3] = lnb_param.GuardTuningWord;

							diseqc_a.data[1] = lnb_param.GuardTuningWord_a >> 16;
							diseqc_a.data[2] = lnb_param.GuardTuningWord_a >> 8;
							diseqc_a.data[3] = lnb_param.GuardTuningWord_a;
							break;
						case 0: //DiSEqC
						default:
							if(pin < 1)
							{
								diseqc.len = diseqc_a.len = 5;
								diseqc.data[2] = diseqc_a.data[2] = 0x5A;
							}
							else
							{
								diseqc.len = diseqc_a.len = 6;
								diseqc.data[2] = diseqc_a.data[2] = 0x5C;
								diseqc.data[5] = diseqc_a.data[5] = pin;
							}
							diseqc.data[0] = diseqc_a.data[0] = 0xE0;
							diseqc.data[1] = diseqc_a.data[1] = 0x10;
							diseqc.data[3] = lnb_param.GuardTuningWord >> 8;
							diseqc.data[4] = lnb_param.GuardTuningWord;
							diseqc_a.data[3] = lnb_param.GuardTuningWord_a >> 8;
							diseqc_a.data[4] = lnb_param.GuardTuningWord_a;
					}
					frontend.setData(eDVBFrontend::SATCR, lnb_param.SatCR_idx);

					sec_sequence.push_back( eSecCommand(eSecCommand::IF_TUNER_UNLOCKED_GOTO, +12));	//skip all, if tuner unlocked
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_TIMEOUT, 4));
					sec_sequence.push_back( eSecCommand(eSecCommand::SEND_DISEQC, diseqc));
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, 25) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, VOLTAGE(13)));
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_VOLTAGE_CHANGE_BEFORE_SWITCH_CMDS]));
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, VOLTAGE(18)));
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_VOLTAGE_CHANGE_BEFORE_SWITCH_CMDS]));
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_TIMEOUT_GOTO, +4));	//skip all, if tuner unlocked
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_TUNER_UNLOCKED_GOTO, +3));	//skip all, if tuner unlocked
					sec_sequence.push_back( eSecCommand(eSecCommand::SEND_DISEQC, diseqc_a));
					sec_sequence.push_back( eSecCommand(eSecCommand::GOTO, -8));			//repeate until timeout
				}
//<<<
				switch(lnb_param.SatCR_format)
				{
					case 1: //JESS
						if(pin < 1)
						{
							diseqc.len = 4;
							diseqc.data[0] = 0x70;
							diseqc.data[1] = lnb_param.TuningWord >> 16;
							diseqc.data[2] = lnb_param.TuningWord >> 8;
							diseqc.data[3] = lnb_param.TuningWord;
						}
						else
						{
							diseqc.len = 5;
							diseqc.data[0] = 0x71;
							diseqc.data[4] = pin;
						}
						diseqc.data[1] = lnb_param.TuningWord >> 16;
						diseqc.data[2] = lnb_param.TuningWord >> 8;
						diseqc.data[3] = lnb_param.TuningWord;
						break;
					case 0: //DiSEqC
					default:
						if(pin < 1)
						{
							diseqc.len = 5;
							diseqc.data[2] = 0x5A;
						}
						else
						{
							diseqc.len = 6;
							diseqc.data[2] = 0x5C;
							diseqc.data[5] = pin;
						}
						diseqc.data[0] = 0xE0;
						diseqc.data[1] = 0x10;
						diseqc.data[3] = lnb_param.TuningWord >> 8;
						diseqc.data[4] = lnb_param.TuningWord;
				}
				frontend.setData(eDVBFrontend::SATCR, lnb_param.SatCR_idx);

				sec_sequence.push_back( eSecCommand(eSecCommand::SEND_DISEQC, diseqc) );
				sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_LAST_DISEQC_CMD]) );
				sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, VOLTAGE(13)) );
				if ( RotorCmd != -1 && RotorCmd != lastRotorCmd && !rotor_param.m_inputpower_parameters.m_use)
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_VOLTAGE_CHANGE_BEFORE_MOTOR_CMD]) );  // wait 150msec after voltage change
			}

			eDebugNoSimulate("RotorCmd %02x, lastRotorCmd %02lx", RotorCmd, lastRotorCmd);
			if ( RotorCmd != -1 && RotorCmd != lastRotorCmd )
			{
				int mrt = m_params[MOTOR_RUNNING_TIMEOUT]; // in seconds!
				eSecCommand::pair compare;
				if (!send_mask && !is_unicable)
				{
					compare.steps = +3;
					compare.tone = iDVBFrontend::toneOff;
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_TONE_GOTO, compare) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_TONE, iDVBFrontend::toneOff) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_CONT_TONE_DISABLE_BEFORE_DISEQC]) );

					compare.voltage = iDVBFrontend::voltageOff;
					compare.steps = +4;
					// the next is a check if voltage is switched off.. then we first set a voltage :)
					// else we set voltage after all diseqc stuff..
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_NOT_VOLTAGE_GOTO, compare) );

					if (rotor_param.m_inputpower_parameters.m_use)
						sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, VOLTAGE(18)) ); // set 18V for measure input power
					else
						sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, VOLTAGE(13)) ); // in normal mode start turning with 13V

					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_ENABLE_VOLTAGE_BEFORE_MOTOR_CMD]) ); // wait 750ms when voltage was disabled
					sec_sequence.push_back( eSecCommand(eSecCommand::GOTO, +9) );  // no need to send stop rotor cmd and recheck voltage
				}
				else
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_BETWEEN_SWITCH_AND_MOTOR_CMD]) ); // wait 700ms when diseqc changed

				eDVBDiseqcCommand diseqc;
				memset(diseqc.data, 0, MAX_DISEQC_LENGTH);
				diseqc.len = 3;
				diseqc.data[0] = 0xE0;
				diseqc.data[1] = 0x31;	// positioner
				diseqc.data[2] = 0x60;	// stop
				sec_sequence.push_back( eSecCommand(eSecCommand::IF_ROTORPOS_VALID_GOTO, +5) );
				sec_sequence.push_back( eSecCommand(eSecCommand::SEND_DISEQC, diseqc) );
				sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, 50) );
				sec_sequence.push_back( eSecCommand(eSecCommand::SEND_DISEQC, diseqc) );
				// wait 150msec after send rotor stop cmd
				sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_MOTOR_STOP_CMD]) );

				diseqc.data[0] = 0xE0;
				diseqc.data[1] = 0x31;		// positioner
				if ( useGotoXX )
				{
					diseqc.len = 5;
					diseqc.data[2] = 0x6E;	// drive to angular position
					diseqc.data[3] = ((RotorCmd & 0xFF00) / 0x100);
					diseqc.data[4] = RotorCmd & 0xFF;
				}
				else
				{
					diseqc.len = 4;
					diseqc.data[2] = 0x6B;	// goto stored sat position
					diseqc.data[3] = RotorCmd;
					diseqc.data[4] = 0x00;
				}

			// use measure rotor input power to detect motor state
				if ( rotor_param.m_inputpower_parameters.m_use)
				{
					bool turn_fast = need_turn_fast(rotor_param.m_inputpower_parameters.m_turning_speed) && !is_unicable;
					eSecCommand::rotor cmd;
					eSecCommand::pair compare;
					if (turn_fast)
						compare.voltage = VOLTAGE(18);
					else
						compare.voltage = VOLTAGE(13);
					compare.steps = +3;
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_VOLTAGE_GOTO, compare) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, compare.voltage) );
			// measure idle power values
					compare.steps = -2;
					if (turn_fast) {
						sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_VOLTAGE_CHANGE_BEFORE_MEASURE_IDLE_INPUTPOWER]) );  // wait 150msec after voltage change
						sec_sequence.push_back( eSecCommand(eSecCommand::MEASURE_IDLE_INPUTPOWER, 1) );
						compare.val = 1;
						sec_sequence.push_back( eSecCommand(eSecCommand::IF_MEASURE_IDLE_WAS_NOT_OK_GOTO, compare) );
						sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, VOLTAGE(13)) );
					}
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_VOLTAGE_CHANGE_BEFORE_MEASURE_IDLE_INPUTPOWER]) );  // wait 150msec before measure
					sec_sequence.push_back( eSecCommand(eSecCommand::MEASURE_IDLE_INPUTPOWER, 0) );
					compare.val = 0;
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_MEASURE_IDLE_WAS_NOT_OK_GOTO, compare) );
			////////////////////////////
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_ROTOR_DISEQC_RETRYS, m_params[MOTOR_COMMAND_RETRIES]) );  // 2 retries
					sec_sequence.push_back( eSecCommand(eSecCommand::INVALIDATE_CURRENT_ROTORPARMS) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SEND_DISEQC, diseqc) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_TIMEOUT, 40) );  // 2 seconds rotor start timout
			// rotor start loop
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, 50) );  // 50msec delay
					sec_sequence.push_back( eSecCommand(eSecCommand::MEASURE_RUNNING_INPUTPOWER) );
					cmd.direction=1;  // check for running rotor
					cmd.deltaA=rotor_param.m_inputpower_parameters.m_delta;
					cmd.steps=+5;
					cmd.okcount=0;
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_INPUTPOWER_DELTA_GOTO, cmd ) );  // check if rotor has started
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_TIMEOUT_GOTO, +2 ) );  // timeout .. we assume now the rotor is already at the correct position
					sec_sequence.push_back( eSecCommand(eSecCommand::GOTO, -4) );  // goto loop start
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_NO_MORE_ROTOR_DISEQC_RETRYS_GOTO, turn_fast ? 10 : 9 ) );  // timeout .. we assume now the rotor is already at the correct position
					sec_sequence.push_back( eSecCommand(eSecCommand::GOTO, -8) );  // goto loop start
			////////////////////
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_ROTOR_MOVING) );
					if (turn_fast)
						sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, VOLTAGE(18)) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_TIMEOUT, mrt*20) );  // mrt is in seconds... our SLEEP time is 50ms.. so * 20
			// rotor running loop
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, 50) );  // wait 50msec
					sec_sequence.push_back( eSecCommand(eSecCommand::MEASURE_RUNNING_INPUTPOWER) );
					cmd.direction=0;  // check for stopped rotor
					cmd.steps=+3;
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_INPUTPOWER_DELTA_GOTO, cmd ) );
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_TIMEOUT_GOTO, +2 ) );  // timeout ? this should never happen
					sec_sequence.push_back( eSecCommand(eSecCommand::GOTO, -4) );  // running loop start
			/////////////////////
					sec_sequence.push_back( eSecCommand(eSecCommand::UPDATE_CURRENT_ROTORPARAMS) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_ROTOR_STOPPED) );
				}
			// use normal motor turning mode
				else
				{
					if (curRotorPos != -1)
					{
						mrt = abs(curRotorPos - sat.orbital_position);
						if (mrt > 1800)
							mrt = 3600 - mrt;
						if (mrt % 10)
							mrt += 10; // round a little bit
						mrt *= 2000;  // (we assume a very slow rotor with just 0.5 degree per second here)
						mrt /= 10000;
						mrt += 3; // a little bit overhead
					}
					doSetVoltageToneFrontend=false;
					doSetFrontend=false;
					eSecCommand::rotor cmd;
					eSecCommand::pair compare;
					compare.voltage = VOLTAGE(13);
					compare.steps = +3;
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_VOLTAGE_GOTO, compare) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, compare.voltage) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_VOLTAGE_CHANGE_BEFORE_MOTOR_CMD]) );  // wait 150msec after voltage change

					sec_sequence.push_back( eSecCommand(eSecCommand::INVALIDATE_CURRENT_ROTORPARMS) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_ROTOR_MOVING) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SEND_DISEQC, diseqc) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, 1000) ); // sleep one second before change voltage or tone

					compare.voltage = voltage;
					compare.steps = +3;
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_VOLTAGE_GOTO, compare) ); // correct final voltage?
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, 2000) );  // wait 2 second before set high voltage
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, voltage) );

					compare.tone = tone;
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_TONE_GOTO, compare) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_TONE, tone) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_FINAL_CONT_TONE_CHANGE]) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_FRONTEND, 0) );

					cmd.direction=1;  // check for running rotor
					cmd.deltaA=0;
					cmd.steps = +3;
					cmd.okcount=0;
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_TIMEOUT, mrt*4) );  // mrt is in seconds... our SLEEP time is 250ms.. so * 4
					sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, 250) );  // 250msec delay
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_TUNER_LOCKED_GOTO, cmd ) );
					sec_sequence.push_back( eSecCommand(eSecCommand::IF_TIMEOUT_GOTO, +5 ) );
					sec_sequence.push_back( eSecCommand(eSecCommand::GOTO, -3) );  // goto loop start
					sec_sequence.push_back( eSecCommand(eSecCommand::UPDATE_CURRENT_ROTORPARAMS) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_ROTOR_STOPPED) );
					sec_sequence.push_back( eSecCommand(eSecCommand::GOTO, +4) );
					sec_sequence.push_back( eSecCommand(eSecCommand::START_TUNE_TIMEOUT, tunetimeout) );
					sec_sequence.push_back( eSecCommand(eSecCommand::SET_FRONTEND, 1) );
					sec_sequence.push_back( eSecCommand(eSecCommand::GOTO, -5) );
					eDebugNoSimulate("set rotor timeout to %d seconds", mrt);
				}
				sec_fe->setData(eDVBFrontend::NEW_ROTOR_CMD, RotorCmd);
				sec_fe->setData(eDVBFrontend::NEW_ROTOR_POS, sat.orbital_position);
			}

			if (doSetVoltageToneFrontend && !is_unicable)
			{
				eSecCommand::pair compare;
				compare.voltage = voltage;
				compare.steps = +3;
				sec_sequence.push_back( eSecCommand(eSecCommand::IF_VOLTAGE_GOTO, compare) ); // voltage already correct ?
				sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, voltage) );
				sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_FINAL_VOLTAGE_CHANGE]) );
				compare.tone = tone;
				sec_sequence.push_back( eSecCommand(eSecCommand::IF_TONE_GOTO, compare) );
				sec_sequence.push_back( eSecCommand(eSecCommand::SET_TONE, tone) );
				sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_FINAL_CONT_TONE_CHANGE]) );
			}

			sec_sequence.push_back( eSecCommand(eSecCommand::UPDATE_CURRENT_SWITCHPARMS) );

			if (doSetFrontend)
			{
				sec_sequence.push_back( eSecCommand(eSecCommand::START_TUNE_TIMEOUT, tunetimeout) );
				sec_sequence.push_back( eSecCommand(eSecCommand::SET_FRONTEND, 1) );
			}

			sec_sequence.push_front( eSecCommand(eSecCommand::SET_POWER_LIMITING_MODE, eSecCommand::modeStatic) );
			sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, 500) );
			sec_sequence.push_back( eSecCommand(eSecCommand::SET_POWER_LIMITING_MODE, eSecCommand::modeDynamic) );

//get top tuner
			if(((eDVBFrontend *)&frontend)->has_prev())
			{
				eDVBFrontend *fe = (eDVBFrontend *)&frontend;
				fe->getTop(frontend, fe);

				int state;
				fe->getState(state);
				if (state != eDVBFrontend::stateClosed)
				{
					eSecCommandList sec_takeover_sequence;
					sec_takeover_sequence.push_front(eSecCommand(eSecCommand::CHANGE_TUNER_TYPE,((eDVBFrontend *)&frontend)->getCurrentType()));
					sec_takeover_sequence.push_front(eSecCommand(eSecCommand::TAKEOVER, (long)&frontend));
					fe->setSecSequence(sec_takeover_sequence, (eDVBFrontend *)&frontend);
					eDebugNoSimulate("takeover_sec %d",fe->getDVBID());

					sec_sequence.push_front( eSecCommand(eSecCommand::WAIT_TAKEOVER) );
					sec_sequence.push_back( eSecCommand(eSecCommand::RELEASE_TAKEOVER, (long)&frontend) );
					eDebugNoSimulate("waittakeover_sec %d",frontend.getDVBID());
				}
			}
			frontend.setSecSequence(sec_sequence);
			return 0;
		}
	}
	eDebugNoSimulate("found no useable satellite configuration for %s freq %d%s %s on orbital position (%d)",
		sat.system ? "DVB-S2" : "DVB-S",
		sat.frequency,
		sat.polarisation == eDVBFrontendParametersSatellite::Polarisation_Horizontal ? "H" :
			eDVBFrontendParametersSatellite::Polarisation_Vertical ? "V" :
			eDVBFrontendParametersSatellite::Polarisation_CircularLeft ? "CL" : "CR",
		sat.modulation == eDVBFrontendParametersSatellite::Modulation_Auto ? "AUTO" :
			eDVBFrontendParametersSatellite::Modulation_QPSK ? "QPSK" :
			eDVBFrontendParametersSatellite::Modulation_8PSK ? "8PSK" :
			eDVBFrontendParametersSatellite::Modulation_QAM16 ? "QAM16" :
			eDVBFrontendParametersSatellite::Modulation_16APSK ? "16APSK" : "32APSK",
		sat.orbital_position );
	return -1;
}

void eDVBSatelliteEquipmentControl::prepareTurnOffSatCR(iDVBFrontend &frontend)
{
	long satcr, diction, pin;
	eSecCommandList sec_sequence;

	// check if voltage is disabled
	eSecCommand::pair compare;
	compare.steps = +9;	//only close frontend
	compare.voltage = iDVBFrontend::voltageOff;

	sec_sequence.push_back( eSecCommand(eSecCommand::IF_VOLTAGE_GOTO, compare) );
	sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, iDVBFrontend::voltage13) );
	sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_ENABLE_VOLTAGE_BEFORE_SWITCH_CMDS]) );

	sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, iDVBFrontend::voltage18_5) );
	sec_sequence.push_back( eSecCommand(eSecCommand::SET_TONE, iDVBFrontend::toneOff) );
	sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_VOLTAGE_CHANGE_BEFORE_SWITCH_CMDS]) );

	eDVBDiseqcCommand diseqc;
	memset(diseqc.data, 0, MAX_DISEQC_LENGTH);
	frontend.getData(eDVBFrontend::SATCR, satcr);
	frontend.getData(eDVBFrontend::DICTION, diction);
	frontend.getData(eDVBFrontend::PIN, pin);

	switch (diction)
	{
		case 1:
			if(pin < 1)
			{
				diseqc.len = 4;
				diseqc.data[0] = 0x70;
			}
			else
			{
				diseqc.len = 5;
				diseqc.data[0] = 0x71;
				diseqc.data[4] = pin;
			}
			diseqc.data[1] = satcr << 3;
			diseqc.data[2] = 0x00;
			diseqc.data[3] = 0x00;
			break;
		case 0:
		default:
			if(pin < 1)
			{
				diseqc.len = 5;
				diseqc.data[2] = 0x5A;
			}
			else
			{
				diseqc.len = 6;
				diseqc.data[2] = 0x5C;
				diseqc.data[5] = pin;
			}
			diseqc.data[0] = 0xE0;
			diseqc.data[1] = 0x10;
			diseqc.data[3] = satcr << 5;
			diseqc.data[4] = 0x00;
			break;
	}

	sec_sequence.push_back( eSecCommand(eSecCommand::SEND_DISEQC, diseqc) );
	sec_sequence.push_back( eSecCommand(eSecCommand::SLEEP, m_params[DELAY_AFTER_LAST_DISEQC_CMD]) );
	sec_sequence.push_back( eSecCommand(eSecCommand::SET_VOLTAGE, iDVBFrontend::voltage13) );
	sec_sequence.push_back( eSecCommand(eSecCommand::DELAYED_CLOSE_FRONTEND) );

	if(((eDVBFrontend *)&frontend)->has_prev())
	{
		eDVBFrontend *fe = (eDVBFrontend *)&frontend;
		fe->getTop(frontend, fe);

		int state;
		fe->getState(state);
		if (state != eDVBFrontend::stateClosed)
		{
			eSecCommandList sec_takeover_sequence;
			sec_takeover_sequence.push_front(eSecCommand(eSecCommand::CHANGE_TUNER_TYPE,((eDVBFrontend *)&frontend)->getCurrentType()));
			sec_takeover_sequence.push_front(eSecCommand(eSecCommand::TAKEOVER, (long)&frontend));
			fe->setSecSequence(sec_takeover_sequence, (eDVBFrontend *)&frontend);
			eDebug("takeover_sec %d",fe->getDVBID());

			sec_sequence.push_front( eSecCommand(eSecCommand::WAIT_TAKEOVER) );
			sec_sequence.push_back( eSecCommand(eSecCommand::RELEASE_TAKEOVER, (long)&frontend) );
			eDebug("waittakeover_sec %d",frontend.getDVBID());
		}
		else
			eDebug("fail: tuner %d is closed",fe->getDVBID());
	}
	frontend.setSecSequence(sec_sequence);
}

RESULT eDVBSatelliteEquipmentControl::clear()
{
	eSecDebug("eDVBSatelliteEquipmentControl::clear()");
	for (int i=0; i <= m_lnbidx; ++i)
	{
		m_lnbs[i].m_satellites.clear();
		m_lnbs[i].m_slot_mask = 0;
		m_lnbs[i].m_prio = -1; // auto
	}
	m_lnbidx=-1;

	m_not_linked_slot_mask=0;

	//reset some tuner configuration
	for (eSmartPtrList<eDVBRegisteredFrontend>::iterator it(m_avail_frontends.begin()); it != m_avail_frontends.end(); ++it)
	{
		it->m_frontend->setData(eDVBFrontend::SATPOS_DEPENDS_PTR, -1);
		it->m_frontend->setData(eDVBFrontend::LINKED_PREV_PTR, -1);
		it->m_frontend->setData(eDVBFrontend::LINKED_NEXT_PTR, -1);
		it->m_frontend->setData(eDVBFrontend::ROTOR_POS, -1);
		it->m_frontend->setData(eDVBFrontend::ROTOR_CMD, -1);
		it->m_frontend->setData(eDVBFrontend::SATCR, -1);

		if (it->m_frontend->is_FBCTuner())
		{
			eFBCTunerManager *fbcmng = eFBCTunerManager::getInstance();
			if (fbcmng)
				fbcmng->setDefaultFBCID(*it);
		}
	}

	for (eSmartPtrList<eDVBRegisteredFrontend>::iterator it(m_avail_simulate_frontends.begin()); it != m_avail_simulate_frontends.end(); ++it)
	{
		it->m_frontend->setData(eDVBFrontend::SATPOS_DEPENDS_PTR, -1);
		it->m_frontend->setData(eDVBFrontend::LINKED_PREV_PTR, -1);
		it->m_frontend->setData(eDVBFrontend::LINKED_NEXT_PTR, -1);
		it->m_frontend->setData(eDVBFrontend::ROTOR_POS, -1);
		it->m_frontend->setData(eDVBFrontend::ROTOR_CMD, -1);
		it->m_frontend->setData(eDVBFrontend::SATCR, -1);
	}

	return 0;
}

/* LNB Specific Parameters */
RESULT eDVBSatelliteEquipmentControl::addLNB()
{
	if ( (m_lnbidx+1) < (int)(sizeof(m_lnbs) / sizeof(eDVBSatelliteLNBParameters)))
		m_curSat=m_lnbs[++m_lnbidx].m_satellites.end();
	else
	{
		eDebug("no more LNB free... cnt is %d", m_lnbidx);
		return -ENOSPC;
	}
	eSecDebug("eDVBSatelliteEquipmentControl::addLNB(%d)", m_lnbidx);
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setLNBSlotMask(int slotmask)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setLNBSlotMask(%d)", slotmask);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_slot_mask = slotmask;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setLNBLOFL(int lofl)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setLNBLOFL(%d)", lofl);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_lof_lo = lofl;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setLNBLOFH(int lofh)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setLNBLOFH(%d)", lofh);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_lof_hi = lofh;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setLNBThreshold(int threshold)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setLNBThreshold(%d)", threshold);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_lof_threshold = threshold;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setLNBIncreasedVoltage(bool onoff)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setLNBIncreasedVoltage(%d)", onoff);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_increased_voltage = onoff;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setLNBPrio(int prio)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setLNBPrio(%d)", prio);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_prio = prio;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setLNBSatCRpositionnumber(int SatCR_positionnumber)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setLNBSatCRpositionnumber(%d)", SatCR_positionnumber);
//	if(!((SatCR_positionnumber > 0) && (SatCR_positionnumber <= MAX_FIXED_LNB_POSITIONS)))
//		return -EPERM;
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].SatCR_positionnumber = SatCR_positionnumber;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setLNBSatCRTuningAlgo(int SatCR_switch_reliable)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setLNBSatCRTuningAlgo(%d)", SatCR_switch_reliable);
	if(!((SatCR_switch_reliable >= 0) && (SatCR_switch_reliable <= 1)))
		return -EPERM;
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].SatCR_switch_reliable = SatCR_switch_reliable;
	else
		return -ENOENT;
	return 0;
}

/* DiSEqC Specific Parameters */
RESULT eDVBSatelliteEquipmentControl::setDiSEqCMode(int diseqcmode)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setDiSEqcMode(%d)", diseqcmode);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_diseqc_parameters.m_diseqc_mode = (eDVBSatelliteDiseqcParameters::t_diseqc_mode)diseqcmode;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setToneburst(int toneburst)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setToneburst(%d)", toneburst);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_diseqc_parameters.m_toneburst_param = (eDVBSatelliteDiseqcParameters::t_toneburst_param)toneburst;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setRepeats(int repeats)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setRepeats(%d)", repeats);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_diseqc_parameters.m_repeats=repeats;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setCommittedCommand(int command)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setCommittedCommand(%d)", command);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_diseqc_parameters.m_committed_cmd=command;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setUncommittedCommand(int command)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setUncommittedCommand(%d)", command);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_diseqc_parameters.m_uncommitted_cmd = command;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setCommandOrder(int order)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setCommandOrder(%d)", order);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_diseqc_parameters.m_command_order=order;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setFastDiSEqC(bool onoff)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setFastDiSEqc(%d)", onoff);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_diseqc_parameters.m_use_fast=onoff;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setSeqRepeat(bool onoff)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setSeqRepeat(%d)", onoff);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_diseqc_parameters.m_seq_repeat = onoff;
	else
		return -ENOENT;
	return 0;
}

/* Rotor Specific Parameters */
RESULT eDVBSatelliteEquipmentControl::setLongitude(float longitude)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setLongitude(%f)", longitude);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_rotor_parameters.m_gotoxx_parameters.m_longitude=longitude;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setLatitude(float latitude)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setLatitude(%f)", latitude);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_rotor_parameters.m_gotoxx_parameters.m_latitude=latitude;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setLoDirection(int direction)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setLoDirection(%d)", direction);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_rotor_parameters.m_gotoxx_parameters.m_lo_direction=direction;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setLaDirection(int direction)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setLaDirection(%d)", direction);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_rotor_parameters.m_gotoxx_parameters.m_la_direction=direction;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setUseInputpower(bool onoff)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setUseInputpower(%d)", onoff);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_rotor_parameters.m_inputpower_parameters.m_use=onoff;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setInputpowerDelta(int delta)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setInputpowerDelta(%d)", delta);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_rotor_parameters.m_inputpower_parameters.m_delta=delta;
	else
		return -ENOENT;
	return 0;
}

/* Unicable Specific Parameters */
RESULT eDVBSatelliteEquipmentControl::setLNBSatCRformat(int SatCR_format)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setLNBSatCRformat(%d)", SatCR_format);
	if(!((SatCR_format >-1) && (SatCR_format < 2)))
		return -EPERM;
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].SatCR_format = SatCR_format;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setLNBSatCR(int SatCR_idx)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setLNBSatCR(%d)", SatCR_idx);
	if(!((SatCR_idx >=-1) && (SatCR_idx < MAX_SATCR)))
		return -EPERM;
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].SatCR_idx = SatCR_idx;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setLNBSatCRvco(int SatCRvco)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setLNBSatCRvco(%d)", SatCRvco);
	if(!((SatCRvco >= 950*1000) && (SatCRvco <= 2150*1000)))
		return -EPERM;
	if(!((m_lnbs[m_lnbidx].SatCR_idx >= 0) && (m_lnbs[m_lnbidx].SatCR_idx < MAX_SATCR)))
		return -ENOENT;
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].SatCRvco = SatCRvco;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setLNBSatCRpositions(int SatCR_positions)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setLNBSatCRpositions(%d)", SatCR_positions);
	if(SatCR_positions < 1)
		return -EPERM;
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].SatCR_positions = SatCR_positions;
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::getLNBSatCRpositions()
{
	if ( currentLNBValid() )
		return m_lnbs[m_lnbidx].SatCR_positions;
	return -ENOENT;
}

RESULT eDVBSatelliteEquipmentControl::getLNBSatCRformat()
{
	if ( currentLNBValid() )
		return m_lnbs[m_lnbidx].SatCR_format;
	return -ENOENT;
}

RESULT eDVBSatelliteEquipmentControl::getLNBSatCR()
{
	if ( currentLNBValid() )
		return m_lnbs[m_lnbidx].SatCR_idx;
	return -ENOENT;
}

RESULT eDVBSatelliteEquipmentControl::getLNBSatCRvco()
{
	if ( currentLNBValid() )
		return m_lnbs[m_lnbidx].SatCRvco;
	return -ENOENT;
}

/* Satellite Specific Parameters */
RESULT eDVBSatelliteEquipmentControl::addSatellite(int orbital_position)
{
	eSecDebug("eDVBSatelliteEquipmentControl::addSatellite(%d)", orbital_position);
	if ( currentLNBValid() )
	{
		std::multimap<int,eDVBSatelliteSwitchParameters>::iterator ret =
			m_lnbs[m_lnbidx].m_satellites.insert(
				std::pair<int, eDVBSatelliteSwitchParameters>(orbital_position, eDVBSatelliteSwitchParameters())
			);

		m_curSat = ret;
	}
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setVoltageMode(int mode)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setVoltageMode(%d)", mode);
	if ( currentLNBValid() && m_curSat != m_lnbs[m_lnbidx].m_satellites.end() )
		m_curSat->second.m_voltage_mode = (eDVBSatelliteSwitchParameters::t_voltage_mode)mode;
	else
		return -ENOENT;
	return 0;

}

RESULT eDVBSatelliteEquipmentControl::setToneMode(int mode)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setToneMode(%d)", mode);
	if ( currentLNBValid() )
	{
		if ( m_curSat != m_lnbs[m_lnbidx].m_satellites.end() )
			m_curSat->second.m_22khz_signal = (eDVBSatelliteSwitchParameters::t_22khz_signal)mode;
		else
			return -EPERM;
	}
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setRotorPosNum(int rotor_pos_num)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setRotorPosNum(%d)", rotor_pos_num);
	if ( currentLNBValid() )
	{
		if ( m_curSat != m_lnbs[m_lnbidx].m_satellites.end() )
			m_curSat->second.m_rotorPosNum=rotor_pos_num;
		else
			return -EPERM;
	}
	else
		return -ENOENT;
	return 0;
}

RESULT eDVBSatelliteEquipmentControl::setRotorTurningSpeed(int speed)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setRotorTurningSpeed(%d)", speed);
	if ( currentLNBValid() )
		m_lnbs[m_lnbidx].m_rotor_parameters.m_inputpower_parameters.m_turning_speed = speed;
	else
		return -ENOENT;
	return 0;
}

struct sat_compare
{
	int orb_pos, lofl, lofh;
	sat_compare(int o, int lofl, int lofh)
		:orb_pos(o), lofl(lofl), lofh(lofh)
	{}
	sat_compare(const sat_compare &x)
		:orb_pos(x.orb_pos), lofl(x.lofl), lofh(x.lofh)
	{}
	bool operator < (const sat_compare & cmp) const
	{
		if (orb_pos == cmp.orb_pos)
		{
			if ( abs(lofl-cmp.lofl) < 200000 )
			{
				if (abs(lofh-cmp.lofh) < 200000)
					return false;
				return lofh<cmp.lofh;
			}
			return lofl<cmp.lofl;
		}
		return orb_pos < cmp.orb_pos;
	}
};

RESULT eDVBSatelliteEquipmentControl::setTunerLinked(int tu1, int tu2)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setTunerLinked(%d, %d)", tu1, tu2);
	if (tu1 != tu2)
	{
		eDVBRegisteredFrontend *p1=NULL, *p2=NULL;
		eSmartPtrList<eDVBRegisteredFrontend>::iterator it(m_avail_frontends.begin());
		for (; it != m_avail_frontends.end(); ++it)
		{
			if (it->m_frontend->getSlotID() == tu1)
				p1 = *it;
			else if (it->m_frontend->getSlotID() == tu2)
				p2 = *it;
		}
		if (p1 && p2)
		{
			p1->m_frontend->setData(eDVBFrontend::LINKED_PREV_PTR, (long)p2);
			p2->m_frontend->setData(eDVBFrontend::LINKED_NEXT_PTR, (long)p1);

			eFBCTunerManager *fbcmng = eFBCTunerManager::getInstance();
			if (p1->m_frontend->is_FBCTuner() && fbcmng)
			{
				fbcmng->updateFBCID(p1, p2);
			}
		}

		p1=p2=NULL;
		it=m_avail_simulate_frontends.begin();
		for (; it != m_avail_simulate_frontends.end(); ++it)
		{
			if (it->m_frontend->getSlotID() == tu1)
				p1 = *it;
			else if (it->m_frontend->getSlotID() == tu2)
				p2 = *it;
		}
		if (p1 && p2)
		{
			p1->m_frontend->setData(eDVBFrontend::LINKED_PREV_PTR, (long)p2);
			p2->m_frontend->setData(eDVBFrontend::LINKED_NEXT_PTR, (long)p1);
			return 0;
		}
	}
	return -1;
}

RESULT eDVBSatelliteEquipmentControl::setTunerDepends(int tu1, int tu2)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setTunerDepends(%d, %d)", tu1, tu2);
	if (tu1 == tu2)
		return -1;

	eDVBRegisteredFrontend *p1=NULL, *p2=NULL;

	for (eSmartPtrList<eDVBRegisteredFrontend>::iterator it(m_avail_frontends.begin()); it != m_avail_frontends.end(); ++it)
	{
		if (it->m_frontend->getSlotID() == tu1)
			p1 = *it;
		else if (it->m_frontend->getSlotID() == tu2)
			p2 = *it;
	}
	if (p1 && p2)
	{
		p1->m_frontend->setData(eDVBFrontend::SATPOS_DEPENDS_PTR, (long)p2);
		p2->m_frontend->setData(eDVBFrontend::SATPOS_DEPENDS_PTR, (long)p1);
	}

	p1=p2=NULL;
	for (eSmartPtrList<eDVBRegisteredFrontend>::iterator it(m_avail_simulate_frontends.begin()); it != m_avail_simulate_frontends.end(); ++it)
	{
		if (it->m_frontend->getSlotID() == tu1)
			p1 = *it;
		else if (it->m_frontend->getSlotID() == tu2)
			p2 = *it;
	}
	if (p1 && p2)
	{
		p1->m_frontend->setData(eDVBFrontend::SATPOS_DEPENDS_PTR, (long)p2);
		p2->m_frontend->setData(eDVBFrontend::SATPOS_DEPENDS_PTR, (long)p1);
		return 0;
	}

	return -1;
}

void eDVBSatelliteEquipmentControl::setSlotNotLinked(int slot_no)
{
	eSecDebug("eDVBSatelliteEquipmentControl::setSlotNotLinked(%d)", slot_no);
	m_not_linked_slot_mask |= (1 << slot_no);
}

bool eDVBSatelliteEquipmentControl::isRotorMoving()
{
	return m_rotorMoving;
}

void eDVBSatelliteEquipmentControl::setRotorMoving(int slot_no, bool b)
{
	if (b)
		m_rotorMoving |= (1 << slot_no);
	else
		m_rotorMoving &= ~(1 << slot_no);
}

PyObject *eDVBSatelliteEquipmentControl::getBandCutOffFrequency(int slot_no, int orbital_position)
{
	PyObject *pyList = PyList_New(0);
	for (int idx=0; idx <= m_lnbidx; ++idx)
	{
		eDVBSatelliteLNBParameters &lnb_param = m_lnbs[idx];
		if ( lnb_param.m_slot_mask & (1 << slot_no)) // lnb for correct tuner?
		{
			std::map<int, eDVBSatelliteSwitchParameters>::iterator sit = lnb_param.m_satellites.find(orbital_position);
			if ( sit != lnb_param.m_satellites.end())
				PyList_Append(pyList, PyInt_FromLong(lnb_param.m_lof_threshold));
		}
	}
	return pyList;
}

PyObject *eDVBSatelliteEquipmentControl::getFrequencyRangeList(int slot_no, int orbital_position)
{
	PyObject *pyList = PyList_New(0);
	dvb_frontend_info fe_info;

	eSmartPtrList<eDVBRegisteredFrontend>::iterator it(m_avail_frontends.begin());
	for (; it != m_avail_frontends.end(); ++it)
	{
		if (it->m_frontend->getSlotID() == slot_no)
		{
			fe_info = ((eDVBFrontend*)it->m_frontend)->getFrontendInfo(SYS_DVBS);
		}
	}

	for (int idx=0; idx <= m_lnbidx; ++idx)
	{
		eDVBSatelliteLNBParameters &lnb_param = m_lnbs[idx];
		if ( lnb_param.m_slot_mask & (1 << slot_no)) // lnb for correct tuner?
		{
			std::map<int, eDVBSatelliteSwitchParameters>::iterator sit = lnb_param.m_satellites.find(orbital_position);
			if ( sit != lnb_param.m_satellites.end())
			{
				PyObject *pyTuple = PyTuple_New(2);
				PyTuple_SET_ITEM(pyTuple, 0, PyInt_FromLong(lnb_param.m_lof_lo + fe_info.frequency_min));
				PyTuple_SET_ITEM(pyTuple, 1, PyInt_FromLong(lnb_param.m_lof_hi + fe_info.frequency_max));
				PyList_Append(pyList, pyTuple);
			}
		}
	}
	return pyList;
}
