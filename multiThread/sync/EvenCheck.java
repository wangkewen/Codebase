import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
public class EvenCheck implements Runnable{
private final int id;
private IntGenerator generator;
public EvenCheck(IntGenerator generator, int id){
  this.generator = generator;
  this.id = id;
}
public void run(){
  while(!generator.isCanceled()){
    int value = generator.next();
    if(value %2 !=0){
       System.out.println("Check " + id +" Value is "+value);
       generator.cancel();
    }else{
       System.out.println("##### " + id +" Value is "+value);
    }
  }
}
public static void test(IntGenerator generator, int count){
  ExecutorService exec = Executors.newCachedThreadPool();
  for(int i=0;i<count;i++){
     exec.execute(new EvenCheck(generator, i));
  }
  exec.shutdown();
}
public static void test(IntGenerator generator){
  test(generator, 10);
}
}
