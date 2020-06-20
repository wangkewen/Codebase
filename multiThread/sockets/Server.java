import java.net.*;
import java.io.*;
public class Server implements Runnable{
private Socket client;
private BufferedReader br;
private PrintWriter pw;
public Server(Socket s){
  client=s;
  try{
    br=new BufferedReader(new InputStreamReader(client.getInputStream()));
    pw=new PrintWriter(client.getOutputStream(), true);
  }catch(IOException e){
    e.printStackTrace();
  }
}
public void run(){
  try{
    while(true){
      String le = br.readLine();
      if(le==null || le.length()==0) break;
      char[] line = le.toCharArray();
      for(int i=0;i<line.length;i++){
        if(line[i]>='A' && line[i]<='Z')
          pw.print((1+line[i]-'A')+" ");
        else if(line[i]>='a' && line[i]<='z')
          pw.print((1+line[i]-'a')+" ");
        else pw.print(line[i]+" ");
      }
      pw.println();
    }
    pw.close();
    br.close();
    client.close();
  }catch(IOException e){
    e.printStackTrace();
  } 
}
public static void main(String[] args){
try{
   ServerSocket ss = new ServerSocket(5500);
   Socket s = null;
   while(true){
     s = ss.accept();
     Thread t = new Thread(new Server(s));
     t.start();
   }
}catch(IOException e){
   e.printStackTrace();
}
}
}
