import java.net.*;
import java.io.*;
public class Client{
public static void main(String[] args){
try{
  Socket s = new Socket("localhost",5500);
  BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
  PrintWriter pw = new PrintWriter(s.getOutputStream(),true);
  BufferedReader br = new BufferedReader(
                new InputStreamReader(s.getInputStream()));
  while(true){
    String le = in.readLine();
    pw.println(le);
    if(le==null || le.length()==0) break;
    System.out.println(br.readLine());
  }
  br.close();
  pw.close();
  in.close();
  s.close();
}catch(IOException e){
  e.printStackTrace();
}
}
}
