public abstract class IntGenerator{
private volatile boolean isCancel = false;
public abstract int next();
public void cancel(){ isCancel = true;}
public boolean isCanceled(){return isCancel;}
}
