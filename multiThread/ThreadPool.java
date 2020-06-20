import java.util.concurrent.*;
public class ThreadPool{
    class Incrementer implements Runnable{
        protected int count = 5;
        private int taskCount = 0;
        private int id = taskCount++;
        Incrementer() {}
        Incrementer(int id) {
            this.id = id;
        }
        public String status(){
            return "# " + id + " (" + count + ")"; 
        }
        public void run(){
            while(count-- > 0){
                System.out.println(status());
                Thread.yield();
            }
        }
    }
    public static void main(String[] args){
        ExecutorService exec = Executors.newCachedThreadPool();
        ThreadPool tp = new ThreadPool();
        int n = 2;
        for(int i = 0; i < n; i++)
            exec.execute(tp.new Incrementer(i));
        exec.shutdown();
    }
}
