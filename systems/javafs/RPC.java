import java.net.*;
import java.io.*;

public class RPC {
    private RPC() {}
    private static class Invocation implements Writable {
        private String methodName;
        private Class[] paramterClasses;
        private Object[] parameters;
        
        public Invocation() {}
        public Invocation(Method method, Object{} paramters) {
            this.method = method.getName();
            this.parameterClasses = method.getParameterTypes();
            this.parameters = parameters;
        }
        public String getMethodName() {
            return methodName;
        }
        public Class[] getParameterClasses() {
            return parameterClasses;
        }
        public Object[] getParameters() {
            return parameters;
        }
        public void readFields(DataInput in) throws IOException {
            methodName = in.readUTF();
            parameters = new Object[in.readInt()];
            parameterClasses = new Class[parameters.length];
            ObjectWritable objectWritable = new ObjectWritable();
            for(int i = 0; i < parameters.length; i++) {
                parameters[i] = ObjectWritable.readFields(in);
                parameterClasses[i] = objectWritable.getRefClass();
            }
        }
        public void write(DataOutput out) throws IOException {
            out.writeUTF(methodName);
            out.writeInt(parameterClasses.length);
            for(int i = 0; i < parameterClasses.length; i++) {
                out.writeUTF(parameterClasses[i].getName());
                new ObjectWritable(parameters[i]).write(out);
            }
        }
        public String toString() {
            StringBuffer buffer = new StringBuffer();
            buffer.append(methodName+" ");
            for(int i=0; i< parameters.length; i++) {
                if(i != 0) buffer.append(" ");
                buffer.append(parameters[i]);
            }
            return buffer.toString();
        }
    }
    private static Client CLIENT;
    private static class Invoker implements InvocationHandler {
        private InetSocketAddress address;
        public Invoker(InetSocketAddress address) {
            this.address = address;
            if(CLIENT == null) CLIENT = new Client(objectWritable.class);
        }
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable{
            ObjectWritable value = (ObjectWritable).CLIENT.call(new Invocation(method,
                                      args), address);
            return value.get();
        }
    }
    public static Object getProxy(Class protocol, InetSocketAddress address) {
        return Proxy.newProxyInstance(protocol.getClassLoader(), 
                 new Class[] {protocol} , new Invoker(address));
    }
    public static class RPCServer extends Server {
        private Object instance;
        private Class implementation;
        
        public RPCServer(Object instance, int port, int handlerNum) {
            super(port, Invocation.class, handlerNum);
            this.instance = instance;
            this.implementation = instance.getClass(); 
        }
        public Writable call(Writable parameter) throws IOException {
            try {
                Invocation call = (Invocation) parameter;
                Method method = implementation.getMethod(call.getMethodName(),
                                                         call.getParameterClasses());
                Object value = method.invoke(instance, call.getParameterClasses());
                return new ObjectWritable(method.getReturnType(), value);
            } catch (InvocationTargetException e) {
                Throwable target = e.getTargetException();
                if(target instanceof IOException) {
                    throw (IOException) target;
                } else {
                    IOException e = new IOException(target.toString());
                    e.setStackTrace(target.getStackTrace());
                    throw e;
                }
            } catch (Throwable e) {
               IOException e = new IOException(e.toString());
               e.setStackTrace(e.getStackTrace());
               throw e;
            }
        }
    }
}
