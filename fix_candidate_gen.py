with open('C:\\Users\\Sachin\\OneDrive\\Documents\\ML_proj\\src\\matching\\candidate_generator.py', 'r') as f:
    content = f.read()

# Find and replace the section
old_section = """        else:
            # Check if prep state is compatible with raw-basis IFCT
            raw_compatible = {'RAW', 'FRESH'}
            incompatible = {'DRIED', 'POWDERED', 'GROUNDED', 'ROASTED', 'FRIED', 'BOILED', 
                           'COOKED', 'FERMENTED', 'PICKLED', 'SPROUTED', 'BLANCHED', 'MARINATED'}
            
            prep_state_upper = str(prep_state).upper()
            if prep_state_upper in {'DRIED', 'POWDERED', 'GROUNDED', 'ROASTED', 'FRIED', 'BOILED', 
                                    'COOKED', 'FERMENTED', 'PICKLED', 'SPROUTED', 'BLANCHED', 'MARINATED'}:
                return {'auto_accept': False, 'reasons': ['NON_RAW_PREP_STATE'], 
                        'evidence': {'prep_state': str(prep_state), 'incompatible': True}}"""

new_section = """        else:
            # Check if prep state is compatible with raw-basis IFCT
            raw_compatible = {'RAW', 'FRESH'}
            incompatible = {'DRIED', 'POWDERED', 'GROUND', 'ROASTED', 'FRIED', 'BOILED', 
                           'COOKED', 'FERMENTED', 'PICKLED', 'SPROUTED', 'BLANCHED', 'MARINATED', 'SOAKED', 'GROUND'}
            
            prep_state_upper = str(prep_state).upper()
            if prep_state_upper in incompatible:
                return {'auto_accept': False, 'reasons': ['NON_RAW_PREP_STATE'], 
                        'evidence': {'prep_state': str(prep_state), 'incompatible': True}}
            
            # Explicitly allow only RAW and FRESH
            if prep_state_upper not in raw_compatible:
                # NOT_SPECIFIED, UNKNOWN, SOAKED, GROUND, etc. are not auto-accepted
                return {'auto_accept': False, 'reasons': ['NON_RAW_PREP_STATE'], 
                        'evidence': {'prep_state': str(prep_state), 'incompatible': True, 'allowed': list(raw_compatible)}}"""

if old_section in content:
    content = content.replace(old_section, new_section)
    with open('C:\\Users\\Sachin\\OneDrive\\Documents\\ML_proj\\src\\matching\\candidate_generator.py', 'w') as f:
        f.write(content)
    print('Replaced successfully')
else:
    print('Old section not found')
    # Try to find it
    idx = content.find('incompatible = ')
    if idx >= 0:
        print('Found at index:', idx)
        print(content[idx:idx+600])