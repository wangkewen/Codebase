import java.io.*;
import java.net.*;
import java.util.*;

public abstract class Server {
    private static final ThreadLocal SERVER = new ThreadLocal();
    public static Server get() {
        return (Server) SERVER.get();
    }
    private int port;
    private int handlerNum;
    private int maxQueuedCalls;
    private Class parameterClass;
    private int timeout;
    private boolean isServerRunning = true;
    private LinkedList callQueue = new LinkedList();
    private Object callDequeued = new Object();    

    protected Server(int port, Class parameterClass, int handlerNum) {
        this.port = port;
        this.parameterClass = parameterClass;
        this.handlerNum = handlerNum;
        this.maxQueuedCalls = handlerNum;
        this.timeout = 10000;
    }

    private static class Call {
        private int id;
        private Writable parameter;
        private Connection connection;
        public Call(int id, Writable parameter, Connection connection) {
            this.id = id;
            this.parameter = parameter;
            this.connection = connection;
        }
    }
    
    private class Connection extends Thread {
        private Socket socket;
        private DataInputStream in;
        private DataOutputStream out;
        public Connection(Socket socket) throws IOException {
            this.socket = socket;
            socket.setSoTimeout(timeout);
            this.in = new DataInputStream(new BufferedInputStream
                                         (socket.getInputStream()));
            this.out = new DataOutputStream(new BufferedOutputStream
                                         (socket.getOutputStream()));
            this.setDaemon(true);
        }
        
        public void run() {
            SERVER.set(Server.this);
            try {
                while(isServerRunning) {
                    int id;
                    try {
                        id = in.readInt();
                    } catch (SocketTimeoutException e) {
                        continue;
                    }
		    Writable parameter;
		    try {
			parameter = (Writable) parameterClass.newInstance();
		    } catch (InstantiationException e) {
			throw new RuntimeException(e.toString());
		    } catch (IllegalAccessException e) {
			throw new RuntimeException(e.toString());
		    } 
                    parameter.readFields(in);
                    Call call = new Call(id, parameter, this);
                    synchronized (callQueue) {
                        callQueue.addLast(call);
                        callQueue.notify();
                    }
                    while(isServerRunning && callQueue.size() >= maxQueuedCalls) {
                        synchronized (callDequeued) {
                            callDequeued.wait(timeout);
                        }
                    }
                }
            } catch (EOFException eof) {
            } catch (SocketException eof) {
            } catch (Exception e) {
            } finally {
                try {
                    socket.close();
                } catch (IOException e) {}
            }
        }
    }

    private class Listener extends Thread {
        private ServerSocket socket;
        public Listener() throws IOException {
            this.socket = new ServerSocket(port);
            socket.setSoTimeout(timeout);
            this.setDaemon(true);
        }
        public void run() {
            while(isServerRunning) {
                try {
                    new Connection(socket.accept()).start();
                } catch (SocketTimeoutException e) {
                    e.printStackTrace();
                } catch (Exception e) {
                }
            }
            try {
                socket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    private class Handler extends Thread {
        public Handler(int instanceNumber) {
            this.setDaemon(true);
        }
        public void run() {
            SERVER.set(Server.this);
            while (isServerRunning) {
                try {
                   Call call;
                   synchronized (callQueue) {
                       while(isServerRunning && callQueue.size() == 0) {
                           callQueue.wait(timeout); 
                       }
                       if(!isServerRunning) break;
                       call = (Call) callQueue.removeFirst();
                   }
                   synchronized (callDequeued) {
                       callDeueued.notify();
                   }
                   String error = null;
                   Writable value = null;
                   try {
                       value = call(call.parameter);
                   } catch (IOException e) {
                       error = e.toString();
                   } catch (Exception e) {
                       error = e.toString();
                   }
                   DataOutputStream out = call.connection.out;
                   synchronized (out) {
                       out.writeInt(call.id);
                       out.writeBoolean(error!=null);
                       if(error != null) {
                           out.writeUTF(error); 
                       } 
                   }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }
    }
    public void setTimeout(int timeout) {
        this.timeout = timeout;
    }
    public synchronized void start() throws IOException {
        Listener listener = new Listener();
        listener.start();
        for(int i = 0; i < handlerNum; i++) {
            Handler handler = new Handler(i);
            handler.start();
        }
    }
    public synchronized void stop() {
        isServerRunning = false;
        try {
            Thread.sleep(timeout);
        } catch (InterruptedException e) {}
        notifyAll();
    }
    public synchronized void join() throws InterruptedException {
        while(isServerRunning) {
            wait();
        }
    }
    public abstract Writable call(Writable parameter) throws IOException;
}
