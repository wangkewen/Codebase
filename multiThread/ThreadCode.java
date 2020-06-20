public class ThreadCode{
private static int tcid=0;
class SimpleThread extends Thread{
private int countdown = 5;
//private static int threadid = ++tcid;
public SimpleThread(){
  super(Integer.toString(++tcid));
  start();
}
public String toString(){
  return "#"+getName()+"("+countdown+").";
}
public void run(){
  while(true){
     System.out.print(this);
     if(--countdown==0) return;
  }
}
}
class SelfManage implements Runnable{
private int countdown = 5;
private Thread t = new Thread(this);
public SelfManage(){
  t.start();
}
public String toString(){
  return Thread.currentThread().getName()
          + "("+countdown+").\n";
}
public void run(){
  while(true){
     System.out.print(this);
     if(--countdown==0) return;
  }
}
}
class InnerThread{
private int countdown = 5;
private Thread t;
public InnerThread(String name){
  t = new Thread(new Runnable () {
        public void run(){
          while(true){
            System.out.print(this);
            if(--countdown == 0) return;
          }
        }
        public String toString(){
          return Thread.currentThread().getName() + ":"+countdown+".\n";
        }
      }, name);
  t.start();
}
}
public static void test1(ThreadCode tc){
for(int i = 0;i<5;i++){
  tc.new SimpleThread();
}
}
public static void test2(ThreadCode tc){
for(int i=0;i<5;i++){
  tc.new SelfManage();
}
}
public static void test3(ThreadCode tc){
  tc.new InnerThread("Inner#"); 
}
public static void main(String[] args){
ThreadCode tc = new ThreadCode();
test3(tc);
}
}
