#@author
#@category DeReLLM

import json

output_path = getScriptArgs()[0]

program = currentProgram
listing = program.getListing()

functions_data = []

for func in listing.getFunctions(True):
    functions_data.append({
        "name": func.getName(),
        "entry": str(func.getEntryPoint())
    })

# extract strings
strings = []
for data in listing.getDefinedData(True):
    try:
        if data.getDataType().getName() == "string":
            strings.append(str(data))
    except:
        continue

output = {
    "functions": functions_data,
    "strings": strings
}

with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print("Exported to", output_path)
