class configuration(object):
    def __init__(self):
        # sctg2 column correspond to 
        # pharmatheutical products in 
        # raw_data/FAF5.2_State_with_name.csv
        self.pharm_code = 21 
        # relevant columns in
        # FAF5.2_State_with_name.csv
        self.relevant_cols = ['fr_orig', 'dms_origst', 
                              'dms_destst', 'fr_dest',
                              'fr_inmode', 'dms_mode', 
                              'fr_outmode', 'sctg2', 
                              'trade_type', 'tons_2017', 
                              'value_2017']

        self.states = ['Alabama',
                     'Alaska',
                     'Arizona',
                     'Arkansas',
                     'California',
                     'Colorado',
                     'Connecticut',
                     'Delaware',
                     'Washington DC',
                     'Florida',
                     'Georgia',
                     'Idaho',
                     'Illinois',
                     'Indiana',
                     'Iowa',
                     'Kansas',
                     'Kentucky',
                     'Louisiana',
                     'Maine',
                     'Maryland',
                     'Massachusetts',
                     'Michigan',
                     'Minnesota',
                     'Mississippi',
                     'Missouri',
                     'Montana',
                     'Nebraska',
                     'Nevada',
                     'New Hampshire',
                     'New Jersey',
                     'New Mexico',
                     'New York',
                     'North Carolina',
                     'Ohio',
                     'Oklahoma',
                     'Oregon',
                     'Pennsylvania',
                     'Rhode Island',
                     'South Carolina',
                     'South Dakota',
                     'Tennessee',
                     'Texas',
                     'Utah',
                     'Vermont',
                     'Virginia',
                     'Washington',
                     'West Virginia',
                     'Wisconsin',
                     'Wyoming',
                     'Hawaii',
                     'North Dakota']

        self.dms_mode_dict = {
                            1: 'truck',
                            2: 'rail',
                            3: 'water',
                            4: 'air',
                            5: 'multiple'
                        }

class raw_data_path(object):
    def __init__(self):
        self.FAF_State_with_name = 'raw_data/FAF5.2_State_with_name.csv'
        self.Metadata = 'raw_data/Metadata_Codes.csv'
        self.Transportation_Risk = 'raw_data/Transportation_Risk.xlsx'
