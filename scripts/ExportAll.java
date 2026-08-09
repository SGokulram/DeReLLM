// ExportAll.java
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import java.io.*;

public class ExportAll extends GhidraScript {

    @Override
    protected void run() throws Exception {

        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);

        File outFile = new File(getScriptArgs()[0]);
        PrintWriter writer = new PrintWriter(new FileWriter(outFile));

        Listing listing = currentProgram.getListing();

        for (Function func : listing.getFunctions(true)) {
            DecompileResults res = decomp.decompileFunction(func, 30, monitor);
            if (res.decompileCompleted()) {
                writer.println("FUNCTION: " + func.getName());
                writer.println(res.getDecompiledFunction().getC());
                writer.println("-----");
            }
        }

        writer.close();
    }
}
