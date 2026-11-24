with open('C:\\Users\\Sachin\\OneDrive\\Documents\\ML_proj\\src\\matching\\candidate_generator.py', 'r') as f:
    lines = f.readlines()

# Find the lines to replace
# We need to replace from "incompatible = {" to the return statement
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    if 'incompatible = ' in line and 'GROUNDED' in line:
        # Found the start - replace from here
        # Skip until after the return statement
        new_lines.append("            incompatible = {'DRIED', 'POWDERED', 'GROUND', 'ROASTED', 'FRIED', 'BOILED', \n")
        new_lines.append("                           'COOKED', 'FERMENTED', 'PICKLED', 'SPROUTED', 'BLANCHED', 'MARINATED', 'SOAKED', 'GROUND'}\n")
        new_lines.append("\n")
        new_lines.append("            prep_state_upper = str(prep_state).upper()\n")
        new_lines.append("            if prep_state_upper in incompatible:\n")
        new_lines.append("                return {'auto_accept': False, 'reasons': ['NON_RAW_PREP_STATE'], \n")
        new_lines.append("                        'evidence': {'prep_state': str(prep_state), 'incompatible': True}}\n")
        new_lines.append("\n")
        new_lines.append("            # Explicitly allow only RAW and FRESH\n")
        new_lines.append("            if prep_state_upper not in raw_compatible:\n")
        new_lines.append("                # NOT_SPECIFIED, UNKNOWN, SOAKED, GROUND, etc. are not auto-accepted\n")
        new_lines.append("                return {'auto_accept': False, 'reasons': ['NON_RAW_PREP_STATE'], \n")
        new_lines.append("                        'evidence': {'prep_state': str(prep_state), 'incompatible': True, 'allowed': list(raw_compatible)}}\n")
        # Skip the old lines until after the return statement
        while i < len(lines) and 'return' not in lines[i]:
            i += 1
        # Skip the return line and the closing brace
        while i < len(lines) and ('return' in lines[i] or '}' in lines[i] or lines[i].strip() == ''):
            i += 1
        continue
    new_lines.append(line)
    i += 1

with open('C:\\Users\\Sachin\\OneDrive\\Documents\\ML_proj\\src\\matching\\candidate_generator.py', 'w') as f:
    f.writelines(new_lines)

print('Fixed')