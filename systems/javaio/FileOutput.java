import java.io.*;
public class FileOutput {
    static String file = "FileOutput.out";
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new StringReader(BufferedInputFile.read("FileOutput.java")));
        PrintWriter pw = new PrintWriter(new BufferedWriter(new FileWriter(file)));
        int line = 1;
        String s;
        while((s = br.readLine()) != null) {
            pw.println(line++ + ": " + s);
        }
        pw.close();
        System.out.println(BufferedInputFile.read(file));
    }
}
