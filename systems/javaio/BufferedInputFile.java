import java.io.*;

public class BufferedInputFile {
    public static String read(String filename) throws IOException {
        BufferedReader br = new BufferedReader(new FileReader(filename));
        String s;
        StringBuffer fileContent = new StringBuffer();
        while((s = br.readLine()) != null) {
            fileContent.append(s+"\n");
        }
        br.close();
        return fileContent.toString();
    }
    public static void main(String[] args) throws IOException{
       System.out.print(read("BufferedInputFile.class"));
    }
}
