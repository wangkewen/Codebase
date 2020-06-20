import java.io.*;
import java.util.*;

public class TextFile extends ArrayList<String> {
    public static String read(String fileName) {
        StringBuilder out = new StringBuilder();
        try{ 
            BufferedReader br = new BufferedReader(new FileReader(new File(fileName)));
            try{
                String s;
                while((s = br.readLine()) != null) {
                    out.append(s+"\n"); 
                }
            } finally {
                br.close();
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        return out.toString();
    }
    public static void write(String fileName, String text) {
        try{
            PrintWriter out = new PrintWriter(new File(fileName));
            try{
                out.print(text);
            } finally {
                out.close();
            }
        } catch(IOException e) {
            throw new RuntimeException(e);
        }
    }
    public TextFile(String fileName, String splitter) {
        super(Arrays.asList(read(fileName).split(splitter)));
        if(get(0).equals("")) remove(0);
    }
    public TextFile(String fileName) {
        this(fileName, "\n");
    }
    public void write(String fileName) {
        try {
            PrintWriter out = new PrintWriter(new File(fileName));
            try {
                for(String item : this) out.println(item);
            } finally {
                out.close();
            }
        } catch(IOException e) {
            throw new RuntimeException(e);
        }
    }
    public static void main(String[] args) {
        String file = read("TextFile.java");
        write("test.out", file);
        TextFile text = new TextFile("test.out");
        text.write("testCopy.out");
        TreeSet<String> words = new TreeSet<String>(new TextFile("TextFile.java", "\\W+"));
        System.out.println(words.headSet("a"));
    }
} 
