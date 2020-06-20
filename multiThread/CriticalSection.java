import java.util.*;
import java.util.concurrent.*;
class Pair{
    private int x;
    private int y;
    public Pair(int x, int y){
        this.x = x;
        this.y = y;
    }
    public Pair() { this(0, 0); }
    public int getX () { return this.x; }
    public int getY () { return this.y; }
    public void incrementX() {
        x++;
    }
    public void incrementY() {
        y++;
    }
    public String toString() {
        return "x: "+x + " y: "+y;
    }
    public void checkEqual() {
        if(x == y) System.out.println("x = y ");
        else throw new PairCompareException();
    }
    class PairCompareException extends RuntimeException {
        public PairCompareException() {
            super("Pair not equal  "  + Pair.this);
        }
    }
}
abstract class PairManager {
    protected Pair p = new Pair();
    private List<Pair> storage = Collections.synchronizedList(new ArrayList<Pair>());
    public synchronized Pair getPair() {
        return new Pair (p.getX(), p.getY());
    }
    protected void store(Pair p) {
        storage.add(p);
        try{ 
           TimeUnit.MILLISECONDS.sleep(50);
        }catch(InterruptedException e) {}
    }
    public abstract void increment();
}

class PairManagerA extends PairManager {
   public synchronized void increment() {
       p.incrementX();
       p.incrementY();
       store(getPair());
   }
}

class PairManagerB extends PairManager {
   public void increment() {
       synchronized(this){
           p.incrementX();
           p.incrementY();
           store(getPair());
       }
   }
}

class PairManagerManipulator implements Runnable {
   private PairManager pm;
   public PairManagerManipulator (PairManager pm){
       this.pm = pm;
   }
   public void run() {
       while(true) pm.increment();
   }
   public String toString() {
       return "Pair is " + pm.getPair();
   }
}

class PairChecker implements Runnable {
   private PairManager pm;
   public PairChecker (PairManager pm) {
       this.pm = pm;
   }
   public void run() {
       while(true) pm.getPair().checkEqual();
   }
}
public class CriticalSection {
   public static void test(PairManager pm1, PairManager pm2){
       ExecutorService exec = Executors.newCachedThreadPool();
       PairManagerManipulator pmm1 = new PairManagerManipulator(pm1),
                              pmm2 = new PairManagerManipulator(pm2);
       exec.execute(pmm1);
       exec.execute(pmm2);
       PairChecker pc1 = new PairChecker(pm1),
                   pc2 = new PairChecker(pm2);
       exec.execute(pc1);
       exec.execute(pc2);
       try{
           TimeUnit.MILLISECONDS.sleep(500);
       }catch(InterruptedException e){
           
       }
       System.out.println("pmm1 " + pmm1 + " pmmm2 " + pmm2);
       System.exit(0);
   }
   public static void main(String[] args) {
       PairManager pm1 = new PairManagerA(),
                   pm2 = new PairManagerB();
       test(pm1, pm2);
   }
}
