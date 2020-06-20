import java.util.concurrent.locks.*;
public class EvenGenerator extends IntGenerator{
private int EvenValue = 0;
private Lock lock = new ReentrantLock();
//public synchronized int next(){
public int next(){
  lock.lock();
  try{
  ++EvenValue;
  //Thread.yield();
  ++EvenValue;
  return EvenValue;
  }finally{
    lock.unlock();
  }
}
public static void main(String[] args){
  EvenCheck.test(new EvenGenerator());
}
}
