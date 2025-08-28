import pandas as pd
from pandapower.timeseries.data_sources.frame_data import DFData
from pandaprosumer.create import create_empty_prosumer_container
from pandaprosumer.create import create_period
from pandaprosumer.create_controlled import create_controlled_const_profile, create_controlled_booster_heat_pump
from pandaprosumer.create_controlled import create_controlled_ice_chp
from pandaprosumer.create_controlled import create_controlled_heat_storage
from pandaprosumer.create_controlled import create_controlled_heat_demand
from pandaprosumer.mapping import GenericMapping
from pandaprosumer.run_time_series import run_timeseries
import matplotlib.pyplot as plt


size_kw = 700
altitude_m = 0
fuel = 'ng'
name_chp = 'example_chp'

hp_type = 'water-water3'
name_bhp = 'example_bhp'

capacity = 20000  # in kWh

start = '2020-01-01 00:00:00'
end = '2020-01-02 00:00:00'
time_resolution_s = 900         # 15 min
frequency = '15min'

demand_data = pd.read_excel('input_bhp_chp_1consumer.xlsx')
dur = pd.date_range(start, end, freq=frequency, tz='utc')
demand_data.index = dur
demand_input = DFData(demand_data)

prosumer = create_empty_prosumer_container()
period = create_period(prosumer, time_resolution_s, start, end, 'utc', 'default')

input_columns = ['demand', 'cycle', 't_intake_k', 't_source_k', 'mode', 't_sink_k', 'p_received_kw']
output_columns = ['demand_c', 'cycle_c', 't_intake_c_k', 't_source_c_k', 'mode_c', 't_sink_c_k', 'p_received_c_kw']
cp_index = create_controlled_const_profile(prosumer, input_columns, output_columns, demand_input, period, level=0, order=0)

ice_chp_index = create_controlled_ice_chp(prosumer, size_kw, fuel, altitude_m, name_chp, level=1, order=0)
bhp_index = create_controlled_booster_heat_pump(prosumer, hp_type=hp_type, name=name_bhp, level=1, order=1)
storage_index = create_controlled_heat_storage(prosumer, capacity, level=1, order=2)
heat_demand_index = create_controlled_heat_demand(prosumer, scaling=1.0, level=1, order=3)

GenericMapping(
    prosumer,
    initiator_id = cp_index,
    initiator_column = "cycle_c",
    responder_id = ice_chp_index,
    responder_column = "cycle",
    order = 0)
GenericMapping(
    prosumer,
    initiator_id = cp_index,
    initiator_column = "t_intake_c_k",
    responder_id = ice_chp_index,
    responder_column = "t_intake_k",
    order = 0)

GenericMapping(
    prosumer,
    initiator_id = cp_index,
    initiator_column = "t_source_c_k",
    responder_id = bhp_index,
    responder_column = "t_source_k",
    order = 0)
GenericMapping(
    prosumer,
    initiator_id = cp_index,
    initiator_column = "mode_c",
    responder_id = bhp_index,
    responder_column = "mode",
    order = 0)
GenericMapping(
    prosumer,
    initiator_id = cp_index,
    initiator_column = 't_sink_c_k',
    responder_id = bhp_index,
    responder_column = 't_sink_k',
    order = 0)
GenericMapping(
    prosumer,
    initiator_id = cp_index,
    initiator_column = 'p_received_c_kw',
    responder_id = bhp_index,
    responder_column = 'p_received_kw',
    order = 0)

GenericMapping(
    prosumer,
    initiator_id = cp_index,
    initiator_column = "demand_c",
    responder_id = heat_demand_index,
    responder_column = "q_demand_kw",
    order = 0)


GenericMapping(
    prosumer,
    initiator_id = ice_chp_index,
    initiator_column = "p_th_out_kw",
    responder_id = storage_index,
    responder_column = "q_received_kw",
    order = 0
)
GenericMapping(
    prosumer,
    initiator_id = bhp_index,
    initiator_column = "q_floor",
    responder_id = storage_index,
    responder_column = "q_received_kw",
    order = 0
)

GenericMapping(
    prosumer,
    initiator_id = storage_index,
    initiator_column = "q_delivered_kw",
    responder_id = heat_demand_index,
    responder_column = "q_received_kw",
    order = 0)




run_timeseries(prosumer, period, True)

chp = prosumer.time_series.data_source.loc[0].df.p_th_out_kw
bhp = prosumer.time_series.data_source.loc[1].df.q_floor

demand_data['demand'].plot()
chp.plot()
bhp.plot()

plt.legend()
plt.show()

storage = prosumer.time_series.data_source.loc[2].df
storage.soc.plot()

plt.show()
