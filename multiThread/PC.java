import java.io.*;
import java.util.*;
public class PC{
    class Bread{
	private int number;
	private int N;
	public Bread(){
	    number=0;
	    N=10;
	}
	public synchronized void get(){
	    while(number<=0){
	      try{
		wait();
	      }catch(InterruptedException e){
		e.printStackTrace();
	      }
	    }
	    System.out.println(Thread.currentThread().getId()+" get "+number);
	    number--;
	    notifyAll();
	}
	public synchronized void put(){
	    while(number>=N){
	      try{
		wait();
	      }catch(InterruptedException e){
		e.printStackTrace();
	      }
	    }
	    number++;
	    System.out.println(Thread.currentThread().getId()+"  put "+number);
	    notifyAll();
	}
    }
    class Producer extends Thread{
	private String name;
	private Bread b;
	public Producer(String name,Bread b){
	   this.name=name;
	   this.b=b;
	}
	public synchronized void run(){
	    for(int i=0;i<3;i++){
	      b.put();
	      try{
		 sleep(10);
	      }catch(InterruptedException e){
		 e.printStackTrace();
	      }
	    }
	}
    }
    class Consumer extends Thread{
	private String name;
	private Bread b;
	public Consumer(String name,Bread b){
	   this.name=name;
	   this.b=b;
	}
	public synchronized void run(){
	    for(int i=0;i<3;i++){
	      b.get();
	      try{
		sleep(10);
	      }catch(InterruptedException e){
		e.printStackTrace();
	      }
	    }
	}
    }
    public void test(){
	Bread b = new Bread();
	Producer p1 = new Producer("pa",b);
	Producer p2 = new Producer("pb",b);
	Producer p3 = new Producer("pc",b);
	Consumer c1 = new Consumer("Ca",b);
	Consumer c2 = new Consumer("Cb",b);
	Consumer c3 = new Consumer("Cc",b);
	c1.start();c2.start();c3.start();
	p1.start();p2.start();p3.start();
    }
    public static void main(String[] args){
	PC a = new PC();
	a.test();
    }
}
