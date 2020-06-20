package multiThread;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.util.List;
import java.util.ArrayList;
import java.io.IOException;
public class ScheduleFile {
	private String Filename;
	private File sfile;
	private long baseTime=0l;
	public ScheduleFile(String Filename){
		this.Filename = Filename;
		this.sfile = new File(Filename);
	}
	public synchronized void init(){
		if(sfile.exists()){
			try{
			BufferedReader sbr = new BufferedReader(new FileReader(sfile));
			baseTime = 0l;
			String line = null;
			while((line = sbr.readLine()) != null){
				String server = line.split("\\s+")[3];
				System.out.println("pause "+server);
				baseTime = Long.valueOf(line.split("\\s+")[4]);
			}
			sbr.close();
			baseTime = System.currentTimeMillis(); // for test
			System.out.println("baseTime:"+baseTime);
			}catch(IOException e){
				e.printStackTrace();
			}
		}else System.out.println("FileNotFound...");
	}
	public synchronized void readFile(){
		long currenttime = System.currentTimeMillis();
		System.out.println("currentTime:"+currenttime);
		if(sfile.exists()){
			try{
				String[] pstring = {"/bin/sh","-c","ps -ef | grep java"};
				Process pros = Runtime.getRuntime().exec(pstring);
				pros.waitFor();
				BufferedReader ebr = new BufferedReader(new InputStreamReader(pros.getInputStream()));
				String prosline=null;
				System.out.println("############################################");
				while((prosline = ebr.readLine()) != null){
					System.out.println(prosline);
				}
				System.out.println("############################################");	
			BufferedReader sbr = new BufferedReader(new FileReader(sfile));
			String line = null;
			while((line = sbr.readLine()) != null){
				long startpoint = Long.valueOf(line.split("\\s+")[line.split("\\s+").length-1]) + baseTime;
				if(currenttime >= startpoint && (currenttime - startpoint) < 1000){
					System.out.println(currenttime - startpoint);
					System.out.println("Execute+"+line);
					}
			}
			sbr.close();
			}catch(IOException e){
				e.printStackTrace();
			}catch(InterruptedException e1){
				e1.printStackTrace();
			}
		}
		else System.out.println("FileNotFound...");
	}
	public synchronized void updateFile(){
		List<Long> starttime = new ArrayList<Long>();
		try{
		BufferedWriter sbw = new BufferedWriter(new FileWriter(sfile));
		sbw.write("pr  10G  09:42:23-2016-08-25  xen61  1472132543549  25325  0\n");
		sbw.write("lr  50G  09:42:32-2016-08-25  xen62  1472132552207  15411  17156\n");
		sbw.write("km  1G  09:42:57-2016-08-25  xen63  1472132577005  0  0\n");
        sbw.flush();
        sbw.close();
        System.out.println("Write done...");
		}catch(IOException e){
			e.printStackTrace();
		}
	}
	public static void createNewFile(String filename){ //for test only
		BufferedWriter bw = null;
		try{
			File f = new File(filename);
			bw = new BufferedWriter(new FileWriter(f));
			bw.write(System.currentTimeMillis()+"\n");
			bw.write("10 lr xen61\n");
			bw.write("0 pr xen62\n");
            bw.write("21 wc xen63\n");
            bw.write("3 km xen64\n");
            bw.flush();
		}catch(IOException e){
			e.printStackTrace();
		}finally{
			try{
			bw.close();
			}catch(IOException e1){
				e1.printStackTrace();
			}
		}
	}
	public static void main(String[] args){
		String filename = "testfile.txt";
		//createNewFile(filename);
		long begintime = System.currentTimeMillis();
		ScheduleFile sf = new ScheduleFile(filename);
		sf.readFile();
		System.out.println("Time:"+(System.currentTimeMillis()-begintime));
	}
}
