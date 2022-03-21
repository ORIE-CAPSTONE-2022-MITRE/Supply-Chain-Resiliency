import numpy as np
import pandas as pd
from config import raw_data_path, configuration
from mitre_functions import helpers

raw_data = raw_data_path()
config_info = configuration()
mitre_func = helpers()


class data_loading(object):
    def __init__(self):
        return

    def load_FAF(self):
        df_all = pd.read_csv(raw_data.FAF_State_with_name)
        df_all = df_all.loc[:, config_info.relevant_cols]
        df_pharm = df_all.loc[df_all['sctg2'] == config_info.pharm_code]
        return df_pharm

    def load_infra(self):
        df_t_risk = pd.read_excel(raw_data.Transportation_Risk, sheet_name='infra capacity')
        return df_t_risk


dl = data_loading()


class data_transformation(object):
    def __init__(self):
        return

    '''
    For each state, compute the proportion of supply from other 
    states by tons and value.
    '''
    def state_suppliers_prop(self):
        df_pharm = dl.load_FAF()
        # by tons
        des_left = df_pharm.groupby(['dms_origst', 'dms_destst'])['tons_2017'].sum().reset_index()
        des_right = df_pharm.groupby(['dms_destst'])['tons_2017'].sum().reset_index()
        result = pd.merge(des_left, des_right, on="dms_destst")
        result = result.rename(columns={'tons_2017_x': 'tons_state', 'tons_2017_y': 'tons_total'})
        result['tons_prop'] = result['tons_state'] / result['tons_total']
        # by values
        des_left = df_pharm.groupby(['dms_origst', 'dms_destst'])['value_2017'].sum().reset_index()
        des_right = df_pharm.groupby(['dms_destst'])['value_2017'].sum().reset_index()
        result2 = pd.merge(des_left, des_right, on="dms_destst")
        result2 = result2.rename(columns={'value_2017_x': 'value_state', 'value_2017_y': 'value_total'})
        result2['value_prop'] = result2['value_state'] / result2['value_total']
        # put together
        result['value_state'] = result2['value_state']
        result['value_total'] = result2['value_total']
        result['value_prop'] = result2['value_prop']
        return result

    '''
    For each state, compute the proportion of each transportation mode
    by tons and value.
    '''
    def state_transportation_mode(self):
        df_pharm = dl.load_FAF()
        # looking at only domestic and import data
        df = df_pharm.loc[(df_pharm['trade_type'] == 1) | (df_pharm['trade_type'] == 2)]
        # by tons
        df_temp = df.groupby(['dms_destst', 'dms_mode'])['tons_2017'].sum().reset_index()
        df_temp2 = df.groupby(['dms_destst'])['tons_2017'].sum().reset_index()
        df_transport = df_temp.merge(df_temp2, left_on='dms_destst', right_on='dms_destst')
        df_transport = df_transport.rename(columns={'tons_2017_x': 'tons', 'tons_2017_y': 'tons_total'})
        df_transport['tons_prop'] = df_transport['tons'] / df_transport['tons_total']
        # by values
        df_temp = df.groupby(['dms_destst', 'dms_mode'])['value_2017'].sum().reset_index()
        df_temp2 = df.groupby(['dms_destst'])['value_2017'].sum().reset_index()
        df_transport2 = df_temp.merge(df_temp2, left_on='dms_destst', right_on='dms_destst')
        df_transport2 = df_transport2.rename(columns={'value_2017_x': 'value_state', 'value_2017_y': 'value_total'})
        df_transport2['value_prop'] = df_transport2['value_state'] / df_transport2['value_total']
        # put together
        df_transport['value_state'] = df_transport2['value_state']
        df_transport['value_total'] = df_transport2['value_total']
        df_transport['value_prop'] = df_transport2['value_prop']
        return df_transport

    '''
    For each state, compute the proportion of each type of infrastructure 
    by tons.
    '''
    def state_infra_by_tons(self):
        states = config_info.states

        transport_dict = {
            key: [0] * 9 for key in states
        }

        df_transport = self.state_transportation_mode()
        for index, row in df_transport.iterrows():
            transport_dict[row['dms_destst']][row['dms_mode']] = row['tons_prop']
        df_transport_transform = pd.DataFrame.from_dict(transport_dict, orient='index').reset_index()
        df_transport_transform = df_transport_transform.drop(columns=[0, 6, 7, 8])
        df_transport_transform = df_transport_transform.rename(columns=config_info.dms_mode_dict)
        df_transport_transform = df_transport_transform.rename(columns={'index': 'states'})

        return df_transport_transform

    '''
    For each state, compute the proportion of each type of infrastructure 
    by value.
    '''
    def state_infra_by_value(self):
        states = config_info.states

        transport_dict = {
            key: [0] * 9 for key in states
        }

        df_transport = self.state_transportation_mode()
        for index, row in df_transport.iterrows():
            transport_dict[row['dms_destst']][row['dms_mode']] = row['value_prop']
        df_transport_transform = pd.DataFrame.from_dict(transport_dict, orient='index').reset_index()
        df_transport_transform = df_transport_transform.drop(columns=[0, 6, 7, 8])
        df_transport_transform = df_transport_transform.rename(columns=config_info.dms_mode_dict)
        df_transport_transform = df_transport_transform.rename(columns={'index': 'states'})

        return df_transport_transform

    '''
    For each state, compute the proportion of each type of infrastructure 
    by mileage.
    '''
    def state_infra_by_miles(self):
        df_t = dl.load_infra()
        df_t = df_t.fillna(0)

        df_t['ground'] = (df_t['Bridges'] + df_t['Miles of public road']) / df_t['Grand Total']
        df_t['rail'] = df_t['Miles of freight railroad'] / df_t['Grand Total']
        df_t['water'] = df_t['Miles of inland waterway'] / df_t['Grand Total']

        df_t.loc[df_t['States'] == 'District of Columbia', 'States'] = 'Washington DC'
        df_t = df_t.loc[~df_t['States'].isin(['Puerto Rico', 'United States'])].reset_index(drop=True)

        return df_t

    def states_entropy(self, by='tons'):
        states = config_info.states
        cross_entropy_dict = {
            key: 0 for key in states
        }
        df_t = self.state_infra_by_miles()
        df_target = df_t[['States', 'ground', 'rail', 'water']]
        if(by == 'tons'):
            df_transport_transform = self.state_infra_by_tons()
        else:
            df_transport_transform = self.state_infra_by_value()
        df_temp = df_transport_transform.merge(df_t, left_on='states', right_on='States')
        df_temp['Truck'] = df_temp['truck'] + df_temp['multiple'] * df_temp['ground']
        df_temp['Rail'] = df_temp['rail_x'] + df_temp['multiple'] * df_temp['rail_y']
        df_temp['Water'] = df_temp['water_x'] + df_temp['multiple'] * df_temp['water_y']
        df_temp = df_temp[['States', 'Truck', 'Rail', 'Water']]
        df_temp['Truck_pct'] = df_temp['Truck'] / (df_temp['Truck'] + df_temp['Rail'] + df_temp['Water'])
        df_temp['Rail_pct'] = df_temp['Rail'] / (df_temp['Truck'] + df_temp['Rail'] + df_temp['Water'])
        df_temp['Water_pct'] = df_temp['Water'] / (df_temp['Truck'] + df_temp['Rail'] + df_temp['Water'])
        df_temp = df_temp[['States', 'Truck_pct', 'Rail_pct', 'Water_pct']]
        for s in states:
            p = df_target.loc[df_target['States'] == s, ['ground', 'rail', 'water']].to_numpy().reshape(-1)
            q = df_temp.loc[df_temp['States'] == s, ['Truck_pct', 'Rail_pct', 'Water_pct']].to_numpy().reshape(-1)
            cross_entropy_dict[s] = mitre_func.cross_entropy(p, q)
        entropy_tons = pd.DataFrame.from_dict(cross_entropy_dict, orient='index').reset_index()
        entropy_tons = entropy_tons.rename(columns={'index': 'States', 0: 'Cross_Entropy'})
        return entropy_tons

# dt = data_transformation()
#
# dt.states_entropy()