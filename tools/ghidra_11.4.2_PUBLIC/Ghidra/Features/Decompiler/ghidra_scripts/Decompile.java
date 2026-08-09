// Decompile.java
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;

import java.io.FileWriter;

public class Decompile extends GhidraScript {

    public void run() throws Exception {

        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);

        FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);

        FileWriter writer = new FileWriter("runs/ghidra_output/" + currentProgram.getName() + "_functions.json");
        writer.write("[\n");

        boolean first = true;

        while (functions.hasNext()) {
            Function func = functions.next();

            DecompileResults res = decomp.decompileFunction(func, 30, monitor);
            String code = res.getDecompiledFunction().getC();

            if (!first) writer.write(",\n");
            first = false;

            writer.write("{\"function\":\"" + func.getName() + "\",");
            writer.write("\"code\":\"" + code.replace("\"","\\\"").replace("\n","\\n") + "\"}");
        }

        writer.write("\n]");
        writer.close();
    }
}
