import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.Callable;
import java.util.concurrent.Future;
import java.util.concurrent.ExecutionException;
import java.util.List;
import java.util.ArrayList;
public class MainThread{
protected static int allcount=0;
protected static int taskcount=0;
class Lift implements Runnable{
protected int countdown = 10;
private final int id = taskcount++;
public Lift(){}
public Lift(int countdown){
this.countdown = countdown;
}
public String status(){
return "#"+id+"("
      +(countdown>0? countdown : "Lift")+")";
}
public void run(){
  while(countdown-->0){
      System.out.print(status()+". ");
      try{
      //Thread.sleep(100);
      TimeUnit.MILLISECONDS.sleep(0);
      }catch(InterruptedException e){
        e.printStackTrace();
      }
      //Thread.yield();
      //allcount++;
      //System.out.println("*-"+allcount+"-*");
  }
  System.out.println();
}
}
class TaskwithResult implements Callable<String> {
private int id;
public TaskwithResult(){}
public TaskwithResult(int id){
  this.id = id;
}
public String call(){
  return "Result id is "+id;
}
}
public static void test1(Lift li1){
li1.run();
}
public static void test2(Lift li2){
Thread t1 = new Thread(li2);
t1.start();
Thread.yield();
}
public static void test3(MainThread mt){
for(int i=0;i<5;i++){
   new Thread(mt.new Lift()).start();
}
}
public static void test4(MainThread mt){
//ExecutorService exec = Executors.newCachedThreadPool();
ExecutorService exec = Executors.newFixedThreadPool(5);
for(int i=0;i<5;i++){
   exec.execute(mt.new Lift());
}
exec.shutdown();
}
public static void test5(MainThread mt){
ExecutorService exec = Executors.newCachedThreadPool();
List<Future<String>> returns = new ArrayList<Future<String>>();
for(int i=0;i<10;i++){
   returns.add(exec.submit(mt.new TaskwithResult(i)));
}
for(Future<String> oner : returns){
  try{
    System.out.println(oner.get());
  }catch(InterruptedException e){
    e.printStackTrace();
  }catch(ExecutionException e){
    e.printStackTrace();
  }finally{
    exec.shutdown();
  }
}
}
public static void main(String[] args){
MainThread mt = new MainThread();
Lift li1 = mt.new Lift();
TaskwithResult tr = mt.new TaskwithResult();
test4(mt);
}
}
