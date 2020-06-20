import java.io.*;
import java.util.*;

public class ObjectWritable implements Writable {
    private Class refClass;
    private Object instance;
    public ObjectWritable() {}
    public ObjectWritable(Object instance) {
        this.refClass = instance.getClass();
        this.instance = instance;
    }
    public ObjectWritable(Class refClass, Object instance) {
        this.refClass = refClass;
        this.instance = instance;
    }
    public Object get() {
        return instance; 
    }   
    public Class getRefClass() {
        return refClass;
    }
    public void set(Object instance) {
        this.refClass = instance.getClass();
        this.instance = instance;
    }
    private static final Map PRIMITIVE_NAMES = new HashMap();
    static {
        PRIMITIVE_NAMES.put("boolean", Boolean.TYPE);
        PRIMITIVE_NAMES.put("byte", Byte.TYPE);
        PRIMITIVE_NAMES.put("char", Character.TYPE);
        PRIMITIVE_NAMES.put("short", Short.TYPE);
        PRIMITIVE_NAMES.put("int", Integer.TYPE);
        PRIMITIVE_NAMES.put("long", Long.TYPE);
        PRIMITIVE_NAMES.put("float", Float.TYPE);
        PRIMITIVE_NAMES.put("double", Double.TYPE);
        PRIMITIVE_NAMES.put("void", Void.TYPE);
    }
    public Object readFields(DataInput in) throws IOException {
        String className = in.readUTF();
        Class refClass = (Class) PRIMITIVE_NAMES.get(className);
        if(refClass == null) {
            try{
                refClass = Class.forName(className);
            } catch (ClassNotFoundException e) {
                throw new RuntimeException(e.toString());
            }
        }
        Object instance;
        if(refClass.isPrimitive()) {
            if(refClass == Boolean.TYPE) {
                instance = Boolean.valueOf(in.readBoolean());
            } else if(refClass == Character.TYPE) {
                instance = new Character(in.readChar());
            } else if(refClass == Byte.TYPE) {
                instance = new Byte(in.readByte());
            } else if(refClass == Short.TYPE) {
                instance = new Short(in.readShort());
            } else if(refClass == Integer.TYPE) {
                instance = new Integer(in.readInt());
            } else if(refClass == Long.TYPE) {
                instance = new Long(in.readLong());
            } else if(refClass == Float.TYPE) {
                instance = new Float(in.readFloat());
            } else if(refClass == Double.TYPE) {
                instance = new Double(in.readDouble());
            } else if(refClass == Void.TYPE) {
                instance = null;
            } else {
                throw new IllegalArgumentException("Class not primitive!");
            }
        } else if(refClass.isArray()) {
          // some issues
          int length = in.readInt();  
          instance = Array.newInstance(refClass.getComponentType(), length);
          for(int i = 0; i < length; i++) {
              Array.set(instance, i, readFields(in));
          }
        } else if(refClass == String.class) {
           instance = in.readUTF();
        } else {
        
        }
        return instance;
    }
    public void write(DataOutput out) throws IOException {
        if(instance instanceof Writable) {
            out.writeUTF(instance.getClass().getName());
            ((Writable) instance).write(out);
        }

        out.writeUTF(refClass.getName());
        if(refClass.isPrimitive()) {
            if(refClass == Boolean.TYPE) {
                out.writeBoolean(((Boolean) instance).booleanValue());
            } else if(refClass == Character.TYPE) {
                out.writeChar(((Character) instance).charValue());
            } else if(refClass == Byte.TYPE) {
                out.writeByte(((Byte) instance).byteValue());
            } else if(refClass == Short.TYPE) {
                out.writeShort(((Short) instance).shortValue());
            } else if(refClass == Integer.TYPE) {
                out.writeInt(((Integer) instance).intValue());
            } else if(refClass == Long.TYPE) {
                out.writeLong(((Long) instance).longValue());
            } else if(refClass == Float.TYPE) {
                out.writeFloat(((Float) instance).floatValue());
            } else if(refClass == Double.TYPE) {
                out.writeDouble(((Double) instance).doubleValue());
            } else if(refClass == Void.TYPE) {
            } else {
                throw new IllegalArgumentException("Class not primitive!");
            }
        } else if(refClass.isArray()) {
            int length = Array.getLength(instance);
            out.writeInt(length);
            for(int i = 0; i < length; i++) {
                instance = Array.get(instance, i);
                refClass = refClass.getComponentType();
                write(out);
            }
        } else if(refClass == String.class) {
            out.writeUTF((String instance));
        } else {
        }
    }
}
