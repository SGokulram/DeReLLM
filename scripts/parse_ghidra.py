import json

def parse_file(input_file, output_file):
    functions = []
    
    with open(input_file, 'r') as f:
        content = f.read().split("-----")
        
        for block in content:
            if "FUNCTION:" in block:
                lines = block.strip().split("\n")
                name = lines[0].replace("FUNCTION: ", "")
                code = "\n".join(lines[1:])
                
                functions.append({
                    "function": name,
                    "code": code
                })
    
    with open(output_file, 'w') as f:
        json.dump(functions, f, indent=2)

parse_file("runs/ghidra_output/head_all.c", "runs/ghidra_output/head_functions.json")
parse_file("runs/ghidra_output/cut_all.c", "runs/ghidra_output/cut_functions.json")
