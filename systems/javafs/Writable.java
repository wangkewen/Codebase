import java.io.*;

public interface Writable {
    void write(DataOuput out) throws IOException;
    void readFields(DataInput in) throws IOException;
}
