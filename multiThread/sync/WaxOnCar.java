import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
class Car{
private boolean waxOn = false;
public synchronized void waxed(){
  waxOn = true;
  notifyAll();
}
public synchronized void buffed(){
  waxOn = false;
  notifyAll();
}
public synchronized void waitForWax() throws InterruptedException{
  while(waxOn == false){
    wait();
  }
}
public synchronized void waitForBuff() throws InterruptedException{
  while(waxOn == true){
    wait();
  }
}
}
class WaxOn implements Runnable{
  private Car car;
  public WaxOn(Car c){car = c;}
  public void run(){
    try{
      while(!Thread.interrupted()){
        System.out.println("#Wax on..");
        TimeUnit.MILLISECONDS.sleep(10);
        car.waxed();
        car.waitForBuff();
      }
      }catch(InterruptedException e){
        e.printStackTrace();
      }
      System.out.println("End of Wax");
  }
}
class WaxOff implements Runnable{
  private Car car;
  public WaxOff(Car c){car = c;}
  public void run(){
    try{
      while(!Thread.interrupted()){
        car.waitForWax();
        System.out.println("#Buff Off..");
        TimeUnit.MILLISECONDS.sleep(10);
        car.buffed();
      }
      }catch(InterruptedException e){
        e.printStackTrace();
      }
      System.out.println("End of Buff");
  }
}
public class WaxOnCar{
public static void main(String[] args) throws Exception{
  Car car = new Car();
  ExecutorService exec = Executors.newCachedThreadPool();
  exec.execute(new WaxOn(car));
  exec.execute(new WaxOff(car));
  TimeUnit.MILLISECONDS.sleep(10);
  exec.shutdown();
}
}
