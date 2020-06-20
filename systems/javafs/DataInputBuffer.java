import java.io.*;

public class DataInputBuffer extends DataInputStream {
    private static class Buffer extends ByteArrayInputStream {
        public Buffer() {
            super(new byte[] {});
        }
        public void reset(byte[] input, int start, int length) {
            this.buf = input;
            this.count = start+length;
            this.mark = start;
            this.pos = start;
        }
        public int getPosition() {
            return pos;
        }
        public int getLength() {
            return count;
        }
    }
    private Buffer buffer;
    public DataInputBuffer() {
        this(new Buffer());
    }
    private DataInputBuffer(Buffer buffer) {
        super(buffer);
        this.buffer = buffer;
    }
    public void reset(byte[] input, int length) {
        buffer.reset(input, 0, length);
    }
    public int getPosition() {
        return buffer.getPosition();
    }
    public int getLength() {
        return buffer.getLength();
    }
}
