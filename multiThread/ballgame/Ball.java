import java.awt.geom.*;
import java.util.*;

public class Ball {
    private static final int XSIZE = 20;
    private static final int YSIZE = 20;
    private double x = 0;
    private double y = 0;
    private double dx = 1;
    private double dy = 1;
    private Random rnd;
    private float rColor;
    private float gColor;
    private float bColor;
   
    public Ball () {
        rnd = new Random();
        rColor = rnd.nextFloat();
        gColor = rnd.nextFloat();
        bColor = rnd.nextFloat();
    }
    
    public float[] getColor() {
        return new float[]{rColor, gColor, bColor};
    }
    public void move (Rectangle2D bounds) {
        double dir = rnd.nextDouble();
        if(dir > 0.999) {
           dx = -dx;
           dy = -dy; 
        }
        x += dx;
	y += dy;
        if(x < bounds.getMinX()){
            x = bounds.getMinX();
            dx = -dx;
        }
        if(x + XSIZE + dx > bounds.getMaxX()) {
            x = bounds.getMaxX() - XSIZE;
            dx = -dx;
        }
        if(y < bounds.getMinY()) {
            y = bounds.getMinY();
            dy = -dy;
        }
        if(y + YSIZE + dy > bounds.getMaxY()) {
            y = bounds.getMaxY() - YSIZE;
            dy = -dy;
        }
    }
    public Ellipse2D getShape() {
        return new Ellipse2D.Double(x, y, XSIZE, YSIZE);
    }
}
