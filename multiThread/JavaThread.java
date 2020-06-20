package multiThread;
import java.io.IOException;
public class JavaThread extends Thread{
	private static volatile double d = 1;
	public JavaThread(){
		setDaemon(true);
		start();
	}
	public void run(){
		while(true){
		d = d + 5;
		try{
		sleep(1000);
		}catch(InterruptedException e){
			e.printStackTrace();
		}
		}
	}
	public static void main(String[] args){
		JavaThread jt = new JavaThread();
		try{
		System.in.read();
		System.out.println(d);
		}catch(IOException e){
			e.printStackTrace();
		}
	}
}
