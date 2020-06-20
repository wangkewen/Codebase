import java.net.*;
import java.io.*;
import java.util.*;

public class Client {
    private Hashtable connections = new Hashtable();
    private int count;
    private int timeout; // timeout for each call
    private boolean isClientRunning = true;
    private Class valueClass;

    private class Call {
        int id;
        Writable parameter;
        Writable value;
        String error;
        long lastTime;
        boolean isComplete;
        protected Call(Writable parameter) {
            this.parameter = parameter;
            synchronized (Client.this) {
                this.id = count++;
            }
            record();
       }
        public synchronized void complete() {
            notify();
        }
        public synchronized void record() {
            lastTime = System.currentTimeMillis();
        }
        public synchronized void setValue(Writable value, String error) {
            this.value = value;
            this.error = error;
            this.isComplete = true;
        }
    }
    private class Connection extends Thread {
        private InetSocketAddress address;
        private Socket socket;
        private DataInputStream in;
        private DataOutputStream out;
        private Hashtable calls = new Hashtable();
        private Call readCall;
        private Call writeCall;     
 
        public Connection(InetSocketAddress address) throws IOException {
            this.address = address;
            this.socket = new Socket(address.getAddress(), address.getPort());
            socket.setSoTimeout(timeout);
            // BufferedInputStream read() is synchronized
            // BufferedInputStream extends FilterInputStream
            // DataInputStream extends FilterInputStream
            this.in= new DataInputStream(new BufferedInputStream
                                        (new FilterInputStream(socket.getInputStream()) {
                      public int read(byte[] buf, int off, int len) throws IOException {
                          int value = super.read(buf, off, len);
                          if(readCall != null) {
                              readCall.record();
                          }
                      }
                  }));

            this.out = new DataOutputStream(new BufferedOutputStream
                                        (new FilterOutputStream(socket.getOutputStream()) {
                      public void write(byte[] buf, int off, int len) throws IOException {
                          out.write(buf, off, len);
                          if(writeCall != null) {
                              writeCall.record();
                          }
                      }));
            this.setDaemon(true);
            
        }
        
        public void run() {
            try {
                while(isClientRunning) { 
                    int id;
                    try { 
                        id = in.readInt();
                    } catch (SocketTimeoutException e) {
                        continue;
                    }
                    Call call = (Call) calls.remove(new Integer(id));
                    boolean isError = in.readBoolean();
                    if(isError) {
                        call.setValue(null, in.readUTF());
                    } else {
                        Writable value;
                        try {
                            value = (Writable) valueClass.newInstance();
                        } catch (InstantiationException e) {
                            throw new RuntimeException(e.toString());
                        } catch (IllegalAccessException e) {
                            throw new RuntimeException(e.toString());
                        }
                        try {
                            readCall = call;
                            value.readFields(in);
                        } finally {
                            readCall = null;
                        }
                        call.complete();
                    }
                }
            } catch (EOFException e) {
                throw new RuntimeException(e.toString());
            } catch (Exception e) {
                throw new Exception(e.toString());
            } finally {
                close();
            }
        }
          
        public void close() {
            synchronized (connections) {
                connections.remove(address);
            }
            try {
                socket.close();
            } catch (IOException e) {
            }
        }
    
        public void sendParameter(Call call) throws IOException {
            boolean isError = true;
            try {
                calls.put(new Integer(call.id), call);
                synchronized (out) {
                    try {
                        writeCall = call;
                        out.writeInt(call.id);
                        call.parameter.write(out);
                        out.flush();
                    } finally {
                        writeCall = null;
                    }
                }
                isError = false; 
            } finally {
                if(isError) 
                    close();
            }
        }
    }        

    public Client(Class valueClass) {
	this.valueClass = valueClass;
	this.timeout = 10000;
    }
    
    public void stop() {
        try {
            Thread.sleep(timeout);
        } catch (InterruptedException e) {
        running = false;
    }
    public void setTimeout (int timeout) {
        this.timeout = timeout;
    }

    public Writable call(Writable parameter, InetSocketAddress address) throws IOException {
        Connection connection = null;
        synchronized (connections) {
            connection = (Connection) connections.get(address);
            if(connection == null) {
                connection = new Connection(address);
                connections.put(address, connection);
                connection.start();
            }
        }
        Call call = new Call(parameter);
        synchronized (call) {
            connection.sendParameter(call);
            long waitTime = timeout;
            do {
                try {
                    call.wait(waitTime);
                } catch (InterruptedException e) {}
                waitTime = timeout - (System.currentTimeMillis() - call.lastTime);
            } while ( !call.isComplete && waitTime > 0);
            if(call.error != null) {
                throw new RemoteException(call.error);
            } else if(!call.isComplete) {
                throw new IOException("time out");
            } else {
                return call.value;
            }
        }
    }
}
