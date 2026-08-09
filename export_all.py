#@author
#@category DeReLLM

import json

output_path = getScriptArgs()[0]

program = currentProgram
listing = program.getListing()

# ---------------------------------------------------------
# FUNCTIONS + PSEUDOCODE + CALLERS
# ---------------------------------------------------------

functions_data = []

decompiler = ghidra.app.decompiler.DecompInterface()
decompiler.openProgram(program)

for func in listing.getFunctions(True):

    entry = str(func.getEntryPoint())

    # Decompiled pseudocode
    pseudocode = ""

    try:
        result = decompiler.decompileFunction(func, 30, monitor)

        if result.decompileCompleted():
            pseudocode = result.getDecompiledFunction().getC()
    except:
        pseudocode = ""

    # Direct callers
    callers = []

    try:
        refs = getReferencesTo(func.getEntryPoint())

        for ref in refs:
            caller_func = listing.getFunctionContaining(ref.getFromAddress())

            if caller_func is not None:
                name = caller_func.getName()

                if name not in callers:
                    callers.append(name)
    except:
        pass

    functions_data.append({
        "name": func.getName(),
        "entry": entry,
        "pseudocode": pseudocode,
        "callers": callers
    })

decompiler.dispose()

# ---------------------------------------------------------
# STRINGS
# ---------------------------------------------------------

strings = []

for data in listing.getDefinedData(True):
    try:
        value = data.getValue()

        if value is not None:
            text = str(value)

            if len(text) >= 3:
                strings.append({
                    "address": str(data.getAddress()),
                    "value": text
                })

    except:
        pass

# ---------------------------------------------------------
# PROGRAM METADATA
# ---------------------------------------------------------

output = {
    "binary": program.getName(),
    "executable_format": str(program.getExecutableFormat()),
    "language": str(program.getLanguageID()),
    "compiler": str(program.getCompiler()),
    "functions": functions_data,
    "strings": strings
}

with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print("Exported to", output_path)
