package multiThread;

import java.util.concurrent.TimeUnit;

public class OperateSchedule implements Runnable{
	private int optype;
	private ScheduleFile sf;
	public OperateSchedule(int optype,ScheduleFile sf){
		this.optype = optype;
		this.sf = sf;
	}
	public void run(){
		if(!Thread.interrupted()){
			switch(optype){
			case 0:  sf.init();
			         break;
			case 1:  sf.readFile(); 
			         break;
			case 2:  sf.updateFile(); 
			         break;
			default: System.out.println("No operation..."); 
			         break;
			}	
		}
	}
	public static void main(String[] args){
		String filename = "scfile";
		//ScheduleFile.createNewFile(filename);
		ScheduleFile sf = new ScheduleFile(filename);
		int i=0;
		try{
		Thread ta = new Thread(new OperateSchedule(0,sf));
		ta.start();
		ta.join();
		while(i<50){
			Thread ti = new Thread(new OperateSchedule(1,sf));
			ti.start();
			TimeUnit.MILLISECONDS.sleep(1000);
			ti.join();
			System.out.println("id"+i);
			i++;
			if(i==30) {
				ta = new Thread(new OperateSchedule(0,sf));
				ta.start();
				ta.join();
			ti = new Thread(new OperateSchedule(2,sf));
			ti.start();
			ti.join();
			}
		}}catch(InterruptedException e){
			System.err.println("Interrupted...");
		}
	}
}
